"""Phase 8B Amendment 3: regression tests for the v1.8 classifier repairs, the preserved semantic distinctions and the
evidence-anchored display instrument.

Every sentence here is a GENERAL category example. No test is keyed to a gold case, an accession or a filing id, and
none of the 60 frozen reference labels is consulted.
"""
from datetime import datetime
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'research'))

import phase8b_classifier as clf
import phase8b_display as disp


FILED = datetime(2016, 2, 24)


def role(sentence, filed=FILED, earnings=False):
    return clf.sentence_role(sentence, filed, earnings)


class RepairATests(unittest.TestCase):
    """A capitalised place name never supplies newness; genuine newness still does."""

    def test_place_name_does_not_create_newness(self):
        for place in ('New York', 'New Jersey', 'New Hampshire', 'New Orleans'):
            self.assertFalse(clf.has_newness(f'Box 12, Elmira, {place} 14902 For Immediate Release: the Board approved '
                                             f'the extension of the current stock repurchase plan.'), place)

    def test_place_name_header_still_reads_as_renewal(self):
        s = ('Box 1522 Elmira, New York 14902 (607) 737-3711 For Immediate Release Chemung Financial Extends Share '
             'Repurchase Plan; the Board approved the extension of the current stock repurchase plan.')
        self.assertEqual(role(s, datetime(2010, 11, 23)), 'AUTH_RENEW')

    def test_title_case_new_programme_still_counts(self):
        self.assertTrue(clf.has_newness('Announces New Share Repurchase Program'))
        self.assertEqual(role('Announces New Share Repurchase Program: the Board approved a new $100 million share '
                              'repurchase program.'), 'AUTH_NEW')

    def test_newness_must_govern_the_programme(self):
        self.assertFalse(clf.has_newness('We will continue to consider new opportunities, but we would rather focus on '
                                         'our own healthcare solutions than repurchase shares.'))


class RepairBTests(unittest.TestCase):
    """Forward-looking / risk-factor boilerplate is never an announcement."""

    def test_forward_looking_list_is_not_an_event(self):
        s = ('Forward-looking statements include, without limitation, those regarding 2014 guidance, our capital '
             'allocation strategy and our share repurchase authorization.')
        self.assertTrue(clf.fls_boilerplate(s))
        self.assertEqual(role(s), 'MENTION')

    def test_safe_harbour_after_a_real_announcement_does_not_demote_it(self):
        s = ('The Board today approved a new $50 million share repurchase program. Forward-looking statements in this '
             'release involve risks and uncertainties.')
        self.assertFalse(clf.fls_boilerplate(s))
        self.assertEqual(role(s), 'AUTH_NEW')


class RepairCTests(unittest.TestCase):
    """Extension / renewal with no added capacity is RENEWAL; an extension that also adds capacity is INCREASED."""

    def test_pure_extension_is_renewal(self):
        self.assertEqual(role('On September 15, 2016, the Board of Directors approved an extension of the Company\'s '
                              'stock repurchase program to September 23, 2017.'), 'AUTH_RENEW')

    def test_reaffirmation_is_not_a_new_authorisation(self):
        self.assertNotIn(role('The Board of Directors reaffirmed its intent to repurchase up to 5% of its outstanding '
                              'shares annually.'), ('AUTH_NEW', 'AUTH_INCREASE'))

    def test_second_year_of_an_existing_programme_is_not_new(self):
        self.assertEqual(role('ANNOUNCES APPROVAL OF SECOND YEAR OF TWO-YEAR SHARE REPURCHASE PROGRAM',
                              datetime(2006, 5, 8)), 'AUTH_RENEW')

    def test_extension_that_adds_capacity_is_an_increase(self):
        self.assertEqual(role('The Board authorized an additional $50 million to repurchase shares and extended the '
                              'program by six months.'), 'AUTH_INCREASE')


class RepairETests(unittest.TestCase):
    """"authority" is authorisation terminology - but only an INCREASE OF it is an event."""

    def test_increase_of_authority_with_amounts(self):
        self.assertEqual(role("On February 26, 2016, the Board of Directors increased the Company's authority to "
                              'repurchase common stock from $30.5 million up to $100.0 million.'), 'AUTH_INCREASE')

    def test_increase_of_authority_without_an_amount(self):
        self.assertEqual(role("The Board approved an increase in the Company's authority to repurchase its common "
                              'stock.'), 'AUTH_INCREASE')

    def test_merely_having_authority_is_not_an_event(self):
        self.assertNotIn(role('The Company continues to have authority to repurchase up to 928,000 additional shares '
                              'under its plan.'), ('AUTH_NEW', 'AUTH_INCREASE'))


class PreservedDistinctionTests(unittest.TestCase):
    """The semantic distinctions Amendment 3 requires to survive the repair."""

    def test_remaining_under_existing_authorisation_is_not_an_increase(self):
        for s in ('As of the date hereof, $45 million remains available under the existing share repurchase authorization.',
                  'The Company has approximately $8 million remaining on its $20 million share repurchase program.',
                  'Under the board approved share repurchase plan, the Company can repurchase an additional 6.5 million shares.'):
            self.assertNotIn(role(s), ('AUTH_NEW', 'AUTH_INCREASE'), s)

    def test_in_addition_to_existing_authorisation_is_an_increase(self):
        for s in ('On July 26, 2016 the Board of Directors authorized a plan to repurchase $1 billion of the company\'s '
                  'common stock in addition to the existing stock repurchase plan.',
                  "This $50 million common stock repurchase program is in addition to the Company's currently-existing "
                  'stock repurchase programs authorized by the Board of Directors.'):
            self.assertEqual(role(s), 'AUTH_INCREASE', s)

    def test_replacement_of_a_prior_programme_is_new(self):
        self.assertEqual(role('The Board approved a new $300 million share repurchase program, replacing the prior '
                              'program.'), 'AUTH_NEW')
        self.assertEqual(role('The Board of Directors adopted a new $250 million repurchase authorization that '
                              'supersedes the previously announced program.'), 'AUTH_NEW')

    def test_quarterly_repurchases_are_not_an_authorisation(self):
        self.assertNotIn(role('During the fourth quarter, the Company purchased 1,047,664 shares of its common stock '
                              'at an average price of $86.68 per share.'), ('AUTH_NEW', 'AUTH_INCREASE'))

    def test_completed_programme(self):
        self.assertEqual(role('The Company completed its $500 million share repurchase program during the fourth '
                              'quarter.'), 'DONE')

    def test_non_equity_instruments_are_irrelevant(self):
        for s in ('The Company also granted the Initial Purchasers an option to purchase up to an additional '
                  '$20,000,000 in aggregate principal amount of notes to cover over-allotments.',
                  'The underwriters were granted a 30-day option to purchase up to 1,125,000 additional common units.',
                  'The Compensation Committee approved the following restricted stock repurchases from an officer.'):
            self.assertEqual(role(s), 'NOT_OWN', s)

    def test_accelerated_share_repurchase_is_asr(self):
        self.assertEqual(role('The Company entered into an accelerated share repurchase agreement with a counterparty '
                              'for $200 million.'), 'ASR')

    def test_rule_10b5_1_plan_is_execution_not_authorisation(self):
        for s in ('The Company adopted a pre-arranged stock trading plan for the purpose of repurchasing up to 1.3 '
                  "million shares of the Company's common stock.",
                  'On September 10, 2016, the Company adopted a written trading plan under Rule 10b5-1 which enables '
                  'the Company to repurchase shares.'):
            self.assertNotIn(role(s), ('AUTH_NEW', 'AUTH_INCREASE'), s)

    def test_the_10b5_1_guard_does_not_demote_genuine_authorisations(self):
        """The guard must only remove execution-plan sentences. Where a sentence both authorises a programme and
        mentions a 10b5-1 plan, v1.8 must reach the same role as v1.7 - the guard may not be the thing that changes it.
        (Some such sentences are demoted by the pre-existing generic "under a ... plan" past cue; that is v1.7
        behaviour, is in the conservative direction, and is documented in PHASE8B_CLASSIFIER_V18_DIFF.md.)"""
        import importlib.util
        spec = importlib.util.spec_from_file_location('v17', ROOT / 'research/phase8b/frozen_v1.7/phase8b_classifier_v1.7.py')
        v17 = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(v17)
        for s in ('The Board approved a new $100 million share repurchase program; repurchases may be made under a '
                  'Rule 10b5-1 plan.',
                  'The Board of Directors authorized the repurchase of up to $250 million of common stock, which may '
                  'be effected through a Rule 10b5-1 trading plan.'):
            self.assertTrue(clf.TRADING_PLAN.search(s), s)
            self.assertEqual(role(s), v17.sentence_role(s, FILED, False), s)

    def test_past_announcements_stay_past(self):
        self.assertEqual(role('As previously announced, the Board authorized a $300 million share repurchase '
                              'program.'), 'PAST_AUTH')


class NoCaseSpecificRulesTests(unittest.TestCase):
    """The repair must not have memorised individual filings."""

    def test_classifier_source_names_no_accession_or_gold_id(self):
        import re
        src = (ROOT / 'research' / 'phase8b_classifier.py').read_text(encoding='utf8')
        self.assertIsNone(re.search(r'\d{10}-\d{2}-\d{6}', src), 'classifier must not reference an accession number')
        self.assertIsNone(re.search(r'\bG0\d{2}\b', src), 'classifier must not reference a gold case id')
        for company in ('chemung', 'seacor', 'dycom', 'pioneer', 'schweitzer', 'amerigroup', 'caci', 'odyssey', 'evans'):
            self.assertNotIn(company, src.lower(), f'classifier must not name {company}')


class DisplayInstrumentTests(unittest.TestCase):
    """A3.4: the default passage always carries the classifier's evidence sentence verbatim."""

    def test_normalisation_folds_cp1252_and_punctuation(self):
        self.assertEqual(disp.normalize('The Company\x92s board'), disp.normalize("The Company's board"))
        self.assertEqual(disp.normalize('up to $100.0 million!'), 'up to 100 0 million')

    def test_contains_is_punctuation_insensitive(self):
        self.assertTrue(disp.contains('the Board’s plan was approved', "the Board's plan was approved"))
        self.assertFalse(disp.contains('the Board approved a plan', 'a completely different sentence'))

    def test_empty_evidence_is_never_visible(self):
        self.assertFalse(disp.contains('any passage at all', ''))

    def test_assert_refuses_when_evidence_is_absent(self):
        built = dict(passage='a passage without the sentence', visible=False, reason='not found')
        with self.assertRaises(RuntimeError):
            disp.assert_evidence_visible('0000000000-00-000000', 'some evidence sentence', built=built)

    def test_assert_passes_when_evidence_is_present(self):
        ev = 'The Board approved a new $50 million share repurchase program.'
        built = dict(passage=f'Before. {ev} After.', visible=True, reason='anchored')
        self.assertTrue(disp.assert_evidence_visible('0000000000-00-000000', ev, built=built))

    def test_locate_accepts_a_truncated_evidence_prefix(self):
        sents = ['Unrelated opening sentence.',
                 'The Board of Directors authorized the repurchase of up to $250 million of the Company’s common stock '
                 'over the next twenty-four months in open market transactions.']
        truncated = sents[1][:90]
        self.assertEqual(disp._locate(sents, truncated), 1)


if __name__ == '__main__':
    unittest.main()
