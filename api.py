import json
import time

from fastapi import FastAPI
from pydantic import BaseModel

from answer import answer
from check import check_caption
from chunker import load_chunks
from llm import client, generate
from search import chunks
from understand import understand

app = FastAPI()


class AskRequest(BaseModel):
    brand: str
    question: str


class CheckRequest(BaseModel):
    brand: str
    caption: str


class RuleRequest(BaseModel):
    brand: str
    text: str


class UnderstandRequest(BaseModel):
    chat_id: int
    message: str


@app.get("/")
def home():
    return {"status": "Agency Brain API is running"}


@app.post("/ask")
def ask(req: AskRequest):
    return {"reply": answer(req.question, req.brand)}


@app.post("/check")
def check(req: CheckRequest):
    return {"reply": check_caption(req.caption, req.brand)}


@app.post("/refresh")
def refresh():
    latest = load_chunks()
    latest_texts = {c["text"] for c in latest}
    have_texts = {c["text"] for c in chunks}

    keep = [c for c in chunks if c["text"] in latest_texts]
    new = [c for c in latest if c["text"] not in have_texts]
    removed = len(chunks) - len(keep)

    for start in range(0, len(new), 20):
        batch = new[start : start + 20]
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=[c["text"] for c in batch],
        )
        for chunk, emb in zip(batch, result.embeddings):
            chunk["embedding"] = emb.values
        time.sleep(1)

    chunks[:] = keep + new
    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(chunks, f)

    return {"added": len(new), "removed": removed, "total": len(chunks)}


@app.post("/structure")
def structure(req: RuleRequest):
    prompt = f"""You help an advertising agency keep brand rules organized.
Brand: {req.brand}
The agency received this message to add to the brand's knowledge base:
\"\"\"{req.text}\"\"\"

Return ONLY a JSON object with these keys:
- "category": one of "guideline", "campaign", "sample_posts"
- "title": a short English title (maximum 8 words)
- "content": the message rewritten as one clear English rule or note. Keep every detail such as numbers, dates, and words to avoid. Keep any Bangla or Banglish words exactly as written.
- "valid": true if it is a real brand rule, campaign note, or sample post; false if it is chit-chat, a question, or unrelated

No markdown and no extra text."""
    raw = generate(prompt)
    cleaned = raw.strip()
    cleaned = cleaned.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        return {"valid": False, "category": "", "title": "", "content": ""}

    category = data.get("category", "guideline")
    if category not in ("guideline", "campaign", "sample_posts"):
        category = "guideline"
    return {
        "valid": bool(data.get("valid", False)),
        "category": category,
        "title": str(data.get("title", "")).strip(),
        "content": str(data.get("content", "")).strip(),
    }


@app.post("/understand")
def understand_endpoint(req: UnderstandRequest):
    return understand(req.chat_id, req.message)