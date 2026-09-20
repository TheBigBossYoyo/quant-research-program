"""Tests for the Phase 8B human-labelling UI data layer and HTTP API, run on TEMPORARY COPIES of the real package.
The real labelled outputs are never touched."""
import csv
import json
import shutil
import sys
import tempfile
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'phase8b' / 'labeler'))
import labeler_app as la  # noqa: E402

PKG = ROOT / 'research' / 'phase8b'


def make_workspace(tmp, n_texts=None):
    """Copy the real CSVs, the guide and the referenced texts (all of them, or the first n) into a temp workspace."""
    ws = Path(tmp) / 'ws'; (ws / 'labeling_texts').mkdir(parents=True)
    for name in ('phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv', 'phase8b_labeling_guide.md'):
        shutil.copy2(PKG / name, ws / name)
    for name in ('phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv'):
        with open(PKG / name, encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.DictReader(fh))
        for r in rows if n_texts is None else rows[:n_texts]:
            src = PKG / r['full_text_path']
            if src.exists():
                shutil.copy2(src, ws / r['full_text_path'])
    return ws


class RealPackageChecks(unittest.TestCase):
    """Read-only checks on the real package (no write)."""

    def test_sources_have_no_labels_and_all_texts_resolve(self):
        for name in ('phase8b_labeling_candidates.csv', 'phase8b_retrieval_audit_candidates.csv'):
            with open(PKG / name, encoding='utf-8-sig', newline='') as fh:
                rows = list(csv.DictReader(fh))
            self.assertTrue(all(r['human_label'] == '' for r in rows), f'{name} must ship unlabelled')
            self.assertTrue(all((PKG / r['full_text_path']).exists() for r in rows), f'{name}: a full_text_path does not resolve')
            self.assertFalse(any(k for k in rows[0] if 'ticker' in k.lower() or 'return' in k.lower() or 'price' in k.lower()))


class DataLayerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.ws = make_workspace(self.tmp.name, n_texts=3)
        self.app = la.App(self.ws)

    def tearDown(self):
        self.tmp.cleanup()

    def read(self, key):
        with open(self.app.ds[key].labeled, encoding='utf-8-sig', newline='') as fh:
            return list(csv.DictReader(fh))

    def test_initial_state_has_no_labels_and_labeled_copy_is_created(self):
        st = self.app.state()
        self.assertEqual((st['datasets']['main']['total'], st['datasets']['audit']['total']), (240, 90))
        self.assertEqual(st['done'], 0); self.assertEqual(st['datasets']['main']['first_unlabeled'], 0)
        self.assertTrue(self.app.ds['main'].labeled.exists()); self.assertFalse(self.app.ds['main'].resumed)
        self.assertTrue(all(r['human_label'] == '' for r in self.read('main')))

    def test_label_click_saves_to_disk_and_advances(self):
        res = self.app.label('main', 0, 'd', 'AMBIG')
        rows = self.read('main')
        self.assertEqual(rows[0]['human_label'], 'D'); self.assertEqual(rows[0]['human_notes'], 'AMBIG')
        self.assertEqual(res['next_unlabeled'], 1); self.assertEqual(res['progress']['done'], 1)
        # source untouched
        with open(self.ws / 'phase8b_labeling_candidates.csv', encoding='utf-8-sig', newline='') as fh:
            self.assertEqual(list(csv.DictReader(fh))[0]['human_label'], '')

    def test_invalid_label_rejected(self):
        with self.assertRaises(ValueError):
            self.app.label('main', 0, 'K', '')
        self.assertEqual(self.read('main')[0]['human_label'], '')

    def test_resume_from_labeled_file_keeps_labels_and_notes(self):
        self.app.label('main', 0, 'A', 'note one'); self.app.label('main', 5, 'I', ''); self.app.label('audit', 2, 'J', 'x')
        app2 = la.App(self.ws)
        st = app2.state()
        self.assertTrue(app2.ds['main'].resumed)
        self.assertEqual(st['datasets']['main']['done'], 2); self.assertEqual(st['datasets']['audit']['done'], 1)
        self.assertEqual(st['datasets']['main']['first_unlabeled'], 1)
        r = app2.row('main', 0); self.assertEqual((r['current_label'], r['note'], r['labeled']), ('A', 'note one', True))
        self.assertEqual(app2.row('main', 1)['labeled'], False)

    def test_change_existing_label_and_undo_restores_disk(self):
        self.app.label('main', 3, 'B', 'first')
        self.app.label('main', 3, 'C', 'second')
        self.assertEqual(self.read('main')[3]['human_label'], 'C')
        res = self.app.undo()
        self.assertTrue(res['undone']); self.assertEqual(res['restored_label'], 'B')
        rows = self.read('main'); self.assertEqual((rows[3]['human_label'], rows[3]['human_notes']), ('B', 'first'))
        res = self.app.undo(); self.assertEqual(res['restored_label'], '')
        self.assertEqual(self.read('main')[3]['human_label'], '')
        self.assertFalse(self.app.undo()['undone'])

    def test_note_only_save(self):
        self.app.note('audit', 1, 'NOMENTION')
        self.assertEqual(self.read('audit')[1]['human_notes'], 'NOMENTION'); self.assertEqual(self.read('audit')[1]['human_label'], '')

    def test_navigation_helpers(self):
        d = self.app.ds['main']
        for i in range(0, 240):
            if i != 7:
                d.set_label(i, 'H')
        self.assertEqual(d.next_unlabeled(100), 7); self.assertEqual(d.next_unlabeled(7), None); self.assertEqual(d.prev_unlabeled(3), 7)
        self.assertEqual(d.next_unlabeled(-1), 7); self.assertEqual(d.next_unlabeled(6), 7)
        self.assertEqual(d.find(d.rows[7]['event_id']), 7); self.assertEqual(d.find(d.rows[7]['accession']), 7); self.assertIsNone(d.find('nope'))

    def test_full_text_resolution_and_missing_error(self):
        text, path = self.app.ds['main'].full_text(0, self.ws)
        self.assertIsNotNone(text); self.assertIn('ACCESSION', text)
        text, path = self.app.ds['main'].full_text(200, self.ws)   # not copied into the temp workspace
        self.assertIsNone(text); self.assertTrue(path.endswith('.txt')); self.assertIn('labeling_texts', path)

    def test_labeled_file_structure_mismatch_is_refused(self):
        with open(self.app.ds['audit'].labeled, encoding='utf-8-sig', newline='') as fh:
            rows = list(csv.DictReader(fh)); fields = rows and list(rows[0].keys())
        la.write_csv_atomic(self.app.ds['audit'].labeled, fields, rows[:-1])
        with self.assertRaises(ValueError):
            la.App(self.ws)

    def test_completion_integrity_report(self):
        for k in ('main', 'audit'):
            d = self.app.ds[k]
            for i in range(len(d.rows)):
                d.set_label(i, 'I')
        path, reps = self.app.write_report()
        self.assertTrue(path.exists())
        txt = path.read_text(encoding='utf-8')
        for k in ('main', 'audit'):
            r = reps[k]
            self.assertTrue(r['complete']); self.assertTrue(r['event_ids_unchanged']); self.assertTrue(r['non_label_columns_unchanged']); self.assertFalse(r['duplicate_event_ids'])
            self.assertEqual(r['output_rows'], r['source_rows']); self.assertEqual(r['blank_label_rows'], 0)
        for letter in la.VALID:                       # no per-class counts anywhere in the report
            self.assertNotIn(f'label_{letter}', txt); self.assertNotIn(f' {letter}:', txt)
        self.assertNotIn('return', txt.lower()); self.assertNotIn('price', txt.lower())
        self.assertIn('sha256_output', txt)
        # completed CSV preserves every source column and row order
        with open(self.ws / 'phase8b_labeling_candidates.csv', encoding='utf-8-sig', newline='') as fh:
            src = list(csv.DictReader(fh))
        out = self.read('main')
        self.assertEqual([r['event_id'] for r in out], [r['event_id'] for r in src])
        self.assertEqual(list(out[0].keys()), list(src[0].keys()))
        self.assertTrue(all(o[c] == s[c] for o, s in zip(out, src) for c in src[0] if c not in ('human_label', 'human_notes')))

    def test_backups_created_at_start_and_periodically(self):
        b = self.ws / 'backups'
        self.assertEqual(len(list(b.glob('*_session.csv'))), 2)
        for i in range(la.BACKUP_EVERY):
            self.app.ds['main'].set_label(i, 'E')
        self.assertEqual(len(list(b.glob('phase8b_labeling_candidates_LABELED_*_periodic.csv'))), 1)


class HttpApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory(); cls.ws = make_workspace(cls.tmp.name, n_texts=2)
        la.Handler.app = la.App(cls.ws)
        cls.httpd = ThreadingHTTPServer(('127.0.0.1', 0), la.Handler); cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown(); cls.httpd.server_close(); cls.tmp.cleanup()

    def call(self, path, body=None):
        url = f'http://127.0.0.1:{self.port}{path}'
        req = urllib.request.Request(url, data=json.dumps(body).encode() if body is not None else None, headers={'Content-Type': 'application/json'} if body is not None else {})
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    def test_page_and_api_flow(self):
        with urllib.request.urlopen(f'http://127.0.0.1:{self.port}/') as r:
            html = r.read().decode('utf-8')
        self.assertIn('PHASE 8B HUMAN LABELING', html)
        for bad in ('prediction', 'recommend', 'stock price', 'abnormal return', 'suggested label', 'likely label', 'classifier'):
            self.assertNotIn(bad, html.lower())
        code, st = self.call('/api/state'); self.assertEqual(code, 200); self.assertEqual(st['done'], 0)
        code, row = self.call('/api/row?ds=main&i=0'); self.assertEqual(code, 200); self.assertEqual(row['current_label'], '')
        code, res = self.call('/api/label', dict(ds='main', i=0, label='g', note='')); self.assertEqual(code, 200); self.assertEqual(res['next_unlabeled'], 1)
        code, row = self.call('/api/row?ds=main&i=0'); self.assertEqual(row['current_label'], 'G'); self.assertTrue(row['labeled'])
        code, res = self.call('/api/label', dict(ds='main', i=0, label='K', note='')); self.assertEqual(code, 500); self.assertIn('label must be', res['error'])
        code, ft = self.call('/api/fulltext?ds=main&i=0'); self.assertEqual(code, 200); self.assertIn('ACCESSION', ft['text'])
        code, ft = self.call('/api/fulltext?ds=main&i=100'); self.assertEqual(code, 404); self.assertIn('missing', ft['error']); self.assertIn('.txt', ft['path'])
        code, res = self.call('/api/undo', {}); self.assertTrue(res['undone']); self.assertEqual(res['restored_label'], '')
        code, g = self.call('/api/guide'); self.assertIn('human_label', g['guide'])
        code, f = self.call('/api/find?ds=audit&q=' + la.Handler.app.ds['audit'].rows[4]['event_id']); self.assertEqual(f['index'], 4)


if __name__ == '__main__':
    unittest.main()
