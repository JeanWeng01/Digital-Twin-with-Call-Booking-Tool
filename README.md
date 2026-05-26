[![GitHub Views](https://img.shields.io/badge/dynamic/json?color=blue&label=Views&query=count&url=https://gist.githubusercontent.com/JeanWeng01/8691f50e3354ad3960be6bf26ac30933/raw/views.json&logo=github)](https://github.com/JeanWeng01/Digital-Twin-with-Call-Booking-Tool)

[![GitHub Clones](https://img.shields.io/badge/dynamic/json?color=success&label=Clone&query=count&url=https://gist.githubusercontent.com/JeanWeng01/31fdbae3181046e7bf32defc5df01a78/raw/clone.json&logo=github)](https://github.com/MShawon/github-clone-count-badge)


# Jean's Digital Twin

A Gradio chatbot that represents Jean Weng. Answers questions about her work in AI engineering (RAG over a small knowledge base) and books 15-minute intro calls onto her Cal.com calendar via Claude tool use.

## Clone this repo

If you have git installed, run this from your projects folder:

```bash
git clone https://github.com/JeanWeng01/Digital-Twin-with-Call-Booking-Tool.git
cd Digital-Twin-with-Call-Booking-Tool
```

## Stack
- **Chat:** Anthropic Claude Sonnet 4.6 (`claude-sonnet-4-6`) with tool use
- **Embeddings:** OpenAI `text-embedding-3-small`
- **Vector store:** ChromaDB (local, persisted to `chroma_db/`)
- **UI:** Gradio `ChatInterface` (Gradio 6.x — messages format)
- **Booking:** Cal.com v2 API
- **Notifications:** Pushover
- **Deploy:** Docker → Railway

## Project layout
```
app.py                  # Gradio entrypoint
twin/
  prompts.py            # System prompt
  rag.py                # Paragraph chunking + Chroma + embeddings
  tools.py              # OpenAI tool schemas + dispatch
  calcom.py             # Cal.com API client (v2)
  llm.py                # OpenAI client + tool-call loop
  convolog.py           # Conversation logger (JSONL)
knowledge_base/
  about_jean.md         # Knowledge base — drop more .md files here
logs/
  conversations.jsonl   # One JSON object per turn (gitignored)
Dockerfile
requirements.txt
.env.example
```

## Local setup

1. **Install deps** (use whichever venv you prefer):
   ```bash
   pip install -r requirements.txt
   ```

2. **Copy env template and fill in values:**
   ```bash
   cp .env.example .env
   # then edit .env
   ```

   Required:
   - `ANTHROPIC_API_KEY` — from console.anthropic.com (used for chat)
   - `OPENAI_API_KEY` — from platform.openai.com (used for embeddings only)
   - `CAL_API_KEY` — from cal.com → Settings → Developer → API Keys
   - `CAL_EVENT_TYPE_ID` — numeric ID from your event-type edit URL
   - `CAL_USERNAME` — your cal.com handle (e.g., `jeanweng`)
   - `CAL_EVENT_SLUG` — your event slug (e.g., `15min`)
   - `PUSHOVER_TOKEN`, `PUSHOVER_USER` — for phone notifications when something noteworthy happens

3. **Run:**
   ```bash
   python app.py
   ```

   First launch builds the Chroma index from `knowledge_base/*.md`. Subsequent launches reuse the persisted DB.

   Open http://localhost:7860 in a browser.

## Updating the knowledge base

Drop new `.md` files into `knowledge_base/`. The bot chunks **by paragraph** (split on blank lines), so structure your docs with clear paragraph breaks — each paragraph becomes one retrievable chunk.

To force a rebuild of the index (after editing existing docs):
```bash
rm -rf chroma_db/
python app.py
```

## Deploy to Railway

1. Push this repo to GitHub.
2. In Railway → New Project → Deploy from GitHub → pick this repo.
3. Railway auto-detects the `Dockerfile` and builds.
4. Add env vars under the service's **Variables** tab (same as `.env`).
5. Under **Settings → Networking**, generate a public domain.

The same `Dockerfile` works unchanged on Render, Fly.io, and Cloud Run.

## Deploy to HuggingFace Spaces (alternative)

Same code, free hosting, with built-in community discoverability — but the free tier sleeps after ~48h inactivity (first visitor pays a ~30s cold start).

1. **Create the Space** at [huggingface.co/new-space](https://huggingface.co/new-space) and choose **Docker** as the SDK.
2. **Add this YAML frontmatter to the VERY TOP of `README.md`** (above the badges, above everything — HF parses it from line 1):
   ```yaml
   ---
   title: Digital Twin
   emoji: 🤖
   colorFrom: blue
   colorTo: purple
   sdk: docker
   app_port: 7860
   pinned: false
   ---
   ```
3. **Push the repo** to the Space's git remote (HF shows you the URL when the Space is created), or use the Space's "Sync from GitHub" option to mirror this repo automatically.
4. **Add secrets** under Space → **Settings → Variables and secrets**. Use the same env var list from [Local setup](#local-setup) above — they're injected into the container as env vars exactly like Railway does.
5. **First build takes ~5 min.** The Space is then live at `https://<your-username>-<space-name>.hf.space`.

Both `app_port: 7860` (in the YAML) and the `PORT` env var (if you set one) must match the port the app actually binds to. If you don't set `PORT` anywhere, the app defaults to 7860 and the YAML stays as-is.

## How the booking flow works

1. Visitor expresses interest in talking → bot decides to invoke tools.
2. Bot calls `list_available_slots(timezone)` → Cal.com API returns open 15-min slots.
3. Bot shows 3-5 options in chat, asks visitor to pick one + confirms name/email.
4. Bot calls `create_booking(start_iso, name, email, timezone, topic)`.
5. Cal.com sends the visitor a calendar invite + the meeting link, and emails Jean.

> **Want a different meeting tool?** The video platform (Google Meet, Zoom, Cal Video, Microsoft Teams, in-person, phone, etc.) is set per event type in Cal.com's UI under **Event Types → [your event] → Location**. Change it there and the next booking the bot creates will use the new option — no code change needed on this side.

## Notes on behavior

- The bot is instructed to warm up the conversation before suggesting a call (no first-turn pitches).
- If the booking API fails, the bot falls back to offering `cal.com/<username>/<slug>` as a manual link.
- The tool-call loop is capped at 5 iterations per turn to prevent infinite loops.

## Conversation logs

Every turn (user message + bot reply) is appended as one JSON object to `logs/conversations.jsonl`. Each line:
```json
{"timestamp": "...UTC ISO...", "session_id": "<gradio_session_hash>", "user": "...", "bot": "..."}
```

Read them later with:
```bash
# pretty-print all turns
cat logs/conversations.jsonl | jq

# only one session
cat logs/conversations.jsonl | jq 'select(.session_id == "abc123")'
```

**On Railway:** the container filesystem is ephemeral — logs reset on each redeploy. If you want durable logs, attach a Railway volume mounted at `/app/logs` (or swap `convolog.py` to write to S3/Postgres later).
