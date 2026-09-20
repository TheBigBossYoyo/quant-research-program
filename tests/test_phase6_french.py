import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase6_french as fr  # noqa: E402
import phase6_lock as lock  # noqa: E402

SYNTHETIC = """This file was created using the 202607 CRSP database.
It contains value- and equally-weighted returns for  10 prior return portfolios.

Missing data are indicated by -99.99 or -999.


  Average Value Weighted Returns -- Daily
,Lo PRIOR,PRIOR 2,Hi PRIOR
20171228,   0.10,   0.20,   0.30
20171229,  -0.10, -99.99,   0.50
20180102,   1.00,   1.00,   1.00

  Average Value Weighted Returns -- Monthly
,Lo PRIOR,PRIOR 2,Hi PRIOR
201711,   1.50,   2.50,   3.50
201712,   -999,   0.25,   0.75
201801,   9.00,   9.00,   9.00

  Number of Firms in Portfolios
,Lo PRIOR,PRIOR 2,Hi PRIOR
201712,    300,    301,    302

Copyright 2026 Eugene F. Fama and Kenneth R. French
"""

FACTOR = """This file was created by using the 202607 CRSP database.

Missing data are indicated by -99.99 or -999.

,Mom
20171229,   0.42
20180102,  -0.86

"""


class ParserTests(unittest.TestCase):
    def test_blocks_dates_and_missing_codes(self):
        blocks = fr.parse_blocks(SYNTHETIC)
        self.assertEqual(list(blocks), ['Average Value Weighted Returns -- Daily',
                                        'Average Value Weighted Returns -- Monthly',
                                        'Number of Firms in Portfolios'])
        daily = blocks['Average Value Weighted Returns -- Daily']
        self.assertEqual(daily.index[0], pd.Timestamp('2017-12-28'))
        self.assertTrue(np.isnan(daily.loc['2017-12-29', 'PRIOR 2']))
        monthly = blocks['Average Value Weighted Returns -- Monthly']
        self.assertEqual(monthly.index[1], pd.Timestamp('2017-12-31'))
        self.assertTrue(np.isnan(monthly.iloc[1, 0]))
        self.assertEqual(monthly.loc['2017-11-30', 'Hi PRIOR'], 3.5)
        self.assertEqual(fr.vintage(SYNTHETIC), '202607')

    def test_unnamed_factor_block(self):
        blocks = fr.parse_blocks(FACTOR)
        self.assertEqual(list(blocks), ['block0'])
        self.assertEqual(blocks['block0'].loc['2017-12-29', 'Mom'], 0.42)


class LoaderTests(unittest.TestCase):
    def setUp(self):
        if not (fr.FOLDER / fr.FILES['mom10_monthly']).exists():
            self.skipTest('French archives not present')

    def test_semantic_block_selection_across_title_variants(self):
        for key in ('mom10_monthly', 'strev10_monthly', 'var_monthly', 'size_monthly', 'ind49_monthly'):
            name = fr.select_block(fr.parse_blocks(fr.read_text(key)), 'vw_monthly')
            self.assertIn('monthly', name.lower())
            self.assertNotIn('annual', name.lower())
        self.assertEqual(fr.select_block(fr.parse_blocks(fr.read_text('ff3_monthly')), 'main'), 'block0')
        with self.assertRaises(KeyError):
            fr.select_block(fr.parse_blocks(fr.read_text('mom10_monthly')), 'Returns')  # ambiguous substring

    def test_development_load_is_truncated_and_decimal(self):
        df = fr.load('mom10_monthly', 'vw_monthly')
        self.assertTrue(lock.assert_development(df.index))
        self.assertGreaterEqual(df.index.min(), lock.FRENCH_DEV_START)
        self.assertEqual(df.index.max(), pd.Timestamp('2017-12-31'))
        self.assertEqual(len(df.columns), 10)
        self.assertLess(df.abs().max().max(), 1.5)  # decimal, not percent

    def test_validation_load_is_refused(self):
        with self.assertRaises(lock.LockError):
            fr.load('mom10_monthly', 'vw_monthly', segment='validation')

    def test_manifest_matches_files(self):
        if not fr.MANIFEST.exists():
            self.skipTest('manifest not built')
        m = fr.verify_manifest()
        self.assertEqual(len(m['files']), len(fr.FILES))


if __name__ == '__main__':
    unittest.main()
