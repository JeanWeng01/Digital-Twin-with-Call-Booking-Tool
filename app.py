import os

import gradio as gr
from dotenv import load_dotenv

from twin import rag
from twin.convolog import log_turn
from twin.llm import respond

load_dotenv(override=True)

REQUIRED_ENV = ["OPENAI_API_KEY", "CAL_API_KEY", "CAL_EVENT_TYPE_ID"]


def _check_env() -> None:
    missing = [k for k in REQUIRED_ENV if not os.getenv(k)]
    if missing:
        raise RuntimeError(
            f"Missing required env vars: {', '.join(missing)}. "
            "Copy .env.example to .env and fill in the values."
        )


def chat_fn(message: str, history: list[dict], request: gr.Request):
    session_id = getattr(request, "session_hash", None) or "unknown"
    final_reply = ""
    for partial in respond(message, history):
        final_reply = partial
        yield partial
    log_turn(session_id, message, final_reply)


def build_ui() -> gr.ChatInterface:
    return gr.ChatInterface(
        fn=chat_fn,
        title="Chat with Jean's Digital Twin",
        description=(
            "Hi — I'm a chatbot that represents Jean Weng. Ask me about her work in AI engineering."
        ),
        chatbot=gr.Chatbot(
            placeholder="Ready and listening — say hi 👋",
            height=480,
        ),
    )


if __name__ == "__main__":
    _check_env()
    indexed = rag.build_index()
    print(f"[startup] Knowledge base indexed: {indexed} chunks in '{rag.COLLECTION_NAME}'")

    ui = build_ui()
    ui.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", 7860)),
    )
