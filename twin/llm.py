import os
from typing import Iterator

import anthropic

from twin import rag
from twin.calcom import public_booking_url
from twin.prompts import build_system_prompt
from twin.tools import TOOL_SCHEMAS, run_tool

CHAT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 2048
MAX_TOOL_ITERATIONS = 5

_client = None


def _anthropic() -> anthropic.Anthropic:
    global _client
    if _client is None:
        # Accept either ANTHROPIC_API_KEY (SDK default) or CLAUDE_API_KEY (common alias)
        key = os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_API_KEY")
        _client = anthropic.Anthropic(api_key=key) if key else anthropic.Anthropic()
    return _client


def respond(user_message: str, history: list[dict]) -> Iterator[str]:
    """Streaming generator: yields the progressively-accumulated reply string as
    Claude produces tokens. Handles the tool-use loop transparently — text from
    every assistant turn (including pre-tool 'let me check…' and post-tool reply)
    accumulates into the same string the UI displays."""
    retrieved = rag.retrieve(user_message, n_results=4)
    system_prompt = build_system_prompt(retrieved)

    messages: list[dict] = _sanitize_history(history)
    messages.append({"role": "user", "content": user_message})

    client = _anthropic()
    accumulated = ""

    for _ in range(MAX_TOOL_ITERATIONS):
        with client.messages.stream(
            model=CHAT_MODEL,
            max_tokens=MAX_TOKENS,
            system=system_prompt,
            tools=TOOL_SCHEMAS,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                accumulated += text
                yield accumulated

            response = stream.get_final_message()

        if response.stop_reason == "end_turn":
            return

        if response.stop_reason != "tool_use":
            accumulated += (
                f"\n\n(Something went off-script — you can book directly at {public_booking_url()}.)"
            )
            yield accumulated
            return

        messages.append({"role": "assistant", "content": response.content})

        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            result_str = run_tool(block.name, dict(block.input or {}))
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result_str,
            })

        messages.append({"role": "user", "content": tool_results})

    accumulated += (
        f"\n\nI hit a snag completing that — try booking directly at {public_booking_url()}."
    )
    yield accumulated


def _sanitize_history(history: list[dict]) -> list[dict]:
    """Convert Gradio chat history into Anthropic message format.

    Gradio 6 passes each turn as {'role': ..., 'content': [{'type': 'text', 'text': '...'}], ...}
    even though its docstring says content is a string. We flatten the content blocks
    to a plain string for Claude, and drop any non-text artifacts."""
    clean = []
    for m in history:
        role = m.get("role")
        if role not in ("user", "assistant"):
            continue
        text = _content_to_text(m.get("content"))
        if text.strip():
            clean.append({"role": role, "content": text})
    return clean


def _content_to_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                parts.append(block.get("text") or "")
        return "".join(parts)
    return ""
