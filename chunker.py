import csv
import io
import os
import urllib.request
from collections import Counter

from dotenv import load_dotenv

load_dotenv()


def load_chunks():
    url = os.getenv("SHEET_CSV_URL")
    with urllib.request.urlopen(url) as response:
        text = response.read().decode("utf-8")

    chunks = []
    for row in csv.DictReader(io.StringIO(text)):
        if row["status"].strip().lower() != "approved":
            continue
        brand = row["brand"].strip()
        category = row["category"].strip()
        title = row["title"].strip()
        content = row["content"].strip()
        chunks.append(
            {
                "brand": brand,
                "source": f"{brand} / {title}",
                "text": f"[{brand} | {category} | {title}] {content}",
            }
        )
    return chunks


if __name__ == "__main__":
    chunks = load_chunks()
    print("Total chunks:", len(chunks))
    for brand, count in Counter(c["brand"] for c in chunks).items():
        print(brand, "->", count, "chunks")