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

usage_log = []                        # shown in the app as Bifrost stats
simulate_outage = {"on": False}       # the demo switch
BROKEN_MODEL = "gemini/gemini-outage-simulated"


def _parse_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def ask_json(model, system, user, retries=3):
    requested = model
    fallbacks = list(FALLBACKS)
    if simulate_outage["on"]:
        requested = BROKEN_MODEL            # pretend the main model is down
        fallbacks = [model] + fallbacks     # Bifrost should fall back to the real one
    extra = {"fallbacks": fallbacks} if fallbacks else {}

    for attempt in range(retries):
        try:
            began = time.time()
            resp = client.chat.completions.create(
                model=requested,
                messages=[
                    {"role": "system", "content": system + "\nRespond with valid JSON only."},
                    {"role": "user", "content": user},
                ],
                temperature=0,
                extra_body=extra,
            )
            info = getattr(resp, "model_extra", None) or {}
            routing = (info.get("extra_fields") or {}).get("routing_info") or {}
            usage_log.append({
                "requested": requested,
                "served_by": getattr(resp, "model", requested),
                "fallback_used": bool(routing.get("is_fallback", False)),
                "tokens": resp.usage.total_tokens if resp.usage else 0,
                "seconds": round(time.time() - began, 2),
            })
            return _parse_json(resp.choices[0].message.content)
        except Exception as e:
            if attempt == retries - 1:
                raise
            print(f"Retrying in 15s because of: {str(e)[:120]}")
            time.sleep(15)