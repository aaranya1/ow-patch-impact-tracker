# OW Patch Impact Tracker

Turns Overwatch patch notes into structured, validated change records, then measures how each change shows up in ranked and OWCS pro play, and tests whether the direction of those shifts can be forecast. Built entirely on free tiers.

**Status:** Phase 0 (setup) — LLM wrapper with Gemini, local Postgres.

## Setup

```sh
python -m venv .venv
.venv\Scripts\activate            # Windows; use source .venv/bin/activate elsewhere
pip install -e ".[dev]"
cp config.example.toml config.toml
docker compose up -d --wait       # Postgres on localhost:5432
```

Get a free Gemini API key at https://aistudio.google.com/apikey and put it in a `.env` file at the repo root (gitignored) as `GEMINI_API_KEY=...`, or set it as an environment variable.

```sh
patchimpact smoke                 # sends a test patch line through the wrapper, prints JSON
pytest                            # offline tests
pytest -m live                    # also hits the real Gemini API
```

## Docs

- [PRD](docs/PRD.md)
- [Implementation plan](docs/implementation-plan.md)
