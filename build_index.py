import json
import os
import time

from dotenv import load_dotenv
from google import genai

from chunker import load_chunks

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

chunks = load_chunks()
print("Chunks to embed:", len(chunks))

BATCH = 20
for start in range(0, len(chunks), BATCH):
    batch = chunks[start : start + BATCH]
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=[c["text"] for c in batch],
    )
    for chunk, emb in zip(batch, result.embeddings):
        chunk["embedding"] = emb.values
    print("Done:", start + len(batch), "/", len(chunks))
    time.sleep(1)

with open("index.json", "w", encoding="utf-8") as f:
    json.dump(chunks, f)

print("Saved", len(chunks), "chunks to index.json")