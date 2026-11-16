import os
from datetime import date
from tavily import TavilyClient
from dotenv import load_dotenv
from llm import ask_json, VERIFY_MODEL

load_dotenv()
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

SYSTEM = """You verify one claim using ONLY the web sources provided.
Return JSON in exactly this shape:
{
  "verdict": "supported" | "outdated" | "contradicted" | "inconclusive",
  "current_fact": "what the sources say is true today",
  "evidence_date": "a date found in the sources, or null",
  "best_source_url": "the single most useful source URL, or null",
  "reasoning": "one or two short sentences",
  "confidence": a number between 0 and 1
}

Definitions:
- supported: the sources confirm the claim is still true today.
- outdated: the claim was true in the past but the sources show it has changed.
- contradicted: the sources show the claim is wrong.
- inconclusive: the sources do not settle it.

Rules:
- Use only the sources. Never invent facts or URLs. If unsure, use inconclusive.
- evidence_date must be a date that appears in the sources. If none does, use null.
- Use "outdated" when the claim was true at some earlier time but has since changed.
- Use "contradicted" only when the claim was never accurate.
- If the sources only show that a later event was scheduled before today's date, you may
  mark the claim outdated, but say in the reasoning that this is inferred from the schedule,
  and keep confidence at 0.8 or lower.
- For best_source_url, prefer official, primary, or news sources over social media."""


def search_web(claim):
    # Ask for the latest information, so old pages do not crowd out new ones.
    query = f"{claim} latest update {date.today().year}"
    response = tavily.search(query=query, search_depth="advanced", max_results=6)
    sources = []
    for r in response.get("results", []):
        sources.append({
            "title": r.get("title"),
            "url": r.get("url"),
            "content": (r.get("content") or "")[:1200],
            "published": r.get("published_date"),
        })
    return sources


def verify_claim(claim, sources, today):
    if not sources:
        return {"verdict": "inconclusive", "current_fact": "No sources found.",
                "evidence_date": None, "best_source_url": None,
                "reasoning": "The web search returned nothing.", "confidence": 0.3}

    text = "\n\n".join(
        f"[{i + 1}] {s['title']} ({s['url']}) published={s['published']}\n{s['content']}"
        for i, s in enumerate(sources)
    )
    user = f"Today's date: {today}\n\nCLAIM: {claim}\n\nSOURCES:\n{text}"
    result = ask_json(VERIFY_MODEL, SYSTEM, user)

    result.setdefault("verdict", "inconclusive")
    result.setdefault("current_fact", "")
    result.setdefault("evidence_date", None)
    result.setdefault("best_source_url", None)
    result.setdefault("reasoning", "")
    result.setdefault("confidence", 0.5)

    # Guard: the evidence date must come from a source, not be today's date.
    if str(result.get("evidence_date")) == today:
        result["evidence_date"] = None

    return result