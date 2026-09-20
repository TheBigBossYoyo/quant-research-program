"""Phase 8B Amendment 3 (A3.4): evidence-anchored display builder for human validation. REPLACES the v1.7 lexical
snippet ranker, which was blind to the classifier and hid the decisive sentence in 13 of 38 predicted-positive cases.

Contract: the default visible passage ALWAYS contains, verbatim, the sentence the classifier used as its evidence,
plus one preceding and one following sentence where available, in document order and un-reranked. Nothing is scored,
nothing is dropped, nothing is re-ordered. The human is never scored against hidden evidence.

The human still sees no prediction, margin, rule name, stratum or rationale: this module returns TEXT only, and the
caller writes only text columns into the human CSV.

`assert_evidence_visible` is the mechanical preflight of A3.4. A case that fails it cannot enter a validation sample.
No prices, no returns, no locked data.
"""
import re
import unicodedata

import phase8b_corpus as cp
import phase8b_edgar as ed

BEFORE = 1
AFTER = 1
WIDE_CHARS = 2500
MIN_ANCHOR_CHARS = 40
DOC_TYPES = ('8-K', 'EX-99')
# cp1252 bytes decoded as latin-1 (\x91-\x97) are common in older EDGAR text and must not break matching
CP1252 = {'\x91': "'", '\x92': "'", '\x93': '"', '\x94': '"', '\x95': '-', '\x96': '-', '\x97': '-', '\xa0': ' ',
          '‘': "'", '’': "'", '“': '"', '”': '"', '–': '-', '—': '-', '­': ''}


def normalize(text):
    """Lowercase, fold typographic punctuation, drop everything that is not a letter/digit, collapse whitespace.
    Used for containment tests only; never for display."""
    s = unicodedata.normalize('NFKD', str(text or ''))
    for a, b in CP1252.items():
        s = s.replace(a, b)
    s = re.sub(r'[^0-9a-z]+', ' ', s.lower())
    return re.sub(r'\s+', ' ', s).strip()


def contains(haystack, needle):
    """True when `needle` appears in `haystack` after normalisation. Empty needles never count as visible."""
    n = normalize(needle)
    return bool(n) and n in normalize(haystack)


def _locate(sents, evidence):
    """Index of the sentence carrying the classifier evidence. The stored evidence may be a truncated prefix of the
    document sentence (the corpus clips sentences at 700 chars), so a normalised prefix match is accepted."""
    ev = normalize(evidence)
    if not ev:
        return None
    for i, s in enumerate(sents):                         # exact (normalised) containment first
        if ev in normalize(s):
            return i
    head = ev[:200]                                       # then the leading 200 normalised chars
    if len(head) >= MIN_ANCHOR_CHARS:
        for i, s in enumerate(sents):
            if head in normalize(s):
                return i
        for i, s in enumerate(sents):                     # finally: the document sentence is a prefix of the evidence
            ns = normalize(s)
            if len(ns) >= MIN_ANCHOR_CHARS and ev.startswith(ns):
                return i
    return None


def evidence_passage(accession, evidence, before=BEFORE, after=AFTER, wide_chars=WIDE_CHARS):
    """Default visible passage anchored on the classifier's evidence sentence.

    Returns dict(passage, sentences, evidence_sentence, document, wider_context, visible, reason).
    `visible` is False only when the evidence sentence cannot be located in the filing at all; such a case is refused
    by `assert_evidence_visible` and must not enter a validation sample.
    """
    f = ed.load_filing(accession)
    docs = [d for d in f['documents'] if d['type'].upper().startswith(DOC_TYPES)]
    for d in docs:
        sents = cp.sentences(d['text'])
        i = _locate(sents, evidence)
        if i is None:
            continue
        lo, hi = max(0, i - before), min(len(sents), i + after + 1)
        window = sents[lo:hi]
        passage = ' '.join(window)
        pos = d['text'].find(sents[i][:60])
        a = max(0, pos - wide_chars // 3) if pos >= 0 else 0
        wide = ('...' if a else '') + d['text'][a:a + wide_chars] + '...'
        return dict(passage=passage, sentences=window, evidence_sentence=sents[i], document=d['type'],
                    wider_context=wide, visible=contains(passage, evidence), reason='anchored on classifier evidence')
    return dict(passage='', sentences=[], evidence_sentence='', document=docs[0]['type'] if docs else '',
                wider_context=(docs[0]['text'][:wide_chars] if docs else ''), visible=False,
                reason='classifier evidence sentence not found in the filing text')


def assert_evidence_visible(accession, evidence, built=None):
    """Mechanical preflight (A3.4). Raises unless the default passage contains the classifier evidence verbatim."""
    b = built or evidence_passage(accession, evidence)
    if not b['visible'] or not contains(b['passage'], evidence):
        raise RuntimeError(f'classifier_evidence_visible == False for {accession}: {b["reason"]}; '
                           f'the case cannot enter the validation sample (Amendment 3 A3.4)')
    return True
