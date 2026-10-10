# Agency Brain

Agency Brain is a prototype knowledge assistant for marketing agency teams. It uses brand guidelines and campaign notes to answer questions and review draft captions against brand rules.

## What it does

- Loads approved brand knowledge rows from a published CSV source (configured with `SHEET_CSV_URL`).
- Splits and embeds that content with Google's Gemini embedding model, then stores the local vector index in `index.json`.
- Retrieves brand-specific context for questions and generates answers with source references.
- Checks captions against hard and soft brand rules and can suggest a corrected version.
- Provides a Streamlit interface and a FastAPI service with ask, caption-check, refresh, rule-structuring, and message-understanding endpoints.
- Includes a message-intent helper that recognizes ask, check, rule, and chat intents and keeps short per-chat context.

## Architecture

```text
Approved CSV rows
      |
      v
chunker.py -> build_index.py -> index.json (local embeddings)
                                      |
                 +--------------------+--------------------+
                 v                                         v
          Streamlit app                              FastAPI service
       ask / caption check               ask / check / refresh / structure / understand
                 \                                         /
                  +------ Gemini embeddings and text generation
```

The n8n workflow export is included below. It connects Telegram messages to the API and Google Sheets approval flow.

## Telegram and n8n workflow

A sanitized n8n workflow export is included at [`n8n/agency-brain-telegram.example.json`](n8n/agency-brain-telegram.example.json). It receives Telegram messages, checks an allowed-user list, asks the API to classify the message, and routes it to brand Q&A, caption review, or a rule-submission path. Proposed rules are structured, saved as pending in Google Sheets, and sent for Telegram approval; approval updates the sheet and calls the API to refresh its index.

Before using the imported workflow:

1. Import the JSON file into your n8n instance.
2. Reconnect your own Telegram and Google Sheets credentials to the relevant nodes. The exported credential references were removed.
3. Replace `YOUR_GOOGLE_SHEET_ID` in each Google Sheets node with a spreadsheet you control. The sheet should have the fields used by the workflow: `brand`, `category`, `title`, `content`, `status`, `added_on`, and `id`.
4. In the **Allowed user?** node, replace `REPLACE_WITH_YOUR_TELEGRAM_USER_ID` with the Telegram numeric user ID(s) allowed to use the bot. The workflow denies access until configured.
5. Confirm the API URLs in the HTTP Request nodes. They use `http://127.0.0.1:8000`; change the host if n8n runs on a different machine or container from the FastAPI service.
6. Test the workflow with non-sensitive sample data, then activate it in n8n.

The included workflow is inactive and contains placeholders for account-specific values. Do not commit live credentials, a real Telegram user ID, or a private Google Sheet ID.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key
- A CSV URL containing approved knowledge rows with the columns `status`, `brand`, `category`, `title`, and `content`

Install the Python packages:

```bash
python -m venv venv
# Activate the environment for your operating system, then:
pip install -r requirements.txt
```

Create a `.env` file in the project root using `.env.example`:

```dotenv
GEMINI_API_KEY=your_api_key_here
SHEET_CSV_URL=https://example.com/approved-knowledge.csv
```

Build the local embedding index:

```bash
python build_index.py
```

Run the Streamlit app:

```bash
streamlit run app.py
```

Run the FastAPI service:

```bash
uvicorn api:app --reload
```

The index is generated locally and intentionally excluded from Git. Build it from an approved, non-confidential sample knowledge source before running the application.

## API endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Check that the API process is running |
| `POST` | `/ask` | Ask a question about a brand |
| `POST` | `/check` | Check a caption against brand rules |
| `POST` | `/refresh` | Refresh the local index from the configured CSV |
| `POST` | `/structure` | Structure a submitted brand note as JSON |
| `POST` | `/understand` | Classify a chat message and retain short chat context |

Example request:

```json
{
  "brand": "example_brand",
  "question": "What tone should we use?"
}
```

## Project layout

```text
.
├── answer.py       # Retrieval-grounded answers
├── api.py          # FastAPI endpoints
├── app.py          # Streamlit interface
├── build_index.py  # Generate and save embeddings
├── check.py        # Caption review against hard and soft rules
├── chunker.py      # Load approved CSV rows as knowledge chunks
├── llm.py          # Gemini client and generation retry handling
├── search.py       # Brand-filtered vector similarity search
├── understand.py   # Message intent classification and short chat memory
└── n8n/
    └── agency-brain-telegram.example.json  # Sanitized workflow export
```

## Data and credentials

Do not commit API keys, private client materials, chat histories, or the generated embedding index. Use public or anonymized sample content in a public repository. The repository `.gitignore` excludes `.env`, `venv/`, `__pycache__/`, `index.json`, `chat_memory.json`, and `documents/`.

This is a prototype. Review the API's access controls and data handling before exposing it to the public internet or using confidential agency/client material.

## Known gaps in this repository snapshot

- No dependency lockfile or existing `requirements.txt` was present; `requirements.txt` here lists direct runtime packages inferred from the Python imports.
- The indexed brand data and source documents are excluded; provide an approved sample CSV and generate a fresh local index to run it.
- No measured quality, speed, or business outcome metrics were supplied, so none are claimed here.
