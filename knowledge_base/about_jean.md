# About Jean

Jean Weng is an AI engineer focused on building production-ready LLM applications. She works at the intersection of conversational AI, retrieval-augmented generation, and tool-using agents — translating cutting-edge model capabilities into systems that solve real problems for real users.

## Background

Jean came to AI engineering after years working across data, software, and product. That cross-disciplinary path shapes how she thinks about LLM systems: not as model demos, but as products with users, latency budgets, error modes, and evolving requirements. She gravitates toward problems where the hardest part isn't the model — it's the system around it.

## What she's working on

She's building a digital twin: a chatbot that represents her, answers questions about her work, and books meetings with people who want to talk further. The project is a working example of the patterns she cares about — RAG over a small, curated knowledge base; tool-calling for real-world side effects (calendar booking); and a system prompt that shapes tone rather than scripts replies. It runs in Docker and deploys to Railway. The stack: OpenAI for both chat and embeddings, ChromaDB for vector storage, Gradio for the UI, Cal.com for booking.

## How she works

Jean prefers shipping a working end-to-end system first, then improving each layer. She believes RAG quality lives or dies at the chunking and retrieval layer, not the model. She thinks tool-calling is where most production LLM value lives in 2026, and that the interesting design work is in the tools themselves — their granularity, their failure modes, and how they're surfaced to the model. She's opinionated about keeping prompts short, code readable, and abstractions minimal until they earn their place.

## What she's interested in talking about

If you're building an LLM-powered product, agent system, or RAG pipeline and want a second opinion on architecture, evaluation, or deployment — she's happy to chat. She's especially interested in conversations about: when to use tool-calling vs. structured outputs; how to evaluate retrieval quality without ground truth; how to keep agents predictable as you add more tools; and how to ship LLM features that hold up under real user traffic.

## How to reach her

The easiest way to talk to Jean is to book a 15-minute intro call through this chatbot. Just say you'd like to book, and the bot will confirm your availability, book for you, and send you the confirmation and meeting link!

---

*This is a placeholder bio. Replace this file with your real content — the bot will rebuild its knowledge base from any .md files dropped into the `knowledge_base/` folder on next launch (delete `chroma_db/` to force a rebuild).*
