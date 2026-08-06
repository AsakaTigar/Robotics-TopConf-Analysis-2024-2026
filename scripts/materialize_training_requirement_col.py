import csv
import os
import sys

TRAINING_REQUIREMENT_17 = {
    "VLA-IE-001": "training_free",
    "VLA-IE-002": "training_free",
    "VLA-IE-003": "training_free",
    "VLA-IE-004": "training_free",
    "VLA-IE-005": "training_free",
    "VLA-IE-006": "analysis_only",
    "VLA-IE-007": "reference_backbone",
    "VLA-IE-008": "requires_finetuning",
    "VLA-IE-009": "trained_architecture",
    "VLA-IE-010": "trained_architecture",
    "VLA-IE-011": "frozen_model_controller_only",
    "VLA-IE-012": "analysis_only",
    "VLA-IE-013": "requires_finetuning",
    "VLA-IE-014": "requires_finetuning",
    "VLA-IE-015": "requires_distillation",
    "VLA-IE-016": "unknown",
    "VLA-IE-017": "unknown",
}

CSV_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "research_tracks",
    "vla_inference_efficiency_2024_2026.csv",
)


def main():
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    col_appended = False
    if "training_requirement" not in fieldnames:
        fieldnames.append("training_requirement")
        col_appended = True

    changed = False
    for row in rows:
        enum_val = TRAINING_REQUIREMENT_17.get(row.get("Track ID", ""), "unknown")
        old_val = row.get("training_requirement")
        if old_val != enum_val:
            changed = True
            row["training_requirement"] = enum_val

    if not col_appended and not changed:
        print("Idempotent: no changes needed.")
        return 0

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(rows)

    if col_appended:
        print("Appended training_requirement column and populated 17 rows.")
    else:
        print("Updated training_requirement values in-place.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
