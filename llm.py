import os, json, re, time
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url=os.getenv("BIFROST_URL", "http://localhost:8080/v1"),
    api_key="not-needed",
)

EXTRACT_MODEL = os.getenv("EXTRACT_MODEL", "gemini/gemini-3.1-flash-lite")
VERIFY_MODEL = os.getenv("VERIFY_MODEL", "gemini/gemini-3.1-flash-lite")
FALLBACKS = [m.strip() for m in os.getenv("FALLBACK_MODELS", "").split(",") if m.strip()]

usage_log = []  # we show this in the app later as Bifrost stats


def _parse_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def ask_json(model, system, user, retries=3):
    extra = {"fallbacks": FALLBACKS} if FALLBACKS else {}
    for attempt in range(retries):
        try:
            began = time.time()
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system + "\nRespond with valid JSON only."},
                    {"role": "user", "content": user},
                ],
                temperature=0,
                extra_body=extra,
            )
            usage_log.append({
                "requested": model,
                "served_by": getattr(resp, "model", model),
                "tokens": resp.usage.total_tokens if resp.usage else 0,
                "seconds": round(time.time() - began, 2),
            })
            return _parse_json(resp.choices[0].message.content)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"Retrying in 15s because of: {str(e)[:120]}")
            time.sleep(15)
            