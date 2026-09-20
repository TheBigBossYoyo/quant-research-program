import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_labeling as lb  # noqa: E402


class AllocationTests(unittest.TestCase):
    def test_floor_then_proportional(self):
        counts = pd.Series({2013: 100, 2014: 300, 2015: 2}, dtype=int)
        q = lb.allocate(counts, 40, 5)
        self.assertEqual(q[2015], 2)                       # capped at availability
        self.assertEqual(sum(q.values()), 40)
        self.assertGreater(q[2014], q[2013])

    def test_total_capped_by_availability(self):
        counts = pd.Series({2013: 3, 2014: 4}, dtype=int)
        q = lb.allocate(counts, 40, 5)
        self.assertEqual(q, {2013: 3, 2014: 4})


class SampleAndSplitTests(unittest.TestCase):
    def cand(self):
        rng = np.random.default_rng(0)
        n = 3000
        years = rng.integers(2004, 2018, n)
        return pd.DataFrame(dict(accession=[f'a{i}' for i in range(n)], cik=rng.integers(1, 800, n), year=years,
                                 file_date=pd.to_datetime(years.astype(str) + '-06-01'), auth_match=rng.random(n) < 0.3, matched='x', display_name=''))

    def test_sample_sizes_strata_and_issuer_uniqueness(self):
        s = lb.sample_candidates(self.cand())
        self.assertEqual(len(s), 240)
        self.assertEqual(s['stratum'].value_counts().to_dict(), {'S1': 160, 'S2': 80})
        self.assertTrue((s.groupby(['year', 'stratum']).size() >= 3).all())
        self.assertFalse(s.duplicated(['cik', 'year', 'stratum']).any())

    def test_sample_is_deterministic(self):
        a = lb.sample_candidates(self.cand(), seed=20260912); b = lb.sample_candidates(self.cand(), seed=20260912)
        self.assertEqual(list(a['accession']), list(b['accession']))
        c = lb.sample_candidates(self.cand(), seed=1)
        self.assertNotEqual(list(a['accession']), list(c['accession']))

    def test_split_one_third_holdout_within_cells_and_cik_consistent(self):
        s = lb.sample_candidates(self.cand()); s['split'] = lb.assign_split(s)
        share = (s['split'] == 'HOLDOUT').mean()
        self.assertTrue(0.25 <= share <= 0.40, share)
        for _, g in s.groupby('cik'):
            self.assertEqual(g['split'].nunique(), 1)                      # no issuer straddles the partitions
        single = s[~s['cik'].duplicated(keep=False)]
        for _, g in single.groupby(['year', 'stratum']):
            self.assertLessEqual(abs((g['split'] == 'HOLDOUT').sum() - len(g) // 3), 2)
        self.assertEqual(list(lb.assign_split(s)), list(s['split']))

    def test_split_forces_repeat_cik_into_first_partition(self):
        s = pd.DataFrame(dict(accession=list('abcdef'), cik=[1, 1, 1, 2, 3, 4], year=[2004, 2005, 2006, 2004, 2004, 2004], stratum=['S1'] * 6))
        s['split'] = lb.assign_split(s)
        self.assertEqual(s[s['cik'] == 1]['split'].nunique(), 1)


class PassageTests(unittest.TestCase):
    def test_passages_prioritise_authorisation_windows(self):
        filler = 'Revenue grew. ' * 200
        text = filler + 'During the quarter we repurchased 1,000 shares. ' + filler + 'The Board authorized a new share repurchase program of up to $50 million. ' + filler
        p = lb.passages(text, ctx=60, max_windows=1)
        self.assertIn('authorized a new share repurchase program', p)
        self.assertNotIn('repurchased 1,000 shares', p)

    def test_passages_empty_without_keywords(self):
        self.assertEqual(lb.passages('nothing relevant here'), '')
        self.assertEqual(lb.passages(''), '')

    def test_passages_merge_overlapping_windows(self):
        text = 'buyback ' * 50
        p = lb.passages(text, ctx=400, max_windows=4)
        self.assertEqual(p.count('[...]'), 0)

    def test_row_has_no_ticker_or_future_columns(self):
        rec = dict(accession='0000000001-15-000001', cik=1, file_date='2015-02-19', display_name='X Corp (XC) (CIK 0000000001)')
        texts = ('Item 8.01 the Board authorized a repurchase program', '', dict(company='X Corp', form='8-K', acceptance='20150219163000', items=['Other Events'], sic='S [1234]'), dict(documents=[dict(type='8-K', chars=50)]))
        row = lb._row(rec, texts)
        self.assertFalse(any('ticker' in k or 'price' in k or 'return' in k for k in row))
        self.assertEqual(row['human_label'], ''); self.assertEqual(row['full_text_path'], 'labeling_texts/0000000001-15-000001.txt')

    def test_complement_strata_by_items(self):
        comp = pd.DataFrame(dict(items=['8.01|9.01', '2.02|9.01', '2.02|8.01', '7.01', '', '5.02']))
        non = comp['items'].apply(lambda s: any(i in s.split('|') for i in lb.NON_EARNINGS_ITEMS) and lb.EARNINGS_ITEM not in s.split('|'))
        self.assertEqual(list(non), [True, False, False, True, False, False])


if __name__ == '__main__':
    unittest.main()
