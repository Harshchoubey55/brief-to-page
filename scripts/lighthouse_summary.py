"""Pick the median Lighthouse run in a folder and print the numbers I track.

    python scripts/lighthouse_summary.py reports/lighthouse/first-pass
"""
import json
import shutil
import statistics
import sys
from pathlib import Path

CATS = ["performance", "accessibility", "best-practices", "seo"]
AUDITS = {
    "largest-contentful-paint": "LCP",
    "cumulative-layout-shift": "CLS",
    "total-blocking-time": "TBT",
    "total-byte-weight": "Page weight",
}


def load(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    row = {c: round(data["categories"][c]["score"] * 100) for c in CATS}
    for key, name in AUDITS.items():
        row[name] = data["audits"][key]["numericValue"]
    row["failing_a11y"] = [
        a["id"]
        for ref in data["categories"]["accessibility"]["auditRefs"]
        if (a := data["audits"][ref["id"]]).get("score") is not None and a["score"] < 1 and ref["weight"] > 0
    ]
    return row


def main():
    folder = Path(sys.argv[1])
    runs = [load(p) for p in sorted(folder.glob("run-*.report.json"))]
    if not runs:
        sys.exit(f"no runs found in {folder}")
    perf = [r["performance"] for r in runs]
    median_idx = perf.index(statistics.median_low(perf))
    median_run = runs[median_idx]
    # keep the median run's HTML report next to the summary, the raw runs stay out of git
    shutil.copy2(folder / f"run-{median_idx + 1}.report.html", folder / "report.html")

    summary = {
        "runs": len(runs),
        "median_run": median_idx + 1,
        "performance_all_runs": perf,
        **{k: v for k, v in median_run.items()},
    }
    (folder / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"{folder.name}: performance {perf} -> median {median_run['performance']}")
    for c in CATS[1:]:
        print(f"  {c}: {median_run[c]}")
    print(f"  LCP {median_run['LCP'] / 1000:.1f} s, CLS {median_run['CLS']:.3f}, "
          f"TBT {median_run['TBT']:.0f} ms, weight {median_run['Page weight'] / 1e6:.2f} MB")
    if median_run["failing_a11y"]:
        print("  accessibility audits failing:", ", ".join(median_run["failing_a11y"]))


if __name__ == "__main__":
    main()
