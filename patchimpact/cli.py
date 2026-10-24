"""patchimpact CLI. Phase 0 has one command: `smoke`, a live check that the LLM wrapper returns JSON."""

import argparse
import json

from patchimpact import llm

SMOKE_SCHEMA = {
    "type": "object",
    "properties": {
        "hero": {"type": "string"},
        "stat": {"type": "string"},
        "old_value": {"type": "number"},
        "new_value": {"type": "number"},
        "direction": {"type": "string", "enum": ["buff", "nerf", "neutral"]},
    },
    "required": ["hero", "stat", "old_value", "new_value", "direction"],
}

SMOKE_TEXT = "Kiriko - Kunai: damage increased from 40 to 45."


def smoke(_args) -> None:
    result = llm.extract(SMOKE_TEXT, SMOKE_SCHEMA, instructions="Extract the balance change as JSON.")
    print(json.dumps(result, indent=2))


def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="patchimpact")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("smoke", help="send a test prompt through the LLM wrapper").set_defaults(func=smoke)
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
