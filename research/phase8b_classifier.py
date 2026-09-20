"""Phase 8B automated classification passes (Amendment 2). Deterministic, documented rules; no labels, prices or returns.

Input: one corpus record (phase8b_corpus): items, filed date, lead_8k, lead_ex, key_sents (repurchase sentences).
pass1(rec) -> dict(label in A-J/UNCLASSIFIED, margin, rule, evidence): sentence-level authorisation grammar.
pass2(rec) -> dict(primary bool, score, cues): document-level weighted cue scorer over title/lead, item codes and a bag
of the repurchase sentences. pass2 is written without reference to pass1 outputs and never receives them.
Both were developed only on the development pool (corpus.dev_pool); the gold set is drawn from the other 80%.
"""
from datetime import datetime
import json
import re

VERSION = '1.8'
MONTHS = 'January|February|March|April|May|June|July|August|September|October|November|December'
MON_IDX = {m.lower(): i + 1 for i, m in enumerate(MONTHS.split('|'))}

# ---------------------------------------------------------------- shared vocabulary
OWN_REPURCHASE = re.compile(r'(repurchas\w*|buy[\s-]?back\w*|(purchase|acquire)\s+(of\s+)?up\s+to\b[^.;]{0,90}?\b(its|the\s+company.?s|our)\s+(own\s+)?(outstanding\s+)?(common\s+|ordinary\s+|class\s+a\s+)?(stock|shares))', re.I)
AUTH_VERB = re.compile(r'\b(authorized|approved|adopted|authorization\s+of|approval\s+of|adoption\s+of)\b|\b(board|directors)\b[^.;]{0,40}?\b(increased|expanded|raised)\b'
                       r'|\b(increase|expansion)\s+(in|of|to)\s+[^.;]{0,60}?(repurchase|buy[\s-]?back)\s+(authorization|program|plan)'
                       # repair E: "authority" / "authorized amount" are authorisation nouns
                       r'|\b(increase|expansion|increased|expanded|raised)\b[^.;]{0,60}?\b(authority|authorized\s+amount)\b', re.I)
DESCRIPTIVE = re.compile(r'\b(is|are|was|were|be|been|being|may|might|would|could|can|will|shall|to|remains?)\s+(also\s+|currently\s+|still\s+)?(authorized|approved)\b'
                         r'|\b(program|plan|authorization|policy)\s+(authorizes|permits|allows|provides)\b|\bmay\s+authorize\b'
                         r'|\b(program|plan|authorization)\s+(previously\s+)?(approved|authorized|adopted)\s+by\b|\bongoing\b|\bpart\s+of\s+(an?|the|its|our)\b'
                         r'|\b(program|plan|authorization)\s+(that\s+was\s+|which\s+was\s+)?(authorized|approved|adopted|announced)\s+(in|on|during)\b|\bavailable\s+(for|under)\b', re.I)
BOARD = re.compile(r'\b(board|directors)\b', re.I)
SIZE = re.compile(r'(\$\s?[\d,.]+\s*(million|billion|m\b|bn\b)?|[\d,.]+\s*(million|billion)\s+(of\s+)?(shares|dollars)|[\d,]{4,}\s+(shares|common\s+shares)|\d+(\.\d+)?\s?(%|percent)|up\s+to\s+[\d$]'
                  r'|\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|fifteen|twenty|twenty-five|thirty|forty|fifty|hundred)\s+(million|billion|thousand|hundred|percent))', re.I)
NEW_CUE = re.compile(r'\b(new|additional|increas\w+|expan\w+|rais\w+|enlarg\w+|supplement\w*)\b', re.I)
INCREASE_CUE = re.compile(r'\b(additional|increas\w+|expan\w+|rais\w+|enlarg\w+|supplement\w*|in\s+addition\s+to|upsiz\w+)\b', re.I)
RENEW_CUE = re.compile(r'\b(renew\w*|re-?authoriz\w+|reactivat\w+|extend\w*|extension|re-?approv\w+|reaffirm\w*|continu\w+\s+(of\s+)?(the|its)|(second|third|fourth|fifth|next)\s+year\s+of)\b', re.I)
PAST_CUE = re.compile(r'\b(previously|prior(ly)?|earlier|remind\w*|(that|which)\s+(we|was|were|the\s+company)\s+(had\s+)?announced|announced\s+(in|last)\s+\w+|existing|current(ly)?\s+authori|had\s+(previously\s+)?(authorized|approved)|originally|remain(s|ing|ed)?|since\s+(inception|the\s+inception|\w+\s+\d{4})|to\s+date|as\s+of\s+(' + MONTHS + r')|pursuant\s+to\s+(the|its|our)|under\s+(the|its|our|this|a)\s+[^.;]{0,60}?(program|plan|authorization))\b', re.I)
HARD_PAST = re.compile(r'\b(previously|prior(ly)?|at\s+that\s+time|earlier(?!\s+(today|this\s+(week|morning)))|remind\w*|(that|which)\s+(we|was|were|the\s+company)\s+(had\s+)?announced|announced\s+(in|last)\s+\w+|originally|last\s+(quarter|year|month|fall|spring|summer|winter)|a\s+year\s+ago)\b', re.I)
NEGATED = re.compile(r'\b(has|have|had|did|does|do|was|were|is|are)\s+not\b|\bnot\s+(yet\s+)?(been\s+)?(authorized|approved|adopted)\b|\bno\s+(new\s+)?(share|stock)?\s*(repurchase|buy[\s-]?back)\b', re.I)
MONTH_ONLY = re.compile(r'\b(in|during|since)\s+(early\s+|late\s+|mid-?\s*)?(' + MONTHS + r')\b(?!\s+\d)', re.I)
PERIOD_CUE = re.compile(r'\b(during\s+(the\s+)?(quarter|year|period|first|second|third|fourth|fiscal|three|six|nine|twelve)|for\s+the\s+(quarter|year|three|six|nine|twelve)|year[\s-]to[\s-]date|in\s+the\s+(first|second|third|fourth)\s+quarter)\b', re.I)
DONE_CUE = re.compile(r'\b(complet\w+|conclud\w+|exhaust\w+|expir\w+|terminat\w+|suspend\w+|discontinu\w+)\b', re.I)
REPURCHASED_ACTIVITY = re.compile(r'\b(repurchased|bought\s+back|purchased)\b[^.;]{0,80}?\b(shares|common\s+stock)\b', re.I)
ASR = re.compile(r'accelerated\s+(share|stock)\s+(repurchase|buy[\s-]?back)|\bASR\b', re.I)
TENDER = re.compile(r'(tender\s+offer|dutch\s+auction|self[\s-]tender|offer\s+to\s+(re)?purchase|odd[\s-]lot)', re.I)
NOT_OWN_EQUITY = re.compile(r'(warrants?\s+to\s+purchase|options?\s+to\s+(purchase|acquire)|underwrit\w+|over-?allot\w*|notes?\b|debentures?|bonds?\b|senior\s+(secured\s+)?(notes|debt)|debt\s+(repurchase|buy[\s-]?back)|convertible|preferred|preference\s+shares|units?\b|agreements?\s+to\s+repurchase|repurchase\s+agreements?|repurchase\s+(obligation|reserve|liabilit|demand|request)\w*|mortgage|loans?\b|receivables|redemption|upon\s+the\s+death|stockholders?\s+may\s+request|employee\s+stock\s+purchase|stock\s+plan|restricted\s+stock|right\s+of\s+first|put\s+right|the\s+fund\b|interval\s+fund|extinguishment|pre-?tax\s+gain|gain\s+on\s+(the\s+)?repurchase|excess\s+(capital\s+)?stock|capital\s+stock|federal\s+home\s+loan\s+bank|fhlbank|members?.?\s+(stock|shares))', re.I)
ANNOUNCE_NOW = re.compile(r'\b(today\s+announced|announced\s+today|announces|announced\s+that|announcing\s+that|has\s+(authorized|approved|adopted)|have\s+(authorized|approved))\b', re.I)
FOLLOW_PAST = re.compile(r'\b(previously|prior|existing|remain(s|ing|ed)?|originally|to\s+date|repurchased)\b', re.I)
DATE_RE = re.compile(r'\b(' + MONTHS + r')\s+(\d{1,2},?\s+)?((19|20)\d{2})\b', re.I)
YEAR_REF = re.compile(r'\b(in|during|since)\s+(fiscal\s+|calendar\s+)?((19|20)\d{2})\b', re.I)
STALE_DAYS = 21
FRESH = re.compile(r'\b(today|announc\w+|recently|subsequent(ly)?\s+to|new|newly|additional|increas\w+|expan\w+|rais\w+)\b', re.I)

# ---------------------------------------------------------------- Amendment 3 repairs (general semantics only)
# Repair A: "new" means newness only when it governs the programme. A capitalised place name ("New York", "New Jersey",
# "Newark") in an address or a glued release header never implies a new authorisation. Programme words are excluded
# from the place pattern so a title-case headline ("Announces New Share Repurchase Program") still counts.
PLACE_NEW = re.compile(r'\bNew\s+(?!(?:Share|Shares|Stock|Common|Ordinary|Class|Repurchase|Buyback|Buy|Program|Programme|Plan|Author)\b)[A-Z][a-zA-Z]+|\bNewark\b')
NEW_PROGRAMME = re.compile(r'\bnew\b[^.;]{0,60}?(repurchas\w*|buy[\s-]?back\w*|program\w*|plan\b|authoriz\w+)'
                           r'|(repurchas\w*|buy[\s-]?back\w*|program\w*|plan\b|authoriz\w+)[^.;]{0,40}?\bis\s+new\b', re.I)
# Repair B: a forward-looking-statements / safe-harbour / risk-factor list is never an announcement. Applied only when
# the boilerplate marker PRECEDES the repurchase cue, i.e. the repurchase words are items inside the legal list.
FLS = re.compile(r'forward[\s-]looking\s+statements?|safe\s+harbor|private\s+securities\s+litigation\s+reform'
                 r'|risks?\s+and\s+uncertainties|actual\s+results\s+(could|may|might)\s+differ', re.I)
# Repair D: a release headline that explicitly announces a repurchase programme is a freshness cue for the filing.
HEADLINE_ANNOUNCE = re.compile(r'(announc\w+|authoriz\w+|approv\w+|adopt\w+|initiat\w+|declar\w+)[^.]{0,90}?(repurchase|buy[\s-]?back)'
                               r'|(repurchase|buy[\s-]?back)\s+(program|programme|plan|authoriz\w+)[^.]{0,60}?(announc\w+|authoriz\w+|approv\w+|adopt\w+)', re.I)
PROGRAMME = re.compile(r'(repurchase|buy[\s-]?back)\s+(program|programme|plan|authoriz\w+)|(program|programme|plan)\s+to\s+(repurchase|buy\s+back)', re.I)
D_ANNOUNCE = re.compile(r'\b(announc\w+|adopt\w+|approv\w+|authoriz\w+|initiat\w+|commenc\w+)\b', re.I)
REMAINING = re.compile(r'\bremain\w*\b', re.I)
# A Rule 10b5-1 trading plan is an EXECUTION mechanism, not an authorisation; adopting one authorises nothing new.
TRADING_PLAN = re.compile(r'(rule\s+)?10b5-?1|pre-?arranged\s+(stock\s+)?trading\s+plan|written\s+trading\s+plan', re.I)
# repurchases of restricted stock from an employee/officer are not an issuer programme
RESTRICTED_BUYBACK = re.compile(r'restricted\s+stock\s+repurchas|repurchas\w*\s+[^.;]{0,40}?restricted\s+(stock|shares)', re.I)
# Preserved distinctions that v1.7 did not actually honour (Amendment 3 lists them explicitly; all are general):
#  - an increase OF THE AUTHORISATION ITSELF is INCREASED even when the sentence quotes no dollar size (repair E);
#  - "in addition to the existing/remaining authorization" is added capacity, not a status restatement;
#  - a newly approved programme REPLACING a completed/prior one is NEW, not a reference to the past.
AUTH_CAPACITY_INCREASE = re.compile(r'\b(increase|expansion)\s+(in|of|to)\s+(the\s+|its\s+|our\s+|their\s+)*(compan(y|ies).?s?\s+)*(share\s+|stock\s+|common\s+stock\s+)?(repurchase\s+)?(authority|authoriz\w+|program\w*|plan)\b'
                                    r'|\b(increased|expanded|raised|enlarged)\s+(the\s+|its\s+|our\s+|their\s+)*(compan(y|ies).?s?\s+)*(share\s+|stock\s+|common\s+stock\s+)?(repurchase\s+)?(authority|authoriz\w+|program\w*|plan)\b', re.I)
ADDED_CAPACITY = re.compile(r'\bin\s+addition\s+to\b', re.I)
REPLACEMENT = re.compile(r'\b(replac\w+|supersed\w+|succeed\w+|in\s+place\s+of)\b', re.I)
NEAR_CHARS = 120


def added_capacity_near(sentence, auth):
    """Added capacity counts only when it sits next to the authorisation verb; a glued slide deck or financial table
    can otherwise pair an unrelated "additional $200 million" with a distant "authorized"."""
    if not auth:
        return False
    return any(abs(m.start() - auth.start()) <= NEAR_CHARS for m in ADDED_CAPACITY.finditer(sentence))


def has_newness(sentence):
    """Repair A: True when the sentence carries newness that actually governs the programme. Capitalised place
    names are removed first, so "New York" in an address or header cannot supply the newness."""
    return bool(NEW_PROGRAMME.search(PLACE_NEW.sub(' ', sentence)))


def fls_boilerplate(sentence):
    """Repair B: True when the repurchase words sit inside forward-looking/risk-factor boilerplate that precedes them."""
    m = FLS.search(sentence)
    if not m:
        return False
    r = OWN_REPURCHASE.search(sentence)
    return bool(r) and m.start() < r.start()


def _filed(rec):
    return datetime.strptime(str(rec['filed'])[:8], '%Y%m%d')


def stale_date(sentence, filed):
    """True when the sentence carries an explicit date more than STALE_DAYS before the filing date."""
    for m in DATE_RE.finditer(sentence):
        mon = MON_IDX[m.group(1).lower()]; year = int(m.group(3)); day = int(re.sub(r'\D', '', m.group(2))) if m.group(2) else 15
        try:
            d = datetime(year, mon, min(day, 28))
        except ValueError:
            continue
        if (filed - d).days > STALE_DAYS:
            return True
    for m in YEAR_REF.finditer(sentence):
        if int(m.group(3)) < filed.year:
            return True
    for m in MONTH_ONLY.finditer(sentence):                       # "In May, our Board authorized ..." in an August filing
        months_back = (filed.month - MON_IDX[m.group(3).lower()]) % 12
        if months_back >= 2 or (months_back == 1 and filed.day > STALE_DAYS):
            return True
    return False


def recent_date(sentence, filed):
    """True when the sentence carries an explicit date within STALE_DAYS before the filing date."""
    for m in DATE_RE.finditer(sentence):
        mon = MON_IDX[m.group(1).lower()]; year = int(m.group(3)); day = int(re.sub(r'\D', '', m.group(2))) if m.group(2) else 15
        try:
            d = datetime(year, mon, min(day, 28))
        except ValueError:
            continue
        if 0 <= (filed - d).days <= STALE_DAYS:
            return True
    return False


def key_sentences(rec):
    ks = rec['key_sents']
    return json.loads(ks) if isinstance(ks, str) else ks


# ---------------------------------------------------------------- pass 1: sentence-level grammar
def sentence_role(s, filed, earnings_release=False):
    """Role of one repurchase sentence: AUTH_NEW, AUTH_INCREASE, AUTH_RENEW, AUTH_WEAK, PAST_AUTH, ACTIVITY, DONE,
    ASR, TENDER, NOT_OWN, MENTION."""
    own = OWN_REPURCHASE.search(s)
    if not own:
        return 'NOT_OWN' if NOT_OWN_EQUITY.search(s) else 'MENTION'
    if fls_boilerplate(s):
        return 'MENTION'                                           # repair B: legal boilerplate is never an event
    if RESTRICTED_BUYBACK.search(s):
        return 'NOT_OWN'                                           # restricted-stock buybacks from insiders are not a programme
    if TENDER.search(s):
        return 'TENDER'
    if NOT_OWN_EQUITY.search(s) and not re.search(r'(share|stock)\s+(repurchase|buy[\s-]?back)', s, re.I):
        return 'NOT_OWN'
    if ASR.search(s):
        return 'ASR'
    if TRADING_PLAN.search(s) and not has_newness(s) and not INCREASE_CUE.search(s) \
            and not (AUTH_VERB.search(s) and BOARD.search(s) and SIZE.search(s)):
        return 'ACTIVITY'      # adopting a 10b5-1 plan is execution, not authorisation - unless the same
                               # sentence is itself a board authorisation of an amount
    auth = AUTH_VERB.search(s)
    # a newly approved programme that REPLACES a completed/prior one is NEW: its backward reference is subordinate
    replaces_prior = bool(REPLACEMENT.search(s) and has_newness(s))
    if auth and (len(re.findall(r'\d[\d,.]*', s)) >= 12 or len(re.findall(r'[•▪·]', s)) >= 2):
        return 'MENTION'                                           # financial table or slide bullets glued into one "sentence"
    if auth and NEGATED.search(s):
        return 'MENTION'                                           # "has not authorized a new stock repurchase program"
    if auth and HARD_PAST.search(s) and not replaces_prior:
        return 'PAST_AUTH'         # "as previously announced ...", "last quarter ..." are never overridden, EXCEPT when
                                   # the sentence approves a new programme replacing the prior one (replaces_prior)
    if auth and re.search(r'\b(has|have|had)\s+\$?\s?[\d,.]+\s*(million|billion)?\s+(remaining\s+)?authorized\b', s, re.I):
        return 'PAST_AUTH'                                         # "currently has $286 million authorized for share repurchase"
    if auth and DESCRIPTIVE.search(s) and not ANNOUNCE_NOW.search(s):
        return 'PAST_AUTH'
    if auth and (BOARD.search(s) or re.search(r'\b(company|corporation|we|it|its|our|announc\w+)\b', s, re.I)):
        if stale_date(s, filed):                                   # an explicit old date always wins
            return 'PAST_AUTH'
        if PERIOD_CUE.search(s) and not re.search(r'\btoday\b', s, re.I):    # "during the quarter the Board approved ..." may be old news
            return 'PAST_AUTH'
        if PAST_CUE.search(s) and not replaces_prior and not (INCREASE_CUE.search(s) and (ANNOUNCE_NOW.search(s) or added_capacity_near(s, auth))):
            return 'PAST_AUTH'
        if RENEW_CUE.search(s) and not INCREASE_CUE.search(s) and not has_newness(s):
            return 'AUTH_RENEW'                                    # repair A + C: "New York" no longer blocks this branch
        if INCREASE_CUE.search(s) and (SIZE.search(s) or ANNOUNCE_NOW.search(s) or AUTH_CAPACITY_INCREASE.search(s)):
            return 'AUTH_INCREASE'
        new = has_newness(s)
        if SIZE.search(s) or new:
            if earnings_release and not FRESH.search(s) and not recent_date(s, filed):
                return 'AUTH_WEAK'          # undated authorisation sentence inside an earnings release: may be quarterly boilerplate
            return 'AUTH_NEW'
        return 'AUTH_WEAK'
    if DONE_CUE.search(s) and re.search(r'(program|plan|authorization|buy[\s-]?back)', s, re.I):
        return 'DONE'
    if REPURCHASED_ACTIVITY.search(s) or PERIOD_CUE.search(s):
        return 'ACTIVITY'
    return 'MENTION'


def pass1(rec):
    filed = _filed(rec)
    sents = [s for s in key_sentences(rec) if s.get('hit')]
    if not sents:
        return dict(label='I', margin=3.0, rule='no_repurchase_sentence', evidence='')
    earnings = bool(re.search(r'Results of Operations', rec.get('items') or ''))
    roles = [(sentence_role(s['text'], filed, earnings), s) for s in sents]
    items = (rec.get('items') or '')
    standalone = bool(re.search(r'Other Events|Regulation FD', items)) and not re.search(r'Results of Operations', items)
    lead = ((rec.get('lead_ex') or '')[:500] + ' ' + (rec.get('lead_8k') or '')[:500])
    headline = bool(re.search(r'(announc\w+|authoriz\w+|approv\w+|increas\w+|expand\w+)[^.]{0,90}(repurchase|buy[\s-]?back)', lead, re.I))
    head_announces = bool(HEADLINE_ANNOUNCE.search(lead))          # repair D: the release headline announces a programme
    # an announcement whose size is in the next sentence: "approved a share repurchase program. Under the program up to $50 million ..."
    nxt = {(s['doc'], s['i']): s['text'] for s in key_sentences(rec)}
    upgraded = []
    for r, s in roles:
        follow = nxt.get((s['doc'], s['i'] + 1), '')
        if r == 'AUTH_WEAK' and ANNOUNCE_NOW.search(s['text']) and SIZE.search(follow) and not FOLLOW_PAST.search(follow) and not NOT_OWN_EQUITY.search(follow):
            r = 'AUTH_NEW'
        # repair D: an authorisation sentence demoted by the earnings-release guard is restored when the release
        # headline itself announces the programme, and the sentence is not flagged as old news.
        elif r == 'AUTH_WEAK' and head_announces and not DONE_CUE.search(s['text']) and not RENEW_CUE.search(s['text']) and not HARD_PAST.search(s['text']) and not stale_date(s['text'], filed):
            r = 'AUTH_NEW'
        upgraded.append((r, s))
    roles = upgraded
    count = {}
    for r, _ in roles:
        count[r] = count.get(r, 0) + 1
    first = lambda role: next((s['text'] for r, s in roles if r == role), '')
    n_inc, n_renew = count.get('AUTH_INCREASE', 0), count.get('AUTH_RENEW', 0)
    n_new = count.get('AUTH_NEW', 0)
    if n_inc or n_new:
        margin = min(n_inc + n_new, 3) + (1.0 if headline else 0.0) + (0.5 if standalone else 0.0) - (0.5 if count.get('TENDER') else 0.0) - (0.5 if count.get('PAST_AUTH', 0) > n_inc + n_new else 0.0)
        label = 'B' if n_inc >= n_new and n_inc > 0 else 'A'
        rule = 'auth_increase' if label == 'B' else 'auth_new'
        ev = first('AUTH_INCREASE') if label == 'B' else first('AUTH_NEW')
        return dict(label=label, margin=round(margin, 2), rule=rule, evidence=ev)
    if count.get('TENDER'):
        return dict(label='J', margin=1.0 + (1.0 if re.search(r'tender|dutch', lead, re.I) else 0.0), rule='tender', evidence=first('TENDER'))
    if n_renew:
        return dict(label='C', margin=1.0, rule='auth_renew', evidence=first('AUTH_RENEW'))
    if count.get('AUTH_WEAK'):
        return dict(label='UNCLASSIFIED', margin=0.0, rule='auth_without_size_or_newness', evidence=first('AUTH_WEAK'))
    if count.get('ASR'):
        return dict(label='F', margin=1.0 + (1.0 if ASR.search(lead) else 0.0), rule='asr', evidence=first('ASR'))
    if count.get('DONE'):
        return dict(label='G', margin=1.0, rule='done', evidence=first('DONE'))
    if count.get('ACTIVITY') or count.get('PAST_AUTH'):
        return dict(label='D', margin=1.0 + min(count.get('ACTIVITY', 0), 2) * 0.5, rule='activity_or_past_authorisation', evidence=first('ACTIVITY') or first('PAST_AUTH'))
    if count.get('MENTION'):
        return dict(label='H', margin=1.0, rule='mention_only', evidence=first('MENTION'))
    return dict(label='I', margin=2.0, rule='not_own_equity', evidence=first('NOT_OWN'))


# ---------------------------------------------------------------- pass 2: document-level cue scorer (independent zone and method)
P2_HEADLINE = re.compile(r'(announc\w+|declar\w+|authoriz\w+|approv\w+|increas\w+|expand\w+|adopt\w+|launch\w+|initiat\w+)[^.]{0,100}?(repurchase|buy[\s-]?back)|(repurchase|buy[\s-]?back)[^.]{0,60}?(authoriz\w+|approv\w+|announc\w+|increas\w+|expand\w+)', re.I)
P2_NEAR_AUTH = re.compile(r'(authoriz\w+|approv\w+)[^.]{0,150}?(repurchase|buy[\s-]?back)|(repurchase|buy[\s-]?back)[^.]{0,150}?(authoriz\w+|approv\w+)', re.I)
P2_NEWNESS = re.compile(r'\b(new|additional|increas\w+|expan\w+)\b[^.]{0,100}?(repurchase|buy[\s-]?back)|(repurchase|buy[\s-]?back)[^.]{0,100}?\b(new|additional|increas\w+|expan\w+)\b', re.I)
P2_NOISE = re.compile(r'(warrant|underwrit|over-?allot|notes\s+due|senior\s+notes|preferred\s+stock|private\s+placement|registered\s+direct|tender\s+offer|dutch\s+auction|accelerated\s+share)', re.I)
P2_FINISHED = re.compile(r'(complet\w+|expir\w+|terminat\w+|suspend\w+)[^.]{0,80}?(repurchase|buy[\s-]?back)', re.I)
P2_THRESHOLD = 3.0


def pass2(rec):
    lead_ex, lead_8k = rec.get('lead_ex') or '', rec.get('lead_8k') or ''
    title = lead_ex[:400] + ' ' + lead_8k[:400]
    lead = lead_ex + ' ' + lead_8k
    items = rec.get('items') or ''
    bag = ' '.join(s['text'] for s in key_sentences(rec) if s.get('hit'))
    cues = {}
    title, lead = PLACE_NEW.sub(' ', title), PLACE_NEW.sub(' ', lead)      # repair A applies to pass 2's newness cues too
    cues['headline'] = 3.0 if P2_HEADLINE.search(title) else 0.0
    cues['lead_auth'] = 2.0 if P2_NEAR_AUTH.search(lead) else 0.0
    cues['lead_newness'] = 1.0 if P2_NEWNESS.search(lead) else 0.0
    cues['standalone_item'] = 1.0 if re.search(r'Other Events|Regulation FD', items) and not re.search(r'Results of Operations', items) else 0.0
    n_auth = len(re.findall(r'authoriz|approv', bag, re.I)); n_size = len(SIZE.findall(bag)); n_new = len(re.findall(r'\b(new|additional|increas\w+|expan\w+)\b', bag, re.I))
    n_past = len(re.findall(r'previously|remaining|existing|prior', bag, re.I))
    cues['bag_auth'] = 2.0 if (n_auth and n_size and n_new and n_new + n_auth > n_past) else 0.0
    cues['noise'] = -2.0 if P2_NOISE.search(lead) else 0.0
    cues['finished'] = -2.0 if P2_FINISHED.search(lead) else 0.0
    cues['previously'] = -1.0 if re.search(r'previously\s+(announced|authorized|approved)', lead, re.I) else 0.0
    cues['no_own_repurchase'] = -3.0 if not re.search(r'repurchas|buy[\s-]?back', lead + ' ' + bag, re.I) else 0.0
    score = sum(cues.values())
    return dict(primary=bool(score >= P2_THRESHOLD), score=round(score, 2), cues={k: v for k, v in cues.items() if v})


def classify_frame(df):
    """Run both passes over a corpus DataFrame; pass 2 is computed from the records only (never from pass-1 output)."""
    recs = df.to_dict('records')
    p1 = [pass1(r) for r in recs]; p2 = [pass2(r) for r in recs]
    out = df[['accession', 'cik', 'company', 'filed', 'year', 'form', 'items', 'dev_pool']].copy()
    out['p1_label'] = [x['label'] for x in p1]; out['p1_margin'] = [x['margin'] for x in p1]; out['p1_rule'] = [x['rule'] for x in p1]; out['p1_evidence'] = [x['evidence'][:500] for x in p1]
    out['p1_primary'] = out['p1_label'].isin(['A', 'B'])
    out['p2_primary'] = [x['primary'] for x in p2]; out['p2_score'] = [x['score'] for x in p2]
    return out
