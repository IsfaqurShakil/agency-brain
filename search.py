import json
import math
import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

with open("index.json", encoding="utf-8") as f:
    chunks = json.load(f)


def brands():
    return sorted({c["brand"] for c in chunks})


def similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    len_a = math.sqrt(sum(x * x for x in a))
    len_b = math.sqrt(sum(y * y for y in b))
    return dot / (len_a * len_b)


def search(question, top_k=3, brand=None):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question,
    )
    q_vector = result.embeddings[0].values
    pool = [c for c in chunks if brand is None or c["brand"] == brand]
    scored = [(similarity(q_vector, c["embedding"]), c) for c in pool]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:top_k]


if __name__ == "__main__":
    print("Brands:", ", ".join(brands()))
    brand = input("Brand: ")
    question = input("Question: ")
    for score, chunk in search(question, brand=brand):
        print("---")
        print("Score:", round(score, 3), "| Source:", chunk["source"])
        print(chunk["text"])