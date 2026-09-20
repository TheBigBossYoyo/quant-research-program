"""Phase 8B human-labelling UI: a neutral local web interface for typing A-J labels into the frozen labelling CSVs.

Standard library only (no dependencies). Disk is authoritative: every label click is written atomically to
<name>_LABELED.csv before the UI advances; the source CSVs are never modified. Restarting resumes from the labelled
file. The app shows nothing beyond the CSV columns and the referenced full text; it never preselects, ranks, suggests
or counts labels by class. Run: python labeler_app.py   (or the START_PHASE8B_LABELER.bat launcher).
Environment: PHASE8B_LABELER_WORKSPACE (folder holding the CSVs; default = parent of this file),
PHASE8B_LABELER_PORT (default 8765), PHASE8B_LABELER_NO_BROWSER=1 to skip opening a browser.
"""
from datetime import datetime
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs
import csv
import hashlib
import json
import os
import shutil
import sys
import threading
import webbrowser

HERE = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get('PHASE8B_LABELER_WORKSPACE', HERE.parent)).resolve()
PORT = int(os.environ.get('PHASE8B_LABELER_PORT', '8765'))
VALID = list('ABCDEFGHIJ')
DATASETS = {'main': ('phase8b_labeling_candidates.csv', 'Main sample'), 'audit': ('phase8b_retrieval_audit_candidates.csv', 'Retrieval audit')}
BACKUP_EVERY = 25
LABEL_COL, NOTE_COL, ID_COL = 'human_label', 'human_notes', 'event_id'
LOCK = threading.Lock()


def read_csv(path):
    with open(path, 'r', encoding='utf-8-sig', newline='') as fh:
        r = csv.DictReader(fh)
        return list(r.fieldnames), [dict(row) for row in r]


def write_csv_atomic(path, fieldnames, rows):
    tmp = path.with_suffix(path.suffix + '.tmp')
    with open(tmp, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames, extrasaction='raise')
        w.writeheader()
        for row in rows:
            w.writerow(row)
        fh.flush(); os.fsync(fh.fileno())
    os.replace(tmp, path)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Dataset:
    def __init__(self, key, workspace):
        self.key = key
        self.source = workspace / DATASETS[key][0]
        self.title = DATASETS[key][1]
        self.labeled = workspace / (self.source.stem + '_LABELED.csv')
        self.backup_dir = workspace / 'backups'
        if not self.source.exists():
            raise FileNotFoundError(f'source CSV not found: {self.source}')
        self.fieldnames, self.source_rows = read_csv(self.source)
        for c in (LABEL_COL, NOTE_COL, ID_COL, 'full_text_path'):
            if c not in self.fieldnames:
                raise ValueError(f'{self.source.name} lacks column {c}')
        if self.labeled.exists():
            fields, rows = read_csv(self.labeled)
            self._check_structure(fields, rows)
            self.rows = rows
            self.resumed = True
        else:
            self.rows = [dict(r) for r in self.source_rows]
            write_csv_atomic(self.labeled, self.fieldnames, self.rows)
            self.resumed = False
        self.saves_since_backup = 0
        self.backup('session')

    def _check_structure(self, fields, rows):
        if fields != self.fieldnames:
            raise ValueError(f'{self.labeled.name} columns differ from the source; refusing to continue')
        if len(rows) != len(self.source_rows):
            raise ValueError(f'{self.labeled.name} has {len(rows)} rows, source has {len(self.source_rows)}; refusing to continue')
        if [r[ID_COL] for r in rows] != [r[ID_COL] for r in self.source_rows]:
            raise ValueError(f'{self.labeled.name} event_id order differs from the source; refusing to continue')

    def backup(self, tag):
        self.backup_dir.mkdir(exist_ok=True)
        dest = self.backup_dir / f"{self.source.stem}_LABELED_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{tag}.csv"
        shutil.copy2(self.labeled, dest)
        self.saves_since_backup = 0
        return dest

    def save(self):
        write_csv_atomic(self.labeled, self.fieldnames, self.rows)
        self.saves_since_backup += 1
        if self.saves_since_backup >= BACKUP_EVERY:
            self.backup('periodic')

    def set_label(self, i, label, note=None):
        if label not in VALID and label != '':
            raise ValueError(f'label must be one of {"".join(VALID)} (or blank to clear)')
        row = self.rows[i]
        prev = dict(label=row[LABEL_COL], note=row[NOTE_COL])
        row[LABEL_COL] = label
        if note is not None:
            row[NOTE_COL] = note
        self.save()
        return prev

    def set_note(self, i, note):
        row = self.rows[i]; prev = row[NOTE_COL]
        row[NOTE_COL] = note; self.save()
        return prev

    def restore(self, i, label, note):
        self.rows[i][LABEL_COL] = label; self.rows[i][NOTE_COL] = note; self.save()

    def is_labeled(self, i):
        return self.rows[i][LABEL_COL].strip().upper() in VALID

    def progress(self):
        done = sum(self.is_labeled(i) for i in range(len(self.rows)))
        n = len(self.rows)
        return dict(key=self.key, title=self.title, total=n, done=done, remaining=n - done, pct=round(100.0 * done / n, 1) if n else 0.0,
                    first_unlabeled=self.next_unlabeled(-1), labeled_file=str(self.labeled), complete=done == n)

    def next_unlabeled(self, i):
        n = len(self.rows)
        for k in list(range(i + 1, n)) + list(range(0, max(i, 0))):      # every row except i itself, i+1 first, then wrap
            if not self.is_labeled(k):
                return k
        return None

    def prev_unlabeled(self, i):
        n = len(self.rows)
        for k in list(range(i - 1, -1, -1)) + list(range(n - 1, i, -1)):
            if not self.is_labeled(k):
                return k
        return None

    def find(self, text):
        t = text.strip().lower()
        for k, r in enumerate(self.rows):
            if t and (r[ID_COL].lower() == t or r.get('accession', '').lower() == t or t in r[ID_COL].lower()):
                return k
        return None

    def full_text(self, i, workspace):
        rel = self.rows[i]['full_text_path']
        path = (workspace / rel)
        if not path.exists():
            return None, str(path)
        return path.read_text(encoding='utf-8', errors='replace'), str(path)

    def integrity(self):
        labels = [r[LABEL_COL].strip().upper() for r in self.rows]
        valid = sum(l in VALID for l in labels); blank = sum(l == '' for l in labels); invalid = len(labels) - valid - blank
        ids_ok = [r[ID_COL] for r in self.rows] == [r[ID_COL] for r in self.source_rows]
        non_label_cols = [c for c in self.fieldnames if c not in (LABEL_COL, NOTE_COL)]
        cols_ok = all(r[c] == s[c] for r, s in zip(self.rows, self.source_rows) for c in non_label_cols)
        dup = len(set(r[ID_COL] for r in self.rows)) != len(self.rows)
        return dict(dataset=self.title, source_file=self.source.name, source_rows=len(self.source_rows), output_file=self.labeled.name, output_rows=len(self.rows),
                    valid_label_rows=valid, blank_label_rows=blank, invalid_label_rows=invalid, event_ids_unchanged=ids_ok, non_label_columns_unchanged=cols_ok,
                    duplicate_event_ids=dup, columns_unchanged=True, complete=(valid == len(self.rows)), sha256_output=sha256(self.labeled), sha256_source=sha256(self.source))


class App:
    def __init__(self, workspace=WORKSPACE):
        self.workspace = workspace
        self.ds = {k: Dataset(k, workspace) for k in DATASETS}
        self.undo_stack = []
        self.guide = (workspace / 'phase8b_labeling_guide.md').read_text(encoding='utf-8') if (workspace / 'phase8b_labeling_guide.md').exists() else 'Guide file not found.'

    def state(self):
        p = {k: d.progress() for k, d in self.ds.items()}
        total = sum(v['total'] for v in p.values()); done = sum(v['done'] for v in p.values())
        return dict(datasets=p, total=total, done=done, all_complete=done == total, undo_available=len(self.undo_stack),
                    workspace=str(self.workspace), resumed={k: d.resumed for k, d in self.ds.items()})

    def row(self, key, i):
        d = self.ds[key]; i = int(i)
        if not 0 <= i < len(d.rows):
            raise IndexError('row out of range')
        r = dict(d.rows[i])
        return dict(index=i, total=len(d.rows), row=r, labeled=d.is_labeled(i), current_label=r[LABEL_COL].strip().upper(), note=r[NOTE_COL],
                    next_unlabeled=d.next_unlabeled(i), prev_unlabeled=d.prev_unlabeled(i))

    def label(self, key, i, label, note):
        d = self.ds[key]; i = int(i)
        with LOCK:
            prev = d.set_label(i, label.strip().upper(), note)
            self.undo_stack.append(dict(ds=key, index=i, prev_label=prev['label'], prev_note=prev['note'], new_label=label.strip().upper()))
            self.undo_stack = self.undo_stack[-50:]
        self.maybe_report()
        return dict(saved=True, index=i, next_unlabeled=d.next_unlabeled(i), progress=d.progress(), state=self.state())

    def note(self, key, i, note):
        d = self.ds[key]
        with LOCK:
            d.set_note(int(i), note)
        return dict(saved=True)

    def undo(self):
        with LOCK:
            if not self.undo_stack:
                return dict(undone=False)
            u = self.undo_stack.pop()
            self.ds[u['ds']].restore(u['index'], u['prev_label'], u['prev_note'])
        return dict(undone=True, ds=u['ds'], index=u['index'], restored_label=u['prev_label'], state=self.state())

    def maybe_report(self):
        if all(d.progress()['complete'] for d in self.ds.values()):
            self.write_report()

    def write_report(self):
        reps = {k: d.integrity() for k, d in self.ds.items()}
        lines = ['PHASE8B_HUMAN_LABELING_INTEGRITY - neutral completeness and structure check (counts and hashes only)', f'generated: {datetime.now().isoformat(timespec="seconds")}', '']
        for k, r in reps.items():
            lines += [f"[{r['dataset']}]"] + [f'  {kk}: {vv}' for kk, vv in r.items() if kk != 'dataset'] + ['']
        path = self.workspace / 'PHASE8B_HUMAN_LABELING_INTEGRITY.txt'
        path.write_text('\n'.join(lines), encoding='utf-8')
        return path, reps


HTML_PATH = HERE / 'labeler.html'


class Handler(BaseHTTPRequestHandler):
    app = None

    def log_message(self, fmt, *args):
        pass

    def _send(self, code, body, ctype='application/json'):
        data = body if isinstance(body, bytes) else json.dumps(body).encode('utf-8')
        self.send_response(code); self.send_header('Content-Type', ctype + '; charset=utf-8'); self.send_header('Content-Length', str(len(data)))
        self.send_header('Cache-Control', 'no-store'); self.end_headers(); self.wfile.write(data)

    def do_GET(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == '/':
                return self._send(200, HTML_PATH.read_bytes(), 'text/html')
            if u.path == '/api/state':
                return self._send(200, self.app.state())
            if u.path == '/api/row':
                return self._send(200, self.app.row(q['ds'], q['i']))
            if u.path == '/api/fulltext':
                text, path = self.app.ds[q['ds']].full_text(int(q['i']), self.app.workspace)
                if text is None:
                    return self._send(404, dict(error=f'Full text file is missing: {path}', path=path))
                return self._send(200, dict(text=text, path=path))
            if u.path == '/api/guide':
                return self._send(200, dict(guide=self.app.guide))
            if u.path == '/api/find':
                k = self.app.ds[q['ds']].find(q.get('q', ''))
                return self._send(200, dict(index=k))
            if u.path == '/api/integrity':
                path, reps = self.app.write_report()
                return self._send(200, dict(path=str(path), reports=reps))
            return self._send(404, dict(error='not found'))
        except Exception as exc:  # surfaced to the UI, never silent
            return self._send(500, dict(error=f'{type(exc).__name__}: {exc}'))

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get('Content-Length', '0')); body = json.loads(self.rfile.read(n) or b'{}')
        try:
            if u.path == '/api/label':
                return self._send(200, self.app.label(body['ds'], body['i'], body['label'], body.get('note')))
            if u.path == '/api/note':
                return self._send(200, self.app.note(body['ds'], body['i'], body.get('note', '')))
            if u.path == '/api/undo':
                return self._send(200, self.app.undo())
            if u.path == '/api/backup':
                return self._send(200, dict(files=[str(d.backup('manual')) for d in self.app.ds.values()]))
            return self._send(404, dict(error='not found'))
        except Exception as exc:
            return self._send(500, dict(error=f'{type(exc).__name__}: {exc}'))


def serve(workspace=WORKSPACE, port=PORT, open_browser=True):
    url = f'http://127.0.0.1:{port}/'
    try:
        httpd = ThreadingHTTPServer(('127.0.0.1', port), Handler)
    except OSError as exc:
        print(f'The labeler is already running (port {port} is in use: {exc}). Opening {url} in your browser; use that window.', flush=True)
        if open_browser and os.environ.get('PHASE8B_LABELER_NO_BROWSER') != '1':
            webbrowser.open(url)
        return
    Handler.app = App(workspace)
    print(f'Phase 8B labeler: workspace {workspace}\n  {url}\n  Close this window (Ctrl+C) to stop; labels are already on disk.', flush=True)
    if open_browser and os.environ.get('PHASE8B_LABELER_NO_BROWSER') != '1':
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == '__main__':
    try:
        serve()
    except Exception as exc:
        print(f'\nERROR: {exc}\n', file=sys.stderr)
        input('Press Enter to close...')
        sys.exit(1)
