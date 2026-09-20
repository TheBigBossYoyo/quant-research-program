"""Minimal decisive snippet for the Phase 8B gold labeler (display only; standard library only).

Works purely on the text already stored in each frozen gold case (key_passage, wider_context). It never reads the sealed
key, so the choice of sentences cannot depend on any model output: the scoring below is a fixed lexical ranking of
category cue words of EVERY class (authorisation, increase, renewal, progress, ASR, completion, tender, non-equity).
Rules: 1-3 sentences; cover-page / contact / forward-looking boilerplate is dropped; glued cover-page "sentences" are
trimmed to the clause around the cue; if the chosen text has an authorisation cue but nothing that separates NEW from
INCREASED or RENEWAL, one more surrounding sentence is added (ambiguity safety).
"""
import re

SENT_SPLIT = re.compile(r'(?<=[.!?])\s+(?=["“(A-Z])')
REPURCHASE = re.compile(r'(repurchas\w*|buy[\s-]?back\w*|bought\s+back|tender\s+offer|dutch\s+auction|purchase\s+(of\s+)?up\s+to)', re.I)
AUTH = re.compile(r'\b(authoriz\w+|approv\w+|adopt\w+)\b', re.I)
CUES = [  # (pattern, weight): every category is represented, none is favoured
    (re.compile(r'\b(authoriz\w+|approv\w+|adopt\w+)\b', re.I), 4),
    (re.compile(r'\b(additional|increas\w+|expan\w+|rais\w+|in\s+addition\s+to)\b', re.I), 3),
    (re.compile(r'\bnew\b', re.I), 2),
    (re.compile(r'\b(exten\w+|renew\w+|re-?authoriz\w+)\b', re.I), 3),
    (re.compile(r'\b(remain\w*|existing|previously|prior|current(ly)?)\b', re.I), 2),
    (re.compile(r'accelerated\s+(share|stock)\s+repurchase|\bASR\b', re.I), 4),
    (re.compile(r'\b(complet\w+|expir\w+|terminat\w+|exhaust\w+|suspend\w+)\b', re.I), 3),
    (re.compile(r'\b(repurchased|bought\s+back|purchased)\b', re.I), 2),
    (re.compile(r'(tender\s+offer|dutch\s+auction)', re.I), 3),
    (re.compile(r'(repurchase\s+(program|plan|authorization)|share\s+repurchase|stock\s+repurchase|buy[\s-]?back)', re.I), 2),
    (re.compile(r'(\$\s?[\d,.]+\s*(million|billion)?|[\d,.]+\s*(million|billion)\s+shares|[\d,]{4,}\s+shares|\d+(\.\d+)?\s?(%|percent))', re.I), 1),
]
DISAMBIGUATOR = re.compile(r'\b(new|additional|increas\w+|expan\w+|exten\w+|renew\w+|existing|remain\w*|previous\w*|prior|replac\w+|complet\w+|expir\w+|first)\b', re.I)
BOILERPLATE = re.compile(r'(forward[\s-]looking|safe\s+harbor|securities\s+and\s+exchange\s+commission|exact\s+name\s+of\s+registrant|pursuant\s+to\s+the\s+requirements|'
                         r'check\s+the\s+appropriate\s+box|written\s+communications\s+pursuant|for\s+immediate\s+release|investor\s+relations|contacts?:|telephone|undersigned|'
                         r'signature|exhibit\s+index|shall\s+not\s+be\s+deemed|incorporated\s+(herein\s+)?by\s+reference|risks?\s+and\s+uncertainties|actual\s+results\s+(may|could)\s+differ)', re.I)
HEADER_BP = re.compile(r'(securities\s+and\s+exchange\s+commission|exact\s+name\s+of\s+registrant|check\s+the\s+appropriate\s+box|written\s+communications\s+pursuant|for\s+immediate\s+release|'
                       r'investor\s+relations|contacts?:|telephone)', re.I)      # cover page and release header: skipped when trimming
CONTENT_BP = re.compile(r'(forward[\s-]looking|safe\s+harbor|risks?\s+and\s+uncertainties|actual\s+results\s+(may|could)\s+differ|shall\s+not\s+be\s+deemed|incorporated\s+(herein\s+)?by\s+reference|'
                        r'undersigned|signature|exhibit\s+index|pursuant\s+to\s+the\s+requirements)', re.I)   # legal boilerplate: penalised as a whole sentence
CLAUSE_START = re.compile(r'(?:(?<=\s)|^)(On\s+(January|February|March|April|May|June|July|August|September|October|November|December)|In\s+addition|Additionally|Also|The\s+(Company|Board|Registrant|Corporation|Bank)|'
                          r'Our\s+Board|During\s+the|As\s+of|Effective|Under\s+the|[A-Z][\w&.,\' -]{2,60}?\s+(today\s+)?announced)')
ITEM_HEAD = re.compile(r'Item\s+\d{1,2}\.\d{2}\.?\s+(Other\s+Events|Regulation\s+FD(\s+Disclosure)?|Results\s+of\s+Operations(\s+and\s+Financial\s+Condition)?|Entry\s+into[^.]{0,60}?Agreement)\.?\s*', re.I)
MAX_SENT_CHARS = 480
MAX_SENTENCES = 3
MAX_TOTAL_CHARS = 900


def split_sentences(text):
    return [s.strip() for s in SENT_SPLIT.split(text or '') if s.strip()]


def score(sentence):
    if not REPURCHASE.search(sentence):
        return 0                                                # a decisive sentence must talk about repurchases
    s = sum(w for rx, w in CUES if rx.search(sentence))
    if BOILERPLATE.search(sentence):
        s -= 10                                                 # shown only when the filing offers nothing else
    return s


def trim_long(sentence):
    """A cover page or press-release header glued to the first real sentence: keep the clause around the first repurchase cue."""
    m = REPURCHASE.search(sentence) or AUTH.search(sentence)
    header = bool(m) and any(True for _ in HEADER_BP.finditer(sentence, 0, m.start()))      # release header / cover page before the cue
    if len(sentence) <= MAX_SENT_CHARS and not header:
        return sentence
    if not m:
        return sentence[:MAX_SENT_CHARS] + ' …'
    lo = max(0, m.start() - 360)
    start = None
    for h in ITEM_HEAD.finditer(sentence, lo, m.start()):
        start = h.end()
    if start is None:
        bp_end = max([b.end() for b in HEADER_BP.finditer(sentence, 0, m.start())] or [0])     # skip cover page, contacts, 'For Immediate Release'
        lo = max(lo, bp_end)
        starts = [c.start(1) for c in CLAUSE_START.finditer(sentence, lo, m.start())]
        start = starts[0] if starts else max(lo if bp_end else 0, m.start() - 220)
        if not starts and start > 0:
            sp = sentence.find(' ', start)
            start = sp + 1 if 0 <= sp < m.start() else start      # never cut inside a word
    end = min(len(sentence), max(m.end() + 300, start + MAX_SENT_CHARS))
    out = sentence[start:end].strip()
    return ('… ' if start > 0 else '') + out + (' …' if end < len(sentence) else '')


def minimal_snippet(key_passage, wider_context=''):
    """Returns dict(sentences=[...], added_for_ambiguity=bool, fallback=bool). Deterministic; no model input."""
    chunks = [c for c in (key_passage or '').split('[...]') if c.strip()]
    sents = []                                                  # (chunk index, position, text)
    for ci, c in enumerate(chunks):
        for pi, s in enumerate(split_sentences(c)):
            sents.append((ci, pi, trim_long(s), bool(CONTENT_BP.search(s))))   # show the clause, remember legal boilerplate
    if not sents:
        return dict(sentences=[(wider_context or '')[:MAX_TOTAL_CHARS]], added_for_ambiguity=False, fallback=True)
    sc = [score(t) - (10 if legal and score(t) > 0 else 0) for _, _, t, legal in sents]
    ranked = sorted(range(len(sents)), key=lambda k: (-sc[k], k))
    if sc[ranked[0]] <= 0:
        if wider_context and wider_context != key_passage:            # nothing decisive in the stored passage: try the wider context once
            again = minimal_snippet(wider_context, '')
            if not again['fallback']:
                return again
        keep = [t for _, _, t, _ in sents if REPURCHASE.search(t)] or [t for _, _, t, legal in sents if not legal and not BOILERPLATE.search(t)]
        return dict(sentences=[k[:MAX_SENT_CHARS] for k in keep[:2]], added_for_ambiguity=False, fallback=True, no_repurchase_text=not any(REPURCHASE.search(k) for k in keep[:2]))
    top = sc[ranked[0]]
    chosen = [ranked[0]]
    for k in ranked[1:]:
        if len(chosen) >= MAX_SENTENCES - 1:
            break
        if sc[k] >= max(5, top - 3) and not _near_duplicate(sents[k][2], [sents[j][2] for j in chosen]):
            chosen.append(k)
    text = ' '.join(sents[k][2] for k in chosen)
    added = False
    if AUTH.search(text) and not DISAMBIGUATOR.search(text):    # ambiguity safety: NEW vs INCREASED vs RENEWAL needs one more sentence
        k0 = chosen[0]
        for cand in (k0 + 1, k0 - 1):
            if 0 <= cand < len(sents) and cand not in chosen and sents[cand][0] == sents[k0][0] and not BOILERPLATE.search(sents[cand][2]):
                chosen.append(cand); added = True
                break
    out, total = [], 0
    for k in sorted(chosen):
        t = trim_long(sents[k][2])
        if total + len(t) > MAX_TOTAL_CHARS and out:
            break
        out.append(t); total += len(t)
    return dict(sentences=out, added_for_ambiguity=added, fallback=False)


def _near_duplicate(s, others):
    a = set(re.findall(r'\w+', s.lower()))
    for o in others:
        b = set(re.findall(r'\w+', o.lower()))
        if a and b and len(a & b) / min(len(a), len(b)) > 0.8:
            return True
    return False
