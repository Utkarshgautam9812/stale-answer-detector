from llm import ask_json, EXTRACT_MODEL

SYSTEM = """You extract factual claims from an AI-generated answer.
Return JSON in this shape:
{"claims": [{"claim": "...", "category": "...", "volatility": "high|medium|low"}]}

category must be one of: pricing, api_version, law_regulation, leadership,
product_feature, statistic, other.

volatility means how likely the fact is to have changed in the last 1-2 years.

Volatility rules:
- "high": any claim that uses time-relative words such as latest, newest, most recent,
  current, currently, now, still, new, recently, or this year. Also any claim about who
  holds a position today, the latest version of something, or a price or plan.
- "medium": facts that change every few years, such as company structure or regulations.
- "low": only facts that essentially never change, such as geography, math, or settled history.

Other rules:
- Only include objective facts that can be checked.
- Ignore opinions and advice.
- Write each claim as one complete, standalone sentence."""


def extract_claims(answer):
    data = ask_json(EXTRACT_MODEL, SYSTEM, answer)
    return data.get("claims", [])