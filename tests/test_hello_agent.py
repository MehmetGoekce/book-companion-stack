"""Smoke tests for hello_agent.py.

Run without the real ``anthropic`` SDK and without an API key by injecting
a fake ``anthropic`` module into ``sys.modules`` before the script executes.

Two kinds of checks:

* Configuration snapshot: the request the script sends (model, limits,
  prompts). These break on purpose when the book's listing changes.
* Behaviour: the script prints only text blocks, stops on a refusal, and
  flags a truncated answer.

Works both under pytest (``pytest test_hello_agent.py``) and standalone
(``python test_hello_agent.py``).
"""

from __future__ import annotations

import contextlib
import io
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

# The model id printed in Chapter 1.6. Change both together.
BOOK_MODEL = "claude-sonnet-5-5"


def _block(kind: str, **fields: Any) -> types.SimpleNamespace:
    return types.SimpleNamespace(type=kind, **fields)


def _install_fake_anthropic(content: list[Any], stop_reason: str) -> MagicMock:
    """Replace the ``anthropic`` import with a recording mock and return the client."""
    fake_module = types.ModuleType("anthropic")
    fake_client = MagicMock(name="AnthropicClient")
    fake_client.messages.create.return_value = types.SimpleNamespace(
        content=content, stop_reason=stop_reason
    )
    fake_module.Anthropic = MagicMock(return_value=fake_client)  # type: ignore[attr-defined]
    sys.modules["anthropic"] = fake_module
    return fake_client


def _run_script(
    content: list[Any] | None = None, stop_reason: str = "end_turn"
) -> tuple[MagicMock, str, int | str | None]:
    """Run the script; return the mock client, captured stdout and the exit code (None = no exit)."""
    if content is None:
        content = [_block("text", text="<mocked completion>")]
    fake_client = _install_fake_anthropic(content, stop_reason)
    out = io.StringIO()
    exit_code: int | str | None = None
    with contextlib.redirect_stdout(out):
        try:
            runpy.run_path(str(SCRIPT), run_name="__main__")
        except SystemExit as exc:
            exit_code = exc.code
    return fake_client, out.getvalue(), exit_code


def _call_kwargs(fake_client: MagicMock) -> dict[str, Any]:
    create = fake_client.messages.create
    assert create.call_count == 1, f"expected exactly one .messages.create call, got {create.call_count}"
    return create.call_args.kwargs


# --- configuration snapshot -------------------------------------------------


def test_snapshot_model_matches_book_listing() -> None:
    kwargs = _call_kwargs(_run_script()[0])
    assert kwargs["model"] == BOOK_MODEL, (
        f"hello_agent.py and the Chapter 1.6 listing must use {BOOK_MODEL!r}; got {kwargs['model']!r}"
    )


def test_snapshot_caps_response_length() -> None:
    kwargs = _call_kwargs(_run_script()[0])
    assert kwargs["max_tokens"] == 4096


def test_snapshot_system_prompt_frames_a_shopping_assistant() -> None:
    system = _call_kwargs(_run_script()[0])["system"].lower()
    assert "shopping assistant" in system
    assert "outdoor" in system, "Ch 1 example uses an outdoor-sports store framing"


def test_snapshot_user_message_asks_about_products() -> None:
    messages = _call_kwargs(_run_script()[0])["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert "trail running" in messages[0]["content"].lower()


# --- behaviour ---------------------------------------------------------------


def test_prints_text_even_when_a_thinking_block_comes_first() -> None:
    content = [_block("thinking", thinking=""), _block("text", text="Try the Speedcross.")]
    _, out, exit_code = _run_script(content)
    assert exit_code is None
    assert "Try the Speedcross." in out


def test_stops_with_a_message_on_refusal() -> None:
    _, out, exit_code = _run_script(content=[], stop_reason="refusal")
    assert exit_code == "The model declined this request."
    assert out == ""


def test_flags_a_truncated_answer() -> None:
    _, out, exit_code = _run_script(stop_reason="max_tokens")
    assert exit_code is None
    assert "<mocked completion>" in out
    assert "cut off at max_tokens" in out


if __name__ == "__main__":
    tests = [obj for name, obj in sorted(globals().items()) if name.startswith("test_") and callable(obj)]
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
