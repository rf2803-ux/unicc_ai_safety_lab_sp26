from __future__ import annotations

import os

import pytest

from ai_safety_lab.clients import ClaudeClient, GeminiClient, LlamaClient, OpenAIClient


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY missing")
def test_openai_client_requires_runtime_only_when_key_present() -> None:
    client = OpenAIClient(model="gpt-4.1-mini")
    assert client.model == "gpt-4.1-mini"


@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="ANTHROPIC_API_KEY missing")
def test_claude_client_requires_runtime_only_when_key_present() -> None:
    client = ClaudeClient(model="claude-3-7-sonnet-latest")
    assert client.model == "claude-3-7-sonnet-latest"


@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY missing")
def test_gemini_client_requires_runtime_only_when_key_present() -> None:
    client = GeminiClient(model="gemini-2.0-flash")
    assert client.model == "gemini-2.0-flash"


def test_llama_client_is_placeholder() -> None:
    client = LlamaClient(model="llama-placeholder")
    with pytest.raises(NotImplementedError):
        client.generate_text("system", "user")
