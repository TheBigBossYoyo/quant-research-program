import inspect
import json
import sys
import unittest
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_classifier as clf  # noqa: E402

FILED = datetime(2015, 5, 8)


def rec(sentences, items='Other Events|Financial Statements and Exhibits', filed='20150508', lead_ex='', lead_8k=''):
    ks = [dict(doc='EX-99#1', i=k, hit=True, text=s) for k, s in enumerate(sentences)]
    return dict(filed=filed, items=items, lead_ex=lead_ex, lead_8k=lead_8k, key_sents=json.dumps(ks))


class SentenceRoleTests(unittest.TestCase):
    def role(self, s, earnings=False, filed=FILED):
        return clf.sentence_role(s, filed, earnings)

    def test_new_and_increase(self):
        self.assertEqual(self.role('The Company announced today that its Board of Directors has authorized the repurchase of up to $100 million of its common stock.'), 'AUTH_NEW')
        self.assertEqual(self.role('The Board of Directors has authorized an additional $250 million for its share repurchase program.'), 'AUTH_INCREASE')
        self.assertEqual(self.role('The Board increased the share repurchase authorization by $2 billion, for a total authorization of $5 billion.'), 'AUTH_INCREASE')
        self.assertEqual(self.role('MGI issued a press release announcing the increase in its share repurchase authorization of 5 million shares.'), 'AUTH_INCREASE')
        self.assertEqual(self.role('The Board authorized an increase to the current stock repurchase plan to purchase up to an aggregate of five million shares.'), 'AUTH_INCREASE')

    def test_descriptive_and_stale_are_not_events(self):
        for s in ('The Company\'s Stock Repurchase Plan authorizes the purchase of up to 12,000,000 shares of its common stock.',
                  'Under the stock repurchase program, the Company is authorized to acquire up to $5 billion of its outstanding shares.',
                  'The Company has $16.7 million available under its $20.0 million share repurchase program authorized in the fiscal 2007 fourth quarter.',
                  'This purchase is part of an ongoing repurchase plan approved by the Board of Directors, which authorizes repurchases up to $250,000.',
                  'In February 2008, the Board of Directors authorized a $500 million share repurchase program.',
                  'On August 20, 2007, the Company announced that its Board authorized increases to the stock repurchase program of $20 million.',
                  'During the quarter, the Board of Directors approved an authorization to repurchase up to an additional 10% of its outstanding shares.',
                  'As previously announced, the Board approved the repurchase of up to 8 million ordinary shares under the share repurchase program.',
                  'The policy provides that the Board of Directors may authorize cash distributions in the form of share repurchases of up to 75 percent of earnings.',
                  'The Board of Directors authorized a new $200 million share repurchase program that we announced in February.',
                  'I would also like to remind everyone that our Board of Directors recently approved an increase in the stock buy-back authorization from $2.0 million to $3.0 million.',
                  'The Federal Home Loan Bank board approved the repurchase of up to $500 million of excess capital stock held by members.',
                  'In January, our Board authorized a new $4 billion share buyback program, which reflects our confidence.',
                  'Last quarter, the Company announced that its Board of Directors authorized the repurchase of an additional $30.0 million of common stock.',
                  'As of the date of this release, the board of directors has not authorized a new stock repurchase program.',
                  'Also, as previously announced, the Company has adopted a program to repurchase up to an additional 2,000,000 shares in the open market.',
                  'The Company currently has $286 million authorized for share repurchase by the Board of Directors.'):
            self.assertIn(self.role(s), ('PAST_AUTH', 'MENTION', 'ACTIVITY', 'NOT_OWN'), s)      # never an authorisation event

    def test_month_only_reference_in_the_filing_month_is_fresh(self):
        self.assertEqual(self.role('In May, the Board of Directors authorized the repurchase of up to $50 million of its common stock.'), 'AUTH_NEW')            # filed 8 May
        self.assertEqual(self.role('In April, the Board of Directors authorized the repurchase of up to $50 million of its common stock.'), 'AUTH_NEW')          # previous month, filed early in the month
        self.assertEqual(self.role('In April, the Board of Directors authorized the repurchase of up to $50 million of its common stock.', filed=datetime(2015, 5, 28)), 'PAST_AUTH')

    def test_recent_explicit_date_is_fresh(self):
        self.assertEqual(self.role('On May 6, 2015, the Board of Directors authorized the repurchase of up to $50 million of its common stock.', earnings=True), 'AUTH_NEW')

    def test_earnings_release_needs_freshness(self):
        s = 'The Board of Directors has authorized the repurchase of up to $100 million of common stock.'
        self.assertEqual(self.role(s, earnings=False), 'AUTH_NEW')
        self.assertEqual(self.role(s, earnings=True), 'AUTH_WEAK')
        self.assertEqual(self.role('The Company also announced today that its Board has authorized the repurchase of up to $100 million of common stock.', earnings=True), 'AUTH_NEW')

    def test_other_roles(self):
        self.assertEqual(self.role('The Board approved an extension of the share repurchase program through December 2016.'), 'AUTH_RENEW')
        self.assertEqual(self.role('The Company commenced a modified Dutch auction tender offer to repurchase up to 5,000,000 shares.'), 'TENDER')
        self.assertEqual(self.role('The board announced approval of an offer to repurchase up to 500,000 shares of common stock at $11.90 per share.'), 'TENDER')
        self.assertEqual(self.role('The Company entered into an accelerated share repurchase agreement to repurchase $200 million of common stock.'), 'ASR')
        self.assertEqual(self.role('The Company completed its $100 million share repurchase program.'), 'DONE')
        self.assertEqual(self.role('During the quarter the Company repurchased 1.2 million shares of common stock for $30 million.'), 'ACTIVITY')
        self.assertEqual(self.role('The Board authorized the repurchase of $50 million of its 6.5% senior notes.'), 'NOT_OWN')
        self.assertEqual(self.role('The investor received a warrant to purchase up to 750,000 shares of common stock.'), 'NOT_OWN')
        self.assertEqual(self.role('These repurchases will result in a pre-tax gain and our Board has authorized additional repurchases.'), 'NOT_OWN')


class Pass1Tests(unittest.TestCase):
    def test_labels(self):
        self.assertEqual(clf.pass1(rec(['The Company announced today that its Board has authorized the repurchase of up to $100 million of its common stock.']))['label'], 'A')
        self.assertEqual(clf.pass1(rec(['The Board has authorized an additional $250 million for its share repurchase program.']))['label'], 'B')
        self.assertEqual(clf.pass1(rec(['During the quarter the Company repurchased 1.2 million shares of common stock for $30 million.']))['label'], 'D')
        self.assertEqual(clf.pass1(rec(['The Company commenced a Dutch auction tender offer to repurchase up to 5,000,000 shares.']))['label'], 'J')
        self.assertEqual(clf.pass1(rec(['The investor received a warrant to purchase up to 750,000 shares of common stock.']))['label'], 'I')
        self.assertEqual(clf.pass1(rec([]))['label'], 'I')
        self.assertEqual(clf.pass1(rec(['The Company announced that its Board of Directors approved a share repurchase program.']))['label'], 'UNCLASSIFIED')

    def test_size_in_following_sentence_upgrades(self):
        r = rec(['The Company announced that its Board of Directors approved a share repurchase program.', 'Under the program the Company may repurchase up to $50 million of its common stock.'])
        self.assertEqual(clf.pass1(r)['label'], 'A')

    def test_authorisation_beats_asr_and_progress_in_same_filing(self):
        r = rec(['The Board has authorized an additional $1 billion for its share repurchase program.', 'The Company entered into an accelerated share repurchase agreement.', 'During the quarter the Company repurchased 2 million shares of common stock.'])
        self.assertEqual(clf.pass1(r)['label'], 'B')

    def test_margin_rises_with_headline_and_standalone_item(self):
        s = ['XYZ Corp today announced that its Board has authorized the repurchase of up to $100 million of its common stock.']
        low = clf.pass1(rec(s, items='Results of Operations and Financial Condition'))
        high = clf.pass1(rec(s, lead_ex='XYZ Corp Announces $100 Million Share Repurchase Program'))
        self.assertGreater(high['margin'], low['margin'])


class Pass2Tests(unittest.TestCase):
    def test_pass2_never_receives_pass1_output(self):
        self.assertEqual(list(inspect.signature(clf.pass2).parameters), ['rec'])
        self.assertNotIn('pass1(', inspect.getsource(clf.pass2)); self.assertNotIn('p1_', inspect.getsource(clf.pass2))

    def test_pass2_scores(self):
        good = rec(['The Board has authorized a new share repurchase program of up to $100 million.'], lead_ex='XYZ Corp Announces New $100 Million Share Repurchase Program. The Board of Directors authorized the repurchase of up to $100 million.')
        self.assertTrue(clf.pass2(good)['primary'])
        noise = rec(['The investor received a warrant to purchase up to 750,000 shares.'], lead_ex='XYZ Corp announces registered direct offering of common stock and warrants', items='Entry into a Material Definitive Agreement')
        self.assertFalse(clf.pass2(noise)['primary'])
        routine = rec(['During the quarter the Company repurchased 1.2 million shares.'], lead_ex='XYZ Corp reports first quarter results. Revenue grew 5%.', items='Results of Operations and Financial Condition')
        self.assertFalse(clf.pass2(routine)['primary'])


if __name__ == '__main__':
    unittest.main()
