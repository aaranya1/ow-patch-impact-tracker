"""Provider wrapper: extract(text, schema) -> dict.

Callers never import a provider SDK directly; switching providers is a config change.
The wrapper only guarantees parseable JSON. Checking the result against the schema and
the consistency rules is schema.py's job, so validation never trusts the model.
"""

import json
import os

from patchimpact.config import load_config


class LLMError(RuntimeError):
    """The provider failed or returned something that isn't JSON."""


def extract(text: str, schema: dict, *, instructions: str = "", config: dict | None = None) -> dict:
    """Ask the configured provider for JSON matching `schema` (a JSON Schema dict)."""
    llm_cfg = (config or load_config())["llm"]
    provider = llm_cfg["provider"]
    if provider not in PROVIDERS:
        raise LLMError(f"unknown provider {provider!r}; expected one of {sorted(PROVIDERS)}")
    raw = PROVIDERS[provider](text, schema, instructions, llm_cfg)
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise LLMError(f"{provider} returned invalid JSON: {e}\n---\n{raw[:500]}") from e


def _gemini(text: str, schema: dict, instructions: str, llm_cfg: dict) -> str:
    from google import genai
    from google.genai import errors, types

    cfg = llm_cfg["gemini"]
    api_key = os.environ.get(cfg["api_key_env"])
    if not api_key:
        raise LLMError(f"set the {cfg['api_key_env']} environment variable")

    client = genai.Client(api_key=api_key)
    try:
        resp = client.models.generate_content(
            model=cfg["model"],
            contents=text,
            config=types.GenerateContentConfig(
                system_instruction=instructions or None,
                temperature=llm_cfg.get("temperature", 0.0),
                response_mime_type="application/json",
                response_json_schema=schema,
            ),
        )
    except errors.APIError as e:
        raise LLMError(f"gemini API error: {e}") from e
    if not resp.text:
        raise LLMError(f"gemini returned no text (finish reason: {resp.candidates and resp.candidates[0].finish_reason})")
    return resp.text


def _not_yet(name: str):
    def call(*_args):
        raise LLMError(f"{name} provider not implemented yet")
    return call


PROVIDERS = {
    "gemini": _gemini,
    "groq": _not_yet("groq"),
    "ollama": _not_yet("ollama"),
}
