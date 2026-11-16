from pipeline import run

answer = (
    "Twitter's CEO is Jack Dorsey, and the platform is still called Twitter. "
    "ChatGPT Plus costs $20 per month. Paris is the capital of France."
)

for r in run(answer):
    print("=" * 60)
    print(f"{r['label']} ({r['score']}/100): {r['claim']}")
    print("Verdict:", r["verdict"], "| Confidence:", r["confidence"])
    print("Current fact:", r["current_fact"])
    print("Why:", r["reasoning"])
    print("Source:", r["best_source_url"])