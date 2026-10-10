import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL = "gemini-3-flash-preview"


def generate(prompt, tries=5):
    for attempt in range(tries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except errors.APIError as e:
            if e.code not in (429, 500, 503) or attempt == tries - 1:
                raise
            wait = 3 * (attempt + 1)
            print(f"Model busy, trying again in {wait} seconds...")
            time.sleep(wait)