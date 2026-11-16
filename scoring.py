OFFICIAL_HINTS = (".gov", ".edu", "docs.", "developer.", "github.com", "/pricing",
                  "investor.", "newsroom", "help.", "wikipedia.org")
WEAK_HINTS = ("instagram.com", "facebook.com", "tiktok.com", "reddit.com",
              "quora.com", "pinterest.com", "x.com", "twitter.com")


def is_official(url):
    return bool(url) and any(h in url.lower() for h in OFFICIAL_HINTS)


def is_weak(url):
    return bool(url) and any(h in url.lower() for h in WEAK_HINTS)


def freshness_score(result):
    try:
        confidence = float(result.get("confidence", 0.5))
    except (TypeError, ValueError):
        confidence = 0.5
    confidence = max(0.0, min(1.0, confidence))

    url = result.get("best_source_url")
    if is_official(url):
        confidence = min(1.0, confidence + 0.1)   # trusted source: more weight
    if is_weak(url):
        confidence = max(0.0, confidence - 0.3)   # social media: less weight

    verdict = result.get("verdict", "inconclusive")
    if verdict == "supported":
        score = 70 + 30 * confidence
    elif verdict == "inconclusive":
        score = 50
    else:  # outdated or contradicted
        score = 30 - 25 * confidence

    return round(max(5, min(95, score)))  # never claim perfect certainty


def label(score):
    if score >= 70:
        return "FRESH"
    if score >= 40:
        return "UNCERTAIN"
    return "STALE"