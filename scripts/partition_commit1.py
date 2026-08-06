"""Commit-1 data partitioner for the Robotics-CoT-Atlas migration.

Reads the backward-compatible master CSV and splits it into four files:
    datasets/verified_papers.csv         rows with NO DATA_QUALITY=* flag AND
                                         year != 2026
    datasets/pending_verification.csv   PLACEHOLDER_AUTHORS + REVIEW flags
                                         (from any venue/year except 2026)
    datasets/predicted_trends.csv        rows where Year == '2026'
                                         (predicted trend topics — never
                                          counted in the 'Total papers' badge)
    datasets/rejected_or_synthetic.csv  RESERVED (empty on commit 1)

The master CSV is NEVER overwritten; it remains the source of truth for
editorial edits.

Run (repo root):
    python scripts/partition_commit1.py
"""
import csv, os

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE  = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE

MAIN_CSV = os.path.join(BASE, "datasets", "robotics_papers_2024_2026_analysis.csv")
OUT_VER  = os.path.join(BASE, "datasets", "verified_papers.csv")
OUT_PEND = os.path.join(BASE, "datasets", "pending_verification.csv")
OUT_PRED = os.path.join(BASE, "datasets", "predicted_trends.csv")
OUT_REJ  = os.path.join(BASE, "datasets", "rejected_or_synthetic.csv")

with open(MAIN_CSV, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames or []
    rows_all = list(reader)

verified, pending, predicted, rejected = [], [], [], []

for r in rows_all:
    notes = r.get("Notes", "") or ""
    year  = r.get("Year",  "") or ""
    ph    = "DATA_QUALITY=PLACEHOLDER_AUTHORS" in notes
    rv    = notes.startswith("DATA_QUALITY=REVIEW") or "DATA_QUALITY=REVIEW|" in notes

    if year == "2026":
        predicted.append(r)
    elif ph or rv:
        pending.append(r)
    else:
        verified.append(r)

def _write_csv(path, rows):
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

_write_csv(OUT_VER,  verified)
_write_csv(OUT_PEND, pending)
_write_csv(OUT_PRED, predicted)
_write_csv(OUT_REJ,  rejected)   # intentionally empty on commit 1

ph_n = sum(1 for r in rows_all if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in (r.get("Notes","") or ""))
rv_n = sum(1 for r in rows_all if "DATA_QUALITY=REVIEW" in (r.get("Notes","") or ""))

print(f"MAIN_CSV rows       : {len(rows_all)}")
print(f"PLACEHOLDER_AUTHORS : {ph_n}")
print(f"REVIEW              : {rv_n}")
print(f"---")
print(f"verified_papers.csv            : {len(verified):>4}")
print(f"pending_verification.csv       : {len(pending):>4}  (= {ph_n} placeholder + {rv_n} review)")
print(f"predicted_trends.csv           : {len(predicted):>4}  (= 2026 trend rows, NOT venue papers)")
print(f"rejected_or_synthetic.csv      : {len(rejected):>4}  (reserved)")
print(f"SUM = {len(verified)+len(pending)+len(predicted)+len(rejected)}")
