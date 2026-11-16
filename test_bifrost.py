from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")

candidates = [
    "gemini/gemini-3.1-flash-lite",
    "gemini/gemini-3.5-flash",
    "gemini/gemini-3-flash-preview",
]

for model in candidates:
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Say hello in 5 words."}],
        )
        print("WORKS:", model, "->", resp.choices[0].message.content)
    except Exception as e:
        print("FAILED:", model, "->", str(e)[:200])