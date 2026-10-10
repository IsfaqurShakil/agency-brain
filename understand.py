import json
from pathlib import Path

from llm import generate
from search import brands

MEMORY_FILE = Path("chat_memory.json")
MAX_TURNS = 4


def _load():
    if MEMORY_FILE.exists():
        return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
    return {}


def _save(data):
    MEMORY_FILE.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _no(reply):
    return {"valid": False, "command": "", "brand": "", "body": "", "reply": reply}


def understand(chat_id, message):
    all_brands = brands()
    memory = _load()
    state = memory.get(str(chat_id), {"last_brand": None, "turns": []})

    history = "\n".join(f"- {t}" for t in state["turns"]) or "(none)"
    prompt = f"""You are the front desk of "Agency Brain", a Telegram assistant for an advertising agency.
Read the new message and decide what the person wants.

Brands: {", ".join(all_brands)}
Brand used in the last message of this chat: {state["last_brand"] or "none"}
Recent messages from this person:
{history}

New message: {message}

Return ONLY a JSON object with these keys:
- "intent": one of
  "ask" = a question about a brand's rules, tone, past campaigns, or results
  "check" = the person wants a caption or post text checked against brand rules
  "rule" = the person is giving a NEW rule, instruction, or campaign note to save
  "chat" = greeting, thanks, or small talk
  "unclear" = anything else
- "brand": one brand from the list, or null if it cannot be worked out. Use the last brand if the message is a follow-up without naming a brand. Match names even if spelled loosely, for example "surjo bank" means surjo_bank.
- "body": for ask, the full standalone question with any follow-up context filled in, in the person's own language. For check, ONLY the caption text to be checked. For rule, the new rule written as a clear statement. Otherwise an empty string.
- "reply": for chat or unclear only, a short friendly reply in the person's language that also says you can answer brand questions, check captions, or save new rules. Otherwise an empty string.

No markdown and no extra text."""

    raw = generate(prompt).strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {"intent": "unclear", "brand": None, "body": "", "reply": ""}

    intent = data.get("intent", "unclear")
    brand = data.get("brand")
    if brand not in all_brands:
        brand = None
    body = str(data.get("body") or "").strip()
    reply = str(data.get("reply") or "").strip()

    state["turns"] = (state["turns"] + [message])[-MAX_TURNS:]
    if brand:
        state["last_brand"] = brand
    memory[str(chat_id)] = state
    _save(memory)

    if intent in ("ask", "check", "rule"):
        if brand is None:
            return _no("Kon brand-er kotha bolchen? Brand gulo: " + ", ".join(all_brands))
        if not body:
            return _no("Aro ektu sposhto kore bolun, ami bujhte parlam na.")
        return {"valid": True, "command": intent, "brand": brand, "body": body, "reply": ""}

    if not reply:
        reply = "Ami brand-er rule niye prosno-r uttor, caption check, ar notun rule save korte pari. Ki jante chan?"
    return _no(reply)