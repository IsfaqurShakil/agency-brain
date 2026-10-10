import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

result = client.models.embed_content(
    model="gemini-embedding-001",
    contents="Shobuj Bite is a healthy snack brand",
)

vector = result.embeddings[0].values
print("Numbers in the list:", len(vector))
print("First 5 numbers:", vector[:5])