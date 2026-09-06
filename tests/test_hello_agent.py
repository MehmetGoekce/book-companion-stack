"""Smoke test for hello_agent.py.

Runs without the real ``anthropic`` SDK and without an API key by
injecting a fake ``anthropic`` module into ``sys.modules`` before the
script executes. Verifies the shape of the call the reader's first
agent makes to the LLM.

Works both under pytest (``pytest test_hello_agent.py``) and standalone
(``python test_hello_agent.py``).
"""

from __future__ import annotations

import runpy
import sys
import types
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

_HERE = Path(__file__).resolve().parent
# Same file works in the book's flat ``code/`` folder and in the companion
# repo's ``scripts/`` + ``tests/`` layout.
SCRIPT = next(
    p for p in (_HERE / "hello_agent.py", _HERE.parent / "scripts" / "hello_agent.py") if p.exists()
)


def _install_fake_anthropic() -> MagicMock:
    """Replace the ``anthropic`` import with a recording mock.

    Returns the mock client instance the script will receive so the
    test can assert on call args.
    """
    fake_module = types.ModuleType("anthropic")
    fake_client = MagicMock(name="AnthropicClient")
    fake_response = MagicMock(name="Response")
    fake_response.content = [types.SimpleNamespace(text="<mocked completion>")]
    fake_client.messages.create.return_value = fake_response
    fake_module.Anthropic = MagicMock(return_value=fake_client)  # type: ignore[attr-defined]
    sys.modules["anthropic"] = fake_module
    return fake_client


def _run_script() -> MagicMock:
    fake_client = _install_fake_anthropic()
    runpy.run_path(str(SCRIPT), run_name="__main__")
    return fake_client


def _call_kwargs(fake_client: MagicMock) -> dict[str, Any]:
    create = fake_client.messages.create
    assert create.call_count == 1, f"expected exactly one .messages.create call, got {create.call_count}"
    return create.call_args.kwargs


def test_uses_current_sonnet_model() -> None:
    kwargs = _call_kwargs(_run_script())
    assert kwargs["model"] == "claude-sonnet-5", (
        f"hello_agent.py must pin the current Sonnet generation; got {kwargs['model']!r}"
    )


def test_caps_response_length() -> None:
    kwargs = _call_kwargs(_run_script())
    assert kwargs["max_tokens"] == 1024


def test_system_prompt_frames_a_shopping_assistant() -> None:
    kwargs = _call_kwargs(_run_script())
    system = kwargs["system"]
    assert "shopping assistant" in system.lower()
    assert "outdoor" in system.lower(), "Ch 1 example uses an outdoor-sports store framing"


def test_user_message_asks_about_products() -> None:
    kwargs = _call_kwargs(_run_script())
    messages = kwargs["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert "trail running" in messages[0]["content"].lower()


if __name__ == "__main__":
    tests = [
        test_uses_current_sonnet_model,
        test_caps_response_length,
        test_system_prompt_frames_a_shopping_assistant,
        test_user_message_asks_about_products,
    ]
    failures: list[str] = []
    for fn in tests:
        try:
            fn()
        except AssertionError as exc:
            failures.append(f"FAIL {fn.__name__}: {exc}")
        else:
            print(f"PASS {fn.__name__}")
    if failures:
        for line in failures:
            print(line)
        sys.exit(1)
    print(f"\n{len(tests)}/{len(tests)} tests passed")
