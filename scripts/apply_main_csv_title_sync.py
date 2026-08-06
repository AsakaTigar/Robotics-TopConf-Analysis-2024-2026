"""Commit 2 / 7 — mirror identity corrections into datasets/ main CSV.

The main public README is rendered from `datasets/robotics_papers_2024_2026_analysis.csv`
and the four partitioned CSVs, NOT from the business-track CSVs under
research_tracks/.  This script re-applies the exact same canonical-title /
arXiv-id / authors corrections to any row in the MAIN CSV whose Paper Link
matches the arXiv ids we verified in `data_verification_log_2026_08.md`.

This is a **field-level in-place mutation** only — rows are never added or
dropped, Year/Venue/Code Link/Robot Type/Affiliation are preserved as-is unless
the auditor explicitly flagged them (VLA-IE-008 had the wrong Paper Link).

Run after scripts/apply_commit2_corrections.py:

  python scripts/apply_main_csv_title_sync.py
"""
import csv, os

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE  = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
MAIN  = os.path.join(BASE, "datasets", "robotics_papers_2024_2026_analysis.csv")
TMP   = MAIN + ".tmp"

# Exact same canonical metadata used for the research_tracks patch.
CANONICAL = {
    "2506.07639": dict(title="Fast ECoT: Efficient Embodied Chain-of-Thought via Thoughts Reuse",
                       authors="Zhekai Duan; Yuan Zhang; Shikai Geng; Gaowen Liu; Joschka Boedecker; Chris Xiaoxuan Lu"),
    "2502.02175": dict(title="VLA-Cache: Efficient Vision-Language-Action Manipulation via Adaptive Token Caching",
                       authors="Siyu Xu; Yunke Wang; Chenghao Xia; Dihao Zhu; Tao Huang; Chang Xu"),
    "2506.10100": dict(title="EfficientVLA: Training-Free Acceleration and Compression for Vision-Language-Action Models",
                       authors="Yantai Yang; Yuhao Wang; Zichen Wen; Luo Zhongwei; Chang Zou; Zhipeng Zhang; Chuan Wen; Linfeng Zhang"),
    "2607.06370": dict(title="ActionCache: Training-Free Acceleration for Vision-Language-Action Models with Action Caching and Refinement",
                       authors="Ryuji Oi; Hikari Otsuka; Kosuke Matsushima; Yuki Ichikawa; Masato Motomura; Tatsuya Kaneko; Daichi Fujiki"),
    "2605.29438": dict(title="ElegantVLA: Learning When to Think for Efficient Vision-Language-Action Models",
                       authors="Ye Li; Huanan Liu; Kangye Ji; Yuan Meng; Jiajun Fan; Yuansong Wang; Shiyu Qin; Chenglei Wu; Shu-Tao Xia; Zhi Wang"),
    "2606.03784": dict(title="Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation",
                       authors="Nan Sun; Yuan Zhang; Yongkun Yang; Wentao Zhao; Peiyan Li; Jun Guo; Wenxuan Song; Pengxiang Ding; Runze Suo; Yifei Su; Xin Xiao; Xinghang Li; Huaping Liu"),
    # CRITICAL paper-link swap for ECoT VLA-IE-008 (was wireless comms 2501.12148)
    "2407.08693": dict(title="Robotic Control via Embodied Chain-of-Thought Reasoning",
                       authors="Michał Zawalski; William Chen; Karl Pertsch; Oier Mees; Chelsea Finn; Sergey Levine"),
    "2604.21254": dict(title="Hyperloop Transformers",
                       authors="Abbas Zeitoun; Lucas Torroba-Hennigen; Yoon Kim"),
    "2605.23872": dict(title="Training-Free Looped Transformers",
                       authors="Lizhang Chen; Jonathan Li; Chen Liang; Ni Lao; Qiang Liu"),
    "2605.16343": dict(title="LoopQ: Quantization for Recursive Transformers",
                       authors="Rui Fang; Hsi-Wen Chen; Ming-Syan Chen"),
    "2602.07845": dict(title="Recurrent-Depth VLA: Implicit Test-Time Compute Scaling of Vision-Language-Action Models via Latent Iterative Reasoning",
                       authors="Yalcin Tur; Jalal Naghiyev; Haoquan Fang; Wei-Chuan Tsai; Jiafei Duan; Dieter Fox; Ranjay Krishna"),
    # Auditor-detected identity mismatches
    "2505.08243": dict(title="Training Strategies for Efficient Embodied Reasoning",
                       authors="William Chen; Suneel Belkhale; Suvir Mirchandani; Oier Mees; Danny Driess; Karl Pertsch; Sergey Levine"),
    "2601.09708": dict(title="Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning",
                       authors="Chi-Pin Huang; Yunze Man; Zhiding Yu; Min-Hung Chen; Jan Kautz; Yu-Chiang Frank Wang; Fu-En Yang"),
    "2507.10524": dict(title="Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation",
                       authors="Sangmin Bae; Yujin Kim; Reza Bayat; Sungnyun Kim; Jiyoun Ha; Tal Schuster; Adam Fisch; Hrayr Harutyunyan; Ziwei Ji; Aaron Courville; Se-Young Yun"),
}

# Auditor-detected WRONG paper-link rows:
#   VLA-IE-008 had link "https://arxiv.org/abs/2501.12148" (comm theory)
#   → replace with 2407.08693 + update title/authors.
WRONG_LINK_SWAPS = {
    "https://arxiv.org/abs/2501.12148": ("2407.08693", "https://arxiv.org/abs/2407.08693"),
}


PENDING_TAG_TEMPLATES = {
    "VLA-IE-016": "VERIFICATION_STATUS=PENDING; authoritative_sources=0; Commit 2.1 Hotfix; arXiv/S2 search exact-title: 0 hits; do not treat as verified baseline",
    "VLA-IE-017": "VERIFICATION_STATUS=PENDING; authoritative_sources=0; Commit 2.1 Hotfix; arXiv/S2 search exact-title: 0 hits; do not treat as verified baseline",
}

FORBIDDEN_PHRASES = [
    "Looped Transformers Are Better In-Context Learners",
    "Better In-Context Learners",
    "From Recurrent to Looped: A Unified View of Weight-Sharing",
    "Unified View of Weight-Sharing",
    "From Recurrent to Looped",
    "OLD_TITLE=",
    "Generic LLM",
    "weight-sharing loops",
    "same-FLOPs deep non-loop",
    "1B loop > 1B non-loop",
    "1B loop > 1B non-loop at same storage",
    "Generic Transformer",
    "theoretical classification of loop vs recurrent depth sharing",
    "sample complexity",
    "implicit regularization",
    "theory unification",
    "Unifies recurrent weight-sharing with looped transformer paradigms",
    "Background reference for loop section",
]


def main():
    with open(MAIN, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    n_patched = 0
    import re as _re
    for r in rows:
        notes = (r.get("Notes") or "")
        scrubbed_notes = notes
        for p in FORBIDDEN_PHRASES:
            scrubbed_notes = scrubbed_notes.replace(p, "")
        scrubbed_notes = _re.sub(r"\s*\|\s*(\s*\|\s*)+", " | ", scrubbed_notes).strip(" |")
        if scrubbed_notes != notes:
            r["Notes"] = scrubbed_notes

        link = r.get("Paper Link", "") or ""
        # Step A: resolve wrong-link swaps first (ECoT 008)
        if link in WRONG_LINK_SWAPS:
            arxiv_id, new_link = WRONG_LINK_SWAPS[link]
            r["Paper Link"] = new_link
            M = CANONICAL[arxiv_id]
            old_t = r["Title"]
            r["Title"] = M["title"]
            r["Authors"] = M["authors"]
            r["Notes"] = (
                (r.get("Notes") or "").strip()
                + f" | CANONICAL_LINK_CORRECTED: 2501.12148→{arxiv_id} @ 2026-08-06; ROADMAP commit 2/7; OLD_TITLE={old_t[:80]}"
            ).lstrip(" |")
            n_patched += 1
            continue

        # Step B: search for a canonical arXiv id substring match
        for arxiv_id, M in CANONICAL.items():
            if arxiv_id in link:
                old_t = r["Title"]
                if r["Title"] == M["title"] and r["Authors"] == M["authors"]:
                    break
                r["Title"] = M["title"]
                r["Authors"] = M["authors"]
                tag = f"CANONICAL_TITLE_VERIFIED: arXiv:{arxiv_id} @ 2026-08-06; ROADMAP commit 2/7; OLD_TITLE={old_t[:80]}"
                existing = (r.get("Notes") or "").strip()
                r["Notes"] = (existing + " | " + tag) if existing else tag
                n_patched += 1
                break

        # Step C: Commit 2.1 Hotfix — IE-016/017 pending tagging (if present in main CSV)
        tid = r.get("Track ID", "") or ""
        matched_pending_key = None
        if tid in PENDING_TAG_TEMPLATES:
            matched_pending_key = tid
        else:
            for pk in PENDING_TAG_TEMPLATES:
                if pk in (r.get("Title") or "") or pk in link:
                    matched_pending_key = pk
                    break
        if matched_pending_key:
            tag = PENDING_TAG_TEMPLATES[matched_pending_key]
            existing_n = (r.get("Notes") or "").strip()
            if "VERIFICATION_STATUS=PENDING" not in existing_n:
                r["Notes"] = (existing_n + " | " + tag) if existing_n else tag
            if (r.get("Paper Link") or "").strip() in ("", "NA", "N/A"):
                a = r.get("Authors") or ""
                if "(related" in a:
                    r["Authors"] = ""
                r["Venue / Source"] = ""
                r["Reported Speedup"] = ""
                r["Primary Metric"] = ""

    with open(TMP, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    os.replace(TMP, MAIN)
    print(f"[commit2-main-csv-sync] Patched {n_patched} / {len(rows)} rows in {MAIN}")


if __name__ == "__main__":
    main()
