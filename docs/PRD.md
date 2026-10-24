# OW Patch Impact Tracker — PRD

A tool that turns Overwatch patch notes into structured, validated data, then measures how each change shows up in ranked and OWCS pro play, and tests whether the direction of those shifts can be forecast. Built entirely on free tiers.

## Goals

- **Phase 1, Extraction (standalone deliverable):** turn any patch's notes into structured, validated change records (hero, ability, stat, old value, new value, buff/nerf) stored in SQL, with measured accuracy.
- **Phase 2, Ranked outcomes:** attach hero pick rate and win rate per patch, so every change has a before and after.
- **Phase 3, Pro outcomes:** attach OWCS hero picks and bans per patch window, so pro and ladder trends can be compared.
- **Phase 4, Analysis and forecasting:** measure how often changes move usage in the expected direction, flag where pros and ranked players disagree, and forecast pick-rate direction before a patch lands, backtested on past patches.
- **Throughout:** grounded, readable patch reports in which every number is verified against the database.

## Non-goals (v1)

- No claim to "predict the meta." The forecast is the direction of pick-rate change, reported with its measured hit rate and caveats.
- No machine-learning model until simple rules have been tried and measured; small data first.
- No video or VOD analysis; text and tabular data only.
- No scraping that breaks a source's terms; if data isn't available legitimately, the phase shrinks.
- No paid APIs or hosting; everything runs on free tiers or locally.

## Functional requirements

1. **Ingest patch notes:** fetch or paste a patch's notes; store the raw text with patch ID, release date, and source URL.
2. **Extract changes:** the LLM returns JSON matching a fixed schema (hero, ability, stat, old value, new value, unit, direction, note), one record per change.
3. **Validate before storing:** reject or flag records with unknown heroes, missing values, or a direction that contradicts the numbers (for example, labeled a buff but the damage went down). Flagged records go to a review queue, not the database.
4. **Query changes:** CLI commands such as `history kiriko` or `patch 2026-10-15` show changes over time.
5. **Ingest outcomes (phases 2-3):** load per-patch ranked hero stats and OWCS picks and bans into their own tables, keyed by patch window.
6. **Analyze and forecast (phase 4):** compute before/after usage deltas per change; run a rule-based direction forecast; backtest it on past patches and report the hit rate.
7. **Grounded patch report:** the LLM writes a short summary from computed stats only; a checker confirms every number and hero name in the text exists in the database, and fails the report if not.
8. **Config, not hardcoding:** model provider, API keys, data paths, and thresholds live in a config file or CLI arguments.

## Data model

| Table | Key fields | Filled in |
| --- | --- | --- |
| patches | patch\_id, release\_date, source\_url, raw\_text | Phase 1 |
| heroes | hero\_id, name, role (tank/damage/support), release\_date | Phase 1 |
| changes | change\_id, patch\_id, hero\_id, ability, stat, old\_value, new\_value, unit, direction, validated | Phase 1 |
| review\_queue | change JSON, reason flagged, resolved | Phase 1 |
| ranked\_stats | patch\_id, hero\_id, rank\_tier, region, pick\_rate, win\_rate | Phase 2 |
| pro\_stats | patch\_id, hero\_id, event, matches, picks, bans | Phase 3 |
| forecasts | patch\_id, hero\_id, predicted\_direction, actual\_direction, correct | Phase 4 |

## Data sources and risks

Check each source before starting the phase that needs it.

- **Patch notes (phase 1):** Blizzard's official patch notes pages. Low risk; pasting the text by hand is a fine fallback.
- **Ranked stats (phase 2):** Blizzard publishes official hero statistics on the Overwatch site. To verify: which ranks and regions are covered, how far back history goes, and whether past patches can be retrieved or have to be snapshotted going forward.
- **Pro stats (phase 3):** Liquipedia is the likely source for OWCS picks and bans. To verify: its API terms, rate limits, and attribution requirements (CC BY-SA). Never scrape against the terms.
- **Small samples:** only a handful of patches per season and limited pro matches per patch. Report trends with counts, not certainties.
- **Confounders:** new heroes, map pool changes, bans, and pro teams copying each other all shift usage independently of patch notes. Tag patches that include these and note them in the analysis.
- **Fallback:** if ranked history can't be retrieved, start snapshotting stats now and build the history forward. Phase 1 stays fully useful on its own.

## Success criteria

- **Phase 1:** at least 95% field-level accuracy on 3 or more hand-labeled patches; every invalid record caught by validation rather than stored.
- **Phase 2-3:** stats loaded for at least 5 patch windows, with each change linked to its before/after usage.
- **Phase 4:** the direction forecast's hit rate is reported against a simple baseline (for example, "buffed heroes go up"), using only past patches, with sample sizes stated.
- **Reports:** zero unverified numbers; the grounding checker passes on every generated report.
- **Cost:** $0 to build and run.
