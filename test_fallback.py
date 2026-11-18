from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="not-needed")

resp = client.chat.completions.create(
    model="gemini/gemini-does-not-exist",
    messages=[{"role": "user", "content": "Say hello in 5 words."}],
    extra_body={"fallbacks": ["gemini/gemini-3.1-flash-lite"]},
)

print("Answer:", resp.choices[0].message.content)
print("Model that actually answered:", resp.model)
print("Extra info:", getattr(resp, "model_extra", None))