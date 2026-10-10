from llm import generate
from search import brands, chunks


def check_caption(caption, brand):
    rules = "\n\n".join(
        c["text"]
        for c in chunks
        if c["brand"] == brand and "| guideline |" in c["text"]
    )

    prompt = f"""You are a brand reviewer for an advertising agency.
Check the caption below against the brand rules of "{brand}" in the context.
Use ONLY the context for the rules.

Two kinds of rules:
- HARD rules use words like "never", "always", "must", "do not". Breaking one means FAIL.
- SOFT rules use words like "avoid", "prefer", "allowed", "welcome". Never FAIL for a soft rule. Only mention it as a suggestion.
Ignore festival rules if the caption is not about a festival.
A rule that applies only to one platform (for example "on Facebook posts") counts as a HARD rule only if the caption clearly says it is for that platform. Otherwise mention it under Suggestions.
In the fixed version, keep the brand name and hashtags exactly as written in the rules. Never translate or change the brand name.
If the fixed version mentions the mobile app, it must also include any reminder line that the rules require for app posts.

Reply in this format:
1. Verdict: PASS or FAIL (FAIL only if a HARD rule is broken)
2. Problems: each broken HARD rule, with the part of the caption that breaks it. Write "None" if there are none.
3. Suggestions: optional improvements from SOFT rules. Write "None" if there are none.
4. Fixed version: if FAIL, rewrite the caption so it follows every hard rule, including required hashtags. If PASS, write "No change needed".
Reply in the same language as the caption.

Context:
{rules}

Caption:
{caption}"""

    return generate(prompt)


if __name__ == "__main__":
    print("Brands:", ", ".join(brands()))
    brand = input("Brand: ")
    caption = input("Caption: ")
    print()
    print(check_caption(caption, brand))