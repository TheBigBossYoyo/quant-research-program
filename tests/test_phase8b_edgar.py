import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'research'))
import phase8b_edgar as ed  # noqa: E402

RAW = """<SEC-DOCUMENT>0001193125-15-054256.txt : 20150219
<SEC-HEADER>0001193125-15-054256.hdr.sgml : 20150219
<ACCEPTANCE-DATETIME>20150219162634
ACCESSION NUMBER:\t\t0001193125-15-054256
CONFORMED SUBMISSION TYPE:\t8-K
PUBLIC DOCUMENT COUNT:\t\t2
CONFORMED PERIOD OF REPORT:\t20150219
ITEM INFORMATION:\t\tOther Events
ITEM INFORMATION:\t\tFinancial Statements and Exhibits
FILED AS OF DATE:\t\t20150219
DATE AS OF CHANGE:\t\t20150219

FILER:

\tCOMPANY DATA:\t
\t\tCOMPANY CONFORMED NAME:\t\t\tInvestar Holding Corp
\t\tCENTRAL INDEX KEY:\t\t\t0001602658
\t\tSTANDARD INDUSTRIAL CLASSIFICATION:\tSTATE COMMERCIAL BANKS [6022]
</SEC-HEADER>
<DOCUMENT>
<TYPE>8-K
<SEQUENCE>1
<FILENAME>d877514d8k.htm
<DESCRIPTION>8-K
<TEXT>
<HTML><BODY><P>Item&nbsp;8.01 <B>Other Events.</B></P><P>On February 19, 2015 the Company issued a press release.</P></BODY></HTML>
</TEXT>
</DOCUMENT>
<DOCUMENT>
<TYPE>EX-99.1
<SEQUENCE>2
<FILENAME>d877514dex991.htm
<DESCRIPTION>EX-99.1
<TEXT>
<html><body><script>var x = 1;</script><p>The Board authorized the repurchase of up to 250,000 shares.</p></body></html>
</TEXT>
</DOCUMENT>
<DOCUMENT>
<TYPE>GRAPHIC
<SEQUENCE>3
<FILENAME>logo.jpg
<TEXT>
begin 644 logo.jpg
M_]C_X``02D9)1@`!`0$`8`!@``#_VP!#``@&!@<&!0@'!P<)"0@*#!0-#`L+
end
</TEXT>
</DOCUMENT>
"""


class HeaderParsingTests(unittest.TestCase):
    def test_header_fields(self):
        h = ed.parse_header(RAW)
        self.assertEqual(h['acceptance'], '20150219162634'); self.assertEqual(h['filed'], '20150219'); self.assertEqual(h['form'], '8-K')
        self.assertEqual(h['items'], ['Other Events', 'Financial Statements and Exhibits']); self.assertEqual(h['sic_code'], '6022')
        self.assertEqual(h['company'], 'Investar Holding Corp'); self.assertEqual(h['cik'], '0001602658'); self.assertEqual(h['doc_count'], '2')

    def test_amendment_form_is_read_from_header(self):
        h = ed.parse_header(RAW.replace('CONFORMED SUBMISSION TYPE:\t8-K', 'CONFORMED SUBMISSION TYPE:\t8-K/A'))
        self.assertEqual(h['form'], '8-K/A')

    def test_missing_header_gives_none_fields(self):
        h = ed.parse_header('no header here')
        self.assertIsNone(h['acceptance']); self.assertIsNone(h['filed']); self.assertEqual(h['items'], [])


class DocumentParsingTests(unittest.TestCase):
    def test_keeps_8k_and_ex99_drops_graphics(self):
        docs = ed.parse_documents(RAW)
        self.assertEqual([d['type'] for d in docs], ['8-K', 'EX-99.1'])
        self.assertIn('Item 8.01 Other Events.', docs[0]['text'])
        self.assertIn('authorized the repurchase of up to 250,000 shares', docs[1]['text'])
        self.assertNotIn('var x', docs[1]['text'])

    def test_keep_types_pattern(self):
        for t in ('8-K', '8-K/A', 'EX-99', 'EX-99.1', 'EX-99.12', 'ex-99.1'):
            self.assertTrue(ed.KEEP_TYPES.match(t), t)
        for t in ('GRAPHIC', 'EX-10.1', 'EX-101.INS', 'XML', 'ZIP', 'EX-3.1'):
            self.assertFalse(ed.KEEP_TYPES.match(t), t)

    def test_html_to_text_collapses_whitespace_and_entities(self):
        self.assertEqual(ed.html_to_text('<p>a&nbsp;&nbsp;b</p>\n\n<p>c</p>'), 'a b c')
        self.assertEqual(ed.html_to_text('plain   text\n here'), 'plain text here')

    def test_submission_url(self):
        self.assertEqual(ed.submission_url('1602658', '0001193125-15-054256'),
                         'https://www.sec.gov/Archives/edgar/data/1602658/000119312515054256/0001193125-15-054256.txt')
        self.assertEqual(ed.submission_url('0001602658', '0001193125-15-054256'), ed.submission_url(1602658, '0001193125-15-054256'))

    def test_accession_year_guard(self):
        self.assertEqual(ed.guard_accession_year('0001193125-15-054256'), 2015)
        self.assertEqual(ed.guard_accession_year('0000950123-99-000001'), 1999)
        for bad in ('0001193125-18-000001', '0001193125-25-000001'):
            with self.assertRaises(ed.Phase8BLockError):
                ed.guard_accession_year(bad)

    def test_slug(self):
        self.assertEqual(ed.slug('"repurchase of up to"'), 'repurchase_of_up_to'); self.assertEqual(ed.slug('"buy-back"'), 'buy_back')


class ConfigTests(unittest.TestCase):
    def test_config_frozen_expressions(self):
        self.assertEqual(len(ed.TARGET), 24); self.assertTrue(ed.AUTH <= set(ed.TARGET)); self.assertEqual(len(ed.COMPLEMENT), 6)
        self.assertEqual(str(ed.RETRIEVAL_END.date()), '2017-12-31')


if __name__ == '__main__':
    unittest.main()
