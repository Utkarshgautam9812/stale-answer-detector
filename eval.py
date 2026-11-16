import json
import time
from pipeline import run

tests = json.load(open("tests.json", encoding="utf-8"))
rows = []

for i, t in enumerate(tests, 1):
    try:
        results = run(t["answer"])
        predicted_stale = any(r["label"] == "STALE" for r in results)
        status = "ok"
    except Exception as e:
        predicted_stale = None
        status = "error: " + str(e)[:80]

    correct = (status == "ok") and (predicted_stale == t["expect_stale"])
    rows.append({"answer": t["answer"], "expected_stale": t["expect_stale"],
                 "predicted_stale": predicted_stale, "correct": correct, "status": status})
    mark = "PASS" if correct else "FAIL"
    print(f"[{i}/{len(tests)}] {mark}  expected_stale={t['expect_stale']}  "
          f"predicted_stale={predicted_stale}  {t['answer']}  {status if status != 'ok' else ''}")
    time.sleep(2)

done = [r for r in rows if r["status"] == "ok"]
stale = [r for r in done if r["expected_stale"]]
fresh = [r for r in done if not r["expected_stale"]]
caught = sum(1 for r in stale if r["predicted_stale"])
false_alarms = sum(1 for r in fresh if r["predicted_stale"])
accuracy = sum(1 for r in done if r["correct"]) / max(1, len(done))

print("\n" + "=" * 50)
print(f"Completed: {len(done)}/{len(rows)}")
print(f"Overall accuracy: {accuracy:.0%}")
print(f"Stale answers caught: {caught}/{len(stale)}")
print(f"False alarms on fresh answers: {false_alarms}/{len(fresh)}")

json.dump(rows, open("eval_results.json", "w", encoding="utf-8"), indent=2)
print("Saved details to eval_results.json")