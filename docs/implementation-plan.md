# OW Patch Impact Tracker — Implementation Plan

## Stack and free-tier setup

- **Language:** Python 3, with pandas for analysis and pytest for tests.
- **Database:** PostgreSQL running locally in Docker (SQLite is fine to start).
- **LLM:** one free provider behind a small wrapper, `llm.extract(text, schema) -> dict`. Start with the Gemini API free tier or Groq's free tier; Ollama with a local model is the fully offline fallback. Check each provider's current free-tier limits before you start, since they change.
- **Why the wrapper:** switching providers (or moving to Claude later) is one config change, and it's a clean design point for interviews.
- **Build with:** Claude Code on your Pro plan as the coding assistant. You write and understand the core logic (schema, validation, analysis); Claude helps with boilerplate and review.

## Repo layout

```
ow-patch-impact/
  config.example.toml   # provider, keys, paths, thresholds
  patchimpact/
    llm.py              # provider wrapper (gemini | groq | ollama)
    schema.py           # change-record schema + validation rules
    ingest_patches.py   # fetch/paste notes -> patches table
    extract.py          # LLM extraction -> validate -> changes / review_queue
    ingest_ranked.py    # phase 2
    ingest_pro.py       # phase 3
    analyze.py          # deltas, backtests, forecasts (phase 4)
    report.py           # grounded report + number checker
    cli.py              # history / patch / report commands
  data/labels/          # hand-labeled patches (ground truth)
  tests/
  docker-compose.yml
  README.md
```

## Phases

1. **Phase 0, Setup (an evening):** repo, Docker Postgres, config file, and the `llm.py` wrapper with one working provider. *Done when:* a test prompt returns valid JSON through the wrapper.
2. **Phase 1a, Ground truth first (a weekend):** paste 3-5 recent patches into the `patches` table and hand-label every change into `data/labels/`. Do this before writing the extractor, so you know what correct looks like (the same habit as writing success criteria at Fleet).
3. **Phase 1b, Extraction and validation (1-2 weekends):** write the schema, prompt, and validation rules; route bad records to `review_queue`; build `history` and `patch` CLI commands. *Done when:* field-level accuracy on your labels is 95% or higher and the validator catches planted bad records. Ship this phase: README, sample output, and the accuracy table.
4. **Phase 2, Ranked stats (a weekend):** confirm what Blizzard's hero statistics cover, then load or begin snapshotting them per patch. *Done when:* each change in the database links to before/after pick and win rates.
5. **Phase 3, Pro stats (a weekend):** check Liquipedia's API terms, then load OWCS picks and bans per patch window, with attribution. *Done when:* pro and ranked usage can be compared side by side per hero.
6. **Phase 4, Analysis (1-2 weekends):** compute deltas, find pro-vs-ladder divergences, and write the rule-based direction forecast. Backtest on past patches only (never test on data the rules were tuned on). *Done when:* the hit rate is reported against the baseline, with sample sizes.
7. **Phase 5, Grounded reports (a weekend):** the LLM writes a patch summary from computed stats; `report.py` extracts every number and hero name from the text and checks each one against the database. *Done when:* reports pass the checker and a planted wrong number fails it.

## Testing and evaluation

- **Unit tests (pytest):** schema validation rules, direction-vs-numbers consistency, the report number-checker, and delta calculations, using fixed sample data with no LLM calls.
- **Extraction eval:** a script compares extracted records to `data/labels/` and prints field-level precision and recall per patch; rerun it whenever the prompt or model changes.
- **Planted failures:** seed bad records and a report with a wrong number to prove the validator and checker catch them.
- **Backtest discipline:** freeze the forecast rules before scoring them on held-out patches; log every forecast with its outcome in the `forecasts` table.
- **Provider comparison (optional):** run the same eval on two free providers and record which is more accurate. That's a great README table.

## Resume and interview angle

Only add these bullets once each phase is actually built and measured; fill in your real numbers.

- *Phase 1:* "Built an LLM pipeline that extracts structured balance changes from Overwatch patch notes, validates them against schema and consistency rules, and achieved \[X\]% field-level accuracy on hand-labeled patches."
- *Phase 4:* "Linked \[N\] patch changes to ranked and OWCS pro usage data; backtested a direction forecast with a \[X\]% hit rate versus a \[Y\]% baseline."
- *Talking points:* ground truth before code; why validation beats trusting model output; the provider wrapper; small samples and confounders, and how you reported results honestly.

This project directly fills the "hands-on LLM API experience" gap from Monti, Taxfyle, and AIVista, and its data side fits your KSU Data Science concentration.
