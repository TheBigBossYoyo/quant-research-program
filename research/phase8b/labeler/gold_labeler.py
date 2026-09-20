"""Phase 8B blinded 60-case gold labeler (Amendment 2). Same disk-first engine as labeler_app, different dataset and
label set. Standard library only. Never reads or serves the sealed key file: no prediction, margin, rationale or
stratum can reach the page. Run: python gold_labeler.py (or START_PHASE8B_GOLD_LABELER.bat).
"""
from pathlib import Path
import os
import sys

import labeler_app as la

HERE = Path(__file__).resolve().parent
WORKSPACE = Path(os.environ.get('PHASE8B_GOLD_WORKSPACE', HERE.parent / 'gold')).resolve()
PORT = int(os.environ.get('PHASE8B_GOLD_PORT', '8766'))
LABELS = ['NEW', 'INCREASED', 'RENEWAL', 'ROUTINE', 'ASR', 'COMPLETED_HISTORICAL', 'IRRELEVANT', 'SELF_TENDER', 'AMBIGUOUS']


_ORIGINAL_ROW = la.App.row


def _row_with_snippet(self, key, i):
    """Adds the minimal decisive snippet (computed from the stored passage only; the sealed key is never read)."""
    import gold_snippet
    out = _ORIGINAL_ROW(self, key, i)
    out['snippet'] = gold_snippet.minimal_snippet(out['row'].get('key_passage', ''), out['row'].get('wider_context', ''))
    return out


def configure():
    la.App.row = _row_with_snippet
    la.VALID = list(LABELS)
    la.DATASETS = {'gold': ('phase8b_gold_candidates.csv', 'Gold validation set')}
    la.ID_COL = 'gold_id'
    la.EXTRA_REQUIRED = ('key_passage', 'wider_context')
    la.HTML_PATH = HERE / 'gold_labeler.html'
    la.REPORT_NAME = 'PHASE8B_GOLD_LABELING_INTEGRITY.txt'
    la.BACKUP_EVERY = 20


if __name__ == '__main__':
    configure()
    try:
        la.serve(WORKSPACE, PORT)
    except Exception as exc:
        print(f'\nERROR: {exc}\n', file=sys.stderr)
        input('Press Enter to close...')
        sys.exit(1)
