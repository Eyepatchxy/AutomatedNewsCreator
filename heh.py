from google import genai
import os

apiKey = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=apiKey)

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    contents="A cyberpunk cat riding a motorcycle"
)

print(response)