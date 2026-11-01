import os

import pytest

from patchimpact import llm
from patchimpact.cli import SMOKE_SCHEMA, SMOKE_TEXT
from patchimpact.config import load_config


def cfg(provider="gemini"):
    c = load_config()
    c["llm"]["provider"] = provider
    return c


def test_parses_provider_json(monkeypatch):
    monkeypatch.setitem(llm.PROVIDERS, "gemini", lambda *a: '{"hero": "Kiriko"}')
    assert llm.extract("x", {}, config=cfg()) == {"hero": "Kiriko"}


def test_invalid_json_raises(monkeypatch):
    monkeypatch.setitem(llm.PROVIDERS, "gemini", lambda *a: "not json")
    with pytest.raises(llm.LLMError, match="invalid JSON"):
        llm.extract("x", {}, config=cfg())


def test_unknown_provider_raises():
    with pytest.raises(llm.LLMError, match="unknown provider"):
        llm.extract("x", {}, config=cfg("nope"))


def test_missing_api_key_raises(monkeypatch):
    c = cfg()
    c["llm"]["gemini"]["api_key_env"] = "PATCHIMPACT_TEST_UNSET_KEY"
    monkeypatch.delenv("PATCHIMPACT_TEST_UNSET_KEY", raising=False)
    with pytest.raises(llm.LLMError, match="PATCHIMPACT_TEST_UNSET_KEY"):
        llm.extract("x", {}, config=c)


@pytest.mark.live
@pytest.mark.skipif(not os.environ.get("GEMINI_API_KEY"), reason="GEMINI_API_KEY not set")
def test_gemini_live():
    result = llm.extract(SMOKE_TEXT, SMOKE_SCHEMA, instructions="Extract the balance change as JSON.")
    assert result["old_value"] == 40 and result["new_value"] == 45
    assert result["direction"] == "buff"
