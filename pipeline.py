import time
from datetime import date
from claims import extract_claims
from verify import search_web, verify_claim
from scoring import freshness_score, label


def run(answer):
    today = date.today().isoformat()
    results = []

    for c in extract_claims(answer):
        if str(c.get("volatility", "")).lower() == "low":
            continue  # stable facts do not need re-checking

        sources = search_web(c["claim"])
        verdict = verify_claim(c["claim"], sources, today)
        score = freshness_score(verdict)

        results.append({**c, **verdict, "score": score,
                        "label": label(score), "sources": sources})
        time.sleep(4)  # gentle pause for free-tier rate limits

    return results