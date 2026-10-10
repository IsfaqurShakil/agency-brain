from llm import generate
from search import brands, search


def rewrite_question(question):
    prompt = f"""Rewrite the question below as one clear English search query.
The question may be in Bangla, English, or Banglish (Bangla written in English letters).
Reply with ONLY the rewritten query, nothing else.

Question: {question}"""
    return generate(prompt).strip()


def answer(question, brand):
    search_query = rewrite_question(question)
    top = search(search_query, top_k=5, brand=brand)
    context = "\n\n".join(
        f"[Source: {chunk['source']}]\n{chunk['text']}" for _, chunk in top
    )

    prompt = f"""You are an assistant for an advertising agency team working on the brand "{brand}".
Answer the question using ONLY the context below.
If the answer is not in the context, say you could not find it.
Reply in the same language as the question.
At the end, list only the sources you actually used for the answer.

Context:
{context}

Question: {question}"""

    return generate(prompt)


if __name__ == "__main__":
    print("Brands:", ", ".join(brands()))
    brand = input("Brand: ")
    question = input("Question: ")
    print()
    print(answer(question, brand))