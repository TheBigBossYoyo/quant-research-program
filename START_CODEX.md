# Codex launch prompt

Work autonomously on the quantitative-trading research project in this repository.

First read every applicable `AGENTS.md` / `AGENTS.override.md`, then read `QUANT_RESEARCH_PROTOCOL_CODEX.md` in full. If they exist, also read `STATUS.md`, `EXPERIMENTS.md`, and `RESEARCH_JOURNAL.md` before making substantive changes.

Then execute the `INITIAL CODEX ACTION` from the protocol.

Important operating requirements:

- Do not give me a long plan and stop. Perform the work with the tools available in this Codex environment.
- Inspect and preserve existing repository work before creating replacements.
- Use empirical tests to resolve research choices whenever possible.
- Verify current Binance and Trading 212 constraints rather than relying on memory.
- If web search is available, use it for current documentation. If shell/network access needed for legitimate package installation, API queries, or dataset downloads is blocked by the sandbox, request the minimum required approval.
- Do not fabricate current fees, API capabilities, datasets, test results, fills, or broker constraints.
- Track failed as well as successful experiments.
- Keep the final untouched test set untouched until the strategy architecture is frozen.
- No live trading. Do not submit real orders, enable live mode, or expose real capital unless I explicitly authorize that separate step later.
- Keep `STATUS.md`, `EXPERIMENTS.md`, and `RESEARCH_JOURNAL.md` current so another Codex session can resume from disk.
- Continue autonomously through the highest-value executable research steps until you reach a genuine blocker, a permission requirement, a human capital-exposure decision, or there is no further useful work executable in the current run.

At major checkpoints, report only concise evidence-based status. The repository files are the durable source of truth.

Begin now.
