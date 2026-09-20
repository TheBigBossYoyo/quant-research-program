import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))
sys.path.insert(0, str(ROOT / 'research' / 'phase8b' / 'labeler'))
import phase8b_gold as gd  # noqa: E402
import phase8b_gold_eval as ge  # noqa: E402


def classified(n=6000, seed=0):
    rng = np.random.default_rng(seed)
    year = rng.integers(2004, 2018, n)
    p1 = rng.random(n) < 0.12
    label = np.where(p1, rng.choice(['A', 'B'], n), rng.choice(['D', 'H', 'I', 'G', 'UNCLASSIFIED'], n, p=[0.35, 0.3, 0.25, 0.07, 0.03]))
    return pd.DataFrame(dict(accession=[f'a{i}' for i in range(n)], cik=rng.integers(1, 2500, n).astype(float), company='C', filed=[f'{y}0601' for y in year], year=year, form='8-K', items='Other Events',
                             dev_pool=rng.random(n) < 0.2, p1_label=label, p1_primary=p1, p1_margin=rng.choice([0.5, 1.0, 2.0, 3.5], n), p1_rule='r', p1_evidence='e',
                             p2_primary=np.where(p1, rng.random(n) < 0.8, rng.random(n) < 0.05), p2_score=1.0))


class GoldSelectionTests(unittest.TestCase):
    def test_strata_sizes_pool_and_issuer_uniqueness(self):
        out = classified(); gold, pool, pos, neg, low = gd.select_gold(out)
        self.assertEqual(len(gold), 60)
        c = gold['stratum'].value_counts().to_dict()
        self.assertEqual((c['P_recent'], c['P_early'], c['N_obvious'], c['H_p1_only'], c['H_p2_only'], c['H_low_margin']), (19, 19, 10, 3, 3, 6))
        self.assertFalse(gold['dev_pool'].any())                                   # never from the development pool
        self.assertEqual(gold['cik'].nunique(), 60)                                # one case per issuer
        P = gold[gold['stratum'].str.startswith('P_')]
        self.assertTrue(P['p1_primary'].all()); self.assertTrue((P[P.stratum == 'P_recent']['year'] >= 2013).all()); self.assertTrue((P[P.stratum == 'P_early']['year'] <= 2012).all())
        N = gold[gold['stratum'] == 'N_obvious']
        self.assertFalse(N['p1_primary'].any()); self.assertFalse(N['p2_primary'].any()); self.assertFalse((N['p1_label'] == 'UNCLASSIFIED').any())
        self.assertEqual(sorted(gold['gold_id']), [f'G{i:03d}' for i in range(1, 61)])

    def test_order_is_shuffled_and_deterministic(self):
        a = gd.select_gold(classified())[0]; b = gd.select_gold(classified())[0]
        self.assertEqual(list(a['accession']), list(b['accession']))
        first_ten = a.head(10)['stratum'].str[0].tolist()
        self.assertGreater(len(set(first_ten)), 1)                                 # strata are interleaved, not blocked

    def test_walk_stratum_assignment_serves_P_first(self):
        q = dict(P_recent=1, P_early=0, N_obvious=1, H_p1_only=1, H_p2_only=1, H_low_margin=1)
        pos = dict(p1_primary=True, p2_primary=False, p1_margin=0.5, p1_label='A', year=2015)
        self.assertEqual(gd.stratum_for(pos, q, 1.5), 'P_recent')                  # a low-margin, pass-2-rejected positive still goes to P while P is open
        q['P_recent'] = 0
        self.assertEqual(gd.stratum_for(pos, q, 1.5), 'H_p1_only')
        self.assertEqual(gd.stratum_for(dict(pos, year=2008, p2_primary=True, p1_margin=1.0), q, 1.5), 'H_low_margin')
        self.assertIsNone(gd.stratum_for(dict(pos, year=2008, p2_primary=True, p1_margin=3.0), q, 1.5))
        neg = dict(p1_primary=False, p2_primary=False, p1_margin=2.0, p1_label='D', year=2010)
        self.assertEqual(gd.stratum_for(neg, q, 1.5), 'N_obvious'); self.assertIsNone(gd.stratum_for(dict(neg, p1_margin=1.0), q, 1.5))
        self.assertEqual(gd.stratum_for(dict(neg, p2_primary=True), q, 1.5), 'H_p2_only')
        self.assertEqual(gd.stratum_for(dict(neg, p1_label='UNCLASSIFIED', p1_margin=0.0), q, 1.5), 'H_low_margin')

    def test_draw_refused_when_not_frozen(self):
        if not gd.is_frozen():
            with self.assertRaises(RuntimeError):
                gd.draw(write=False)


class DecisionRuleTests(unittest.TestCase):
    def frame(self, n_correct, wrong_labels, rule='auth_new'):
        rows = [dict(gold_id=f'G{i}', stratum='P_recent' if i % 2 else 'P_early', human_label='NEW', p1_label='A', p1_primary=True, p1_rule=rule, p1_margin='2', p1_evidence='e', p2_primary='True', accession=f'a{i}') for i in range(n_correct)]
        rows += [dict(gold_id=f'W{i}', stratum='P_recent', human_label=l, p1_label='A', p1_primary=True, p1_rule=r, p1_margin='1', p1_evidence='e', p2_primary='False', accession=f'w{i}') for i, (l, r) in enumerate(wrong_labels)]
        rows += [dict(gold_id=f'N{i}', stratum='N_obvious', human_label='ROUTINE', p1_label='D', p1_primary=False, p1_rule='activity', p1_margin='2', p1_evidence='e', p2_primary='False', accession=f'n{i}') for i in range(10)]
        df = pd.DataFrame(rows); df['human_primary'] = df['human_label'].isin(ge.POS_HUMAN)
        return df

    def test_pass_borderline_fail_thresholds_on_38(self):
        self.assertEqual(ge.evaluate(self.frame(38, []))['verdict'], 'PASS')
        self.assertEqual(ge.evaluate(self.frame(37, [('RENEWAL', 'auth_new')]))['verdict'], 'PASS')              # 37/38 = 97.4%
        self.assertEqual(ge.evaluate(self.frame(36, [('RENEWAL', 'auth_new'), ('ASR', 'auth_increase')]))['verdict'], 'BORDERLINE')   # 94.7%
        self.assertEqual(ge.evaluate(self.frame(33, [('RENEWAL', 'r1'), ('ASR', 'r2'), ('IRRELEVANT', 'r3'), ('SELF_TENDER', 'r4'), ('AMBIGUOUS', 'r5')]))['verdict'], 'FAIL')

    def test_systematic_patterns_block_a_pass(self):
        rep = ge.evaluate(self.frame(36, [('ROUTINE', 'r1'), ('ROUTINE', 'r2')]))                               # two routine updates called positive
        self.assertEqual(rep['verdict'], 'FAIL_OR_REPAIR'); self.assertTrue(rep['systematic']['flag'])
        rep = ge.evaluate(self.frame(36, [('RENEWAL', 'same'), ('ASR', 'same')]))                               # same rule fired twice wrongly
        self.assertEqual(rep['verdict'], 'FAIL_OR_REPAIR')

    def test_ambiguous_counts_against_headline_and_is_reported(self):
        rep = ge.evaluate(self.frame(37, [('AMBIGUOUS', 'auth_new')]))
        h = rep['headline_stratum_P']
        self.assertEqual((h['correct'], h['n'], h['ambiguous']), (37, 38, 1)); self.assertAlmostEqual(h['precision_excluding_ambiguous'], 1.0)

    def test_interval_reported_not_used(self):
        rep = ge.evaluate(self.frame(38, []))
        lo, hi = rep['headline_stratum_P']['ci95']
        self.assertLess(lo, 0.95); self.assertEqual(hi, 1.0); self.assertEqual(rep['verdict'], 'PASS')

    def test_clopper_pearson(self):
        lo, hi = ge.clopper_pearson(38, 38); self.assertAlmostEqual(lo, 0.9075, places=3)
        lo, hi = ge.clopper_pearson(0, 10); self.assertEqual(lo, 0.0)

    def test_unlabelled_rows_block_evaluation(self):
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            pd.DataFrame(dict(gold_id=['G001', 'G002'], human_label=['NEW', ''], human_notes=['', ''])).to_csv(d / 'lab.csv', index=False)
            pd.DataFrame(dict(gold_id=['G001', 'G002'], stratum=['P_recent', 'P_early'], p1_primary=['True', 'True'], p1_label=['A', 'A'], p1_rule=['r', 'r'], p2_primary=['True', 'True'])).to_csv(d / 'key.csv', index=False)
            with self.assertRaises(RuntimeError):
                ge.load(d / 'lab.csv', d / 'key.csv')


class SnippetTests(unittest.TestCase):
    COVER = ('UNITED STATES SECURITIES AND EXCHANGE COMMISSION WASHINGTON, D.C. 20549 FORM 8-K CURRENT REPORT Pursuant to Section 13 or 15(d) of the Securities Exchange Act of 1934 '
             'REX CORPORATION (Exact name of registrant as specified in its charter) 2875 Needmore Road, Dayton, Ohio Registrant telephone number (937) 276-3931 Check the appropriate box below '
             'Item 8.01 Other Events ')

    def setUp(self):
        import gold_snippet
        self.gs = gold_snippet

    def test_cover_page_is_cut_and_decisive_sentence_kept(self):
        kp = self.COVER + 'On August 2, 2012, REX issued a press release announcing that the Board of Directors authorized the repurchase of up to an additional 500,000 shares. A copy is attached as Exhibit 99.1.'
        out = self.gs.minimal_snippet(kp, '')
        text = ' '.join(out['sentences'])
        self.assertIn('authorized the repurchase of up to an additional 500,000 shares', text)
        self.assertNotIn('SECURITIES AND EXCHANGE COMMISSION', text); self.assertNotIn('telephone', text)
        self.assertLess(len(text), 400); self.assertFalse(out['fallback'])

    def test_release_header_before_the_cue_is_skipped(self):
        kp = 'Box 1522 Elmira, New York (607) 737-3711 For Immediate Release: November 22, 2010 Chemung Financial Corporation today announced that its Board of Directors approved the extension of the current stock repurchase plan until November 16, 2011.'
        text = ' '.join(self.gs.minimal_snippet(kp, '')['sentences'])
        self.assertIn('approved the extension of the current stock repurchase plan', text); self.assertNotIn('Immediate Release', text)

    def test_ambiguity_safety_adds_one_sentence(self):
        kp = 'The Company announced that its Board of Directors approved a share repurchase program. The program replaces the prior authorization, which expired in June. Revenue grew five percent.'
        out = self.gs.minimal_snippet(kp, '')
        self.assertTrue(out['added_for_ambiguity']); self.assertEqual(len(out['sentences']), 2); self.assertIn('replaces the prior authorization', out['sentences'][1])
        clear = self.gs.minimal_snippet('The Board of Directors authorized the repurchase of an additional $250 million of common stock. Revenue grew five percent.', '')
        self.assertFalse(clear['added_for_ambiguity']); self.assertEqual(len(clear['sentences']), 1)

    def test_every_category_cue_can_be_the_decisive_sentence(self):
        for s in ('During the quarter the Company repurchased 1.2 million shares for $30 million.', 'The Company entered into an accelerated share repurchase agreement for $200 million.',
                  'The Company completed its $100 million share repurchase program.', 'The Board extended the share repurchase program through December 2016.',
                  'The Company commenced a Dutch auction tender offer for up to 5 million shares.'):
            out = self.gs.minimal_snippet('Revenue grew five percent. ' + s + ' Margins were stable.', '')
            self.assertEqual(out['sentences'][0], s)

    def test_forward_looking_boilerplate_loses_to_a_real_sentence(self):
        kp = ('Forward-looking statements include statements about share repurchases, dividends, authorized programs and additional increases. '
              'During the quarter the Company repurchased 500,000 shares.')
        self.assertEqual(self.gs.minimal_snippet(kp, '')['sentences'], ['During the quarter the Company repurchased 500,000 shares.'])

    def test_no_repurchase_wording_gives_notice_not_cover_page(self):
        out = self.gs.minimal_snippet(self.COVER + 'The Merger Agreement has been approved by the boards of directors.', 'The parties anticipate closing the Merger.')
        self.assertTrue(out['fallback']); self.assertTrue(out['no_repurchase_text'])
        self.assertNotIn('SECURITIES AND EXCHANGE', ' '.join(out['sentences']))

    def test_is_blind_to_model_output_and_limits_length(self):
        import inspect
        src = inspect.getsource(self.gs)
        for bad in ('SEALED', 'p1_', 'p2_', 'stratum', 'phase8b_classifier'):
            self.assertNotIn(bad, src)
        long_kp = ' '.join(f'The Board authorized an additional ${k} million share repurchase.' for k in range(1, 30))
        out = self.gs.minimal_snippet(long_kp, '')
        self.assertLessEqual(len(out['sentences']), 3); self.assertLessEqual(sum(map(len, out['sentences'])), self.gs.MAX_TOTAL_CHARS + 50)

    def test_frozen_gold_file_is_untouched_by_the_ui_change(self):
        import hashlib, json
        log = [json.loads(l) for l in (ROOT / 'research/phase8b/PHASE8B_FREEZE_HASHES.jsonl').read_text(encoding='utf8').splitlines() if l.strip()]
        rec = [r for r in log if r.get('file') == 'research/phase8b/gold/phase8b_gold_candidates.csv'][-1]
        self.assertEqual(hashlib.sha256((ROOT / rec['file']).read_bytes()).hexdigest(), rec['sha256'])


class GoldLabelerTests(unittest.TestCase):
    def test_nine_label_data_layer_on_temp_copy(self):
        import labeler_app as la
        import gold_labeler as gl
        saved = (la.VALID, la.DATASETS, la.ID_COL, la.EXTRA_REQUIRED, la.HTML_PATH, la.REPORT_NAME, la.BACKUP_EVERY)
        try:
            gl.configure()
            with tempfile.TemporaryDirectory() as d:
                ws = Path(d)
                with open(ws / 'phase8b_gold_candidates.csv', 'w', encoding='utf8', newline='') as fh:
                    w = csv.DictWriter(fh, fieldnames=['gold_id', 'company', 'filing_date', 'form', 'items_8k', 'source_document', 'key_passage', 'wider_context', 'human_label', 'human_notes'])
                    w.writeheader()
                    for i in range(3):
                        w.writerow(dict(gold_id=f'G{i + 1:03d}', company='X', filing_date='2015-01-01', form='8-K', items_8k='Other Events', source_document='EX-99.1', key_passage='p', wider_context='w', human_label='', human_notes=''))
                (ws / 'phase8b_gold_key_SEALED.csv').write_text('gold_id,p1_label\nG001,A\n', encoding='utf8')
                app = la.App(ws)
                self.assertEqual(app.state()['datasets']['gold']['total'], 3)
                app.label('gold', 0, 'increased', 'n')
                with self.assertRaises(ValueError):
                    app.label('gold', 1, 'A', '')                       # letters of the old scheme are not valid here
                app.label('gold', 1, 'AMBIGUOUS', '')
                rows = list(csv.DictReader(open(ws / 'phase8b_gold_candidates_LABELED.csv', encoding='utf8', newline='')))
                self.assertEqual([r['human_label'] for r in rows], ['INCREASED', 'AMBIGUOUS', ''])
                served = app.row('gold', 0); row = served['row']
                self.assertFalse(any(k.startswith('p1_') or k.startswith('p2_') or k == 'stratum' for k in row))     # nothing from the sealed key is served
                self.assertEqual(set(served['snippet']) - {'no_repurchase_text'}, {'sentences', 'added_for_ambiguity', 'fallback'})
                app2 = la.App(ws); self.assertEqual(app2.state()['datasets']['gold']['done'], 2); self.assertEqual(app2.state()['datasets']['gold']['first_unlabeled'], 2)
        finally:
            la.VALID, la.DATASETS, la.ID_COL, la.EXTRA_REQUIRED, la.HTML_PATH, la.REPORT_NAME, la.BACKUP_EVERY = saved
            la.App.row = gl._ORIGINAL_ROW

    def test_gold_page_mentions_no_model_output(self):
        html = (ROOT / 'research/phase8b/labeler/gold_labeler.html').read_text(encoding='utf8').lower()
        for bad in ('p1_', 'p2_', 'stratum', 'prediction', 'confidence', 'sealed', 'rationale'):
            self.assertFalse(bad in html, f'gold page mentions {bad!r}')


if __name__ == '__main__':
    unittest.main()
