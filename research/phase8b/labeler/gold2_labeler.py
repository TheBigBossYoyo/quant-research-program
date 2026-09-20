"""Phase 8B Amendment 3: labeler for the FRESH 15-case blind validation set.

Differs from the Amendment 2 gold labeler in exactly one respect, which is the whole point of the repair: the default
visible text is the passage stored with the case, which phase8b_display built around the classifier's own evidence
sentence (that sentence plus one neighbour each side). Nothing is re-ranked, scored or dropped at display time, so the
labeller can never be scored against evidence that was hidden from them (Amendment 3 A3.4).

The human stays blind to the prediction: the sealed key is never read or served, and the human CSV carries no label,
margin, rule, stratum or score (verified by `phase8b_gold2.py preflight`).

Run: python gold2_labeler.py   (or START_PHASE8B_FRESH_LABELER.bat)
"""
from pathlib import Path
import os
import sys

import labeler_app as la

HERE = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get('PHASE8B_GOLD2_WORKSPACE', HERE.parent / 'gold2')).resolve()
PORT = int(os.environ.get('PHASE8B_GOLD2_PORT', '8767'))
LABELS = ['NEW', 'INCREASED', 'RENEWAL', 'ROUTINE', 'ASR', 'COMPLETED_HISTORICAL', 'IRRELEVANT', 'SELF_TENDER', 'AMBIGUOUS']

_ORIGINAL_ROW = la.App.row


def _row_with_passage(self, key, i):
    """The stored evidence-anchored passage is the default visible text. No ranking, no selection, no model output."""
    out = _ORIGINAL_ROW(self, key, i)
    passage = (out['row'].get('key_passage') or '').strip()
    out['snippet'] = dict(sentences=[passage] if passage else [], anchored=True, added_for_ambiguity=False)
    return out


def configure():
    la.App.row = _row_with_passage
    la.VALID = list(LABELS)
    la.DATASETS = {'gold2': ('phase8b_gold2_candidates.csv', 'Fresh validation set (15 cases)')}
    la.ID_COL = 'gold2_id'
    la.EXTRA_REQUIRED = ('key_passage', 'wider_context')
    la.HTML_PATH = HERE / 'gold2_labeler.html'
    la.REPORT_NAME = 'PHASE8B_GOLD2_LABELING_INTEGRITY.txt'
    la.BACKUP_EVERY = 5


if __name__ == '__main__':
    configure()
    try:
        la.serve(WORKSPACE, PORT)
    except Exception as exc:
        print(f'\nERROR: {exc}\n', file=sys.stderr)
        input('Press Enter to close...')
        sys.exit(1)
