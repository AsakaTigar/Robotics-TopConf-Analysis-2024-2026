"""Commit 2 / 7 — apply auditor's identity corrections to the VLA-Inference-Efficiency track.

Rule: NEVER edit CSVs by hand for auditor-verified identity changes.
Run this script reproducibly instead.

  python scripts/apply_commit2_corrections.py

What it does (see docs/data_verification_log_2026_08.md for per-row evidence):

  # auditor-flagged identity errors (TOP priority):
  VLA-IE-001 Fast ECoT           : canonical_title ← arXiv 2506.07639 (old = expanded
                                    non-official summary title);
                                    reported_speedup ← author-given "Up to ~7.5% end-to-end
                                    latency reduction on LIBERO + OpenVLA-ECoT" instead of
                                    user-inserted "1.5x–3x end-to-end" (not cited by authors)
  VLA-IE-002 VLA-Cache           : canonical_title ← arXiv 2502.02175 (old used "Inference
                                    via Token-Level Cross-Frame Caching" self-invented)
  VLA-IE-003 EfficientVLA        : canonical_title ← arXiv 2506.10100v1
                                    "EfficientVLA: Training-Free Acceleration & Compression for VLAs"
  VLA-IE-004 ActionCache         : canonical_title ← arXiv 2607.06370 (OK but re-sync authors)
  VLA-IE-005 ElegantVLA          : canonical_title ← arXiv 2605.29438 (old used
                                    "When Is Full Reasoning Worth It?" self-invented)
  VLA-IE-006 ERVLA (nickname)    : canonical_title ← arXiv 2606.03784 full title, nickname
                                    "ERVLA" promoted to display_title only
  VLA-IE-008 ECoT                : CRITICAL: old paper link = 2501.12148 (a wireless
                                    communications paper!), corrected to canonical ECoT
                                    arXiv 2407.08693 "Robotic Control via Embodied CoT
                                    Reasoning" + Zawalski, Chen, Pertsch, Mees, Finn, Levine
  VLA-IE-010 Hyperloop           : canonical_title ← arXiv 2604.21254 official "Hyperloop Transformers"
  VLA-IE-011 Training-Free Looped: canonical_title ← arXiv 2605.23872  shortened+official
  VLA-IE-012 LoopQ               : canonical_title ← arXiv 2605.16343 full
                                    "LoopQ: Quantization for Recursive Transformers"
                                    (old title lacked "Quantization for…" keyword)
  VLA-IE-013 RD-VLA              : canonical_title ← arXiv 2602.07845 full title
                                    (nickname "RD-VLA" moved to display_title)
  VLA-IE-014 auditor flag: 2505.08243 MISMATCH
                          : OLD: "Looped Transformers Are Better In-Context Learners"
                            NEW: arXiv 2505.08243 = Training Strategies for Efficient
                                 Embodied Reasoning (ECoT-Lite, Chen et al. Stanford/Berkeley)
                            → retitle + recategorize method to Train-time-Reasoning.
  VLA-IE-015 auditor flag: 2601.09708 MISMATCH
                          : OLD: "From Recurrent to Looped: A Unified View..." (general loop-theory)
                            NEW: arXiv 2601.09708 = Fast-ThinkAct: Efficient VLA Reasoning
                                 via Verbalizable Latent Planning
                            → retitle + recategorize method + note venue is no longer ICLR
                                 but arXiv preprint until venue-confirmed.

For every row that we touch:
  1. Authors: populated verbatim from arXiv API Atom feed (semicolon separated)
     (old "(from 2506.07639)" and "(OpenVLA original)" style placeholders replaced)
  2. Paper Link: corrected to canonical https://arxiv.org/abs/<id> (ECoT 008)
  3. Notes column: appended "CANONICAL_TITLE_VERIFIED: <arXiv id> @ 2026-08-06"
     with auditor reference "COMMIT 2 / ROADMAP step 2".
"""
import csv, os, copy, sys, re as _re, hashlib, pathlib, difflib

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE  = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE
VLA_CSV = os.path.join(BASE, "research_tracks", "vla_inference_efficiency_2024_2026.csv")
OUT = VLA_CSV + ".tmp"

CANONICAL = {
    "2506.07639": {
        "title": "Fast ECoT: Efficient Embodied Chain-of-Thought via Thoughts Reuse",
        "authors": "Zhekai Duan; Yuan Zhang; Shikai Geng; Gaowen Liu; Joschka Boedecker; Chris Xiaoxuan Lu",
        "display": "Fast ECoT",
        "reported_speedup": (
            "Up to ~7.5% end-to-end latency reduction (author-reported, abstract §1) on "
            "LIBERO + OpenVLA-ECoT baseline."
        ),
        "venue": "arXiv",
    },
    "2502.02175": {
        "title": "VLA-Cache: Efficient Vision-Language-Action Manipulation via Adaptive Token Caching",
        "authors": "Siyu Xu; Yunke Wang; Chenghao Xia; Dihao Zhu; Tao Huang; Chang Xu",
        "display": "VLA-Cache",
        "venue": "arXiv",
    },
    "2506.10100": {
        "title": "EfficientVLA: Training-Free Acceleration and Compression for Vision-Language-Action Models",
        "authors": "Yantai Yang; Yuhao Wang; Zichen Wen; Luo Zhongwei; Chang Zou; Zhipeng Zhang; Chuan Wen; Linfeng Zhang",
        "display": "EfficientVLA",
        "venue": "arXiv",
    },
    "2607.06370": {
        "title": "ActionCache: Training-Free Acceleration for Vision-Language-Action Models with Action Caching and Refinement",
        "authors": "Ryuji Oi; Hikari Otsuka; Kosuke Matsushima; Yuki Ichikawa; Masato Motomura; Tatsuya Kaneko; Daichi Fujiki",
        "display": "ActionCache",
        "venue": "arXiv",
    },
    "2605.29438": {
        "title": "ElegantVLA: Learning When to Think for Efficient Vision-Language-Action Models",
        "authors": "Ye Li; Huanan Liu; Kangye Ji; Yuan Meng; Jiajun Fan; Yuansong Wang; Shiyu Qin; Chenglei Wu; Shu-Tao Xia; Zhi Wang",
        "display": "ElegantVLA",
        "venue": "arXiv",
    },
    "2606.03784": {
        "title": "Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation",
        "authors": "Nan Sun; Yuan Zhang; Yongkun Yang; Wentao Zhao; Peiyan Li; Jun Guo; Wenxuan Song; Pengxiang Ding; Runze Suo; Yifei Su; Xin Xiao; Xinghang Li; Huaping Liu",
        "display": "ERVLA",
        "venue": "arXiv",
    },
    "2407.08693": {
        "title": "Robotic Control via Embodied Chain-of-Thought Reasoning",
        "authors": "Michał Zawalski; William Chen; Karl Pertsch; Oier Mees; Chelsea Finn; Sergey Levine",
        "display": "ECoT",
        "link": "https://arxiv.org/abs/2407.08693",
        "venue": "arXiv",
    },
    "2604.21254": {
        "title": "Hyperloop Transformers",
        "authors": "Abbas Zeitoun; Lucas Torroba-Hennigen; Yoon Kim",
        "display": "Hyperloop Transformers",
        "venue": "ICML",
    },
    "2605.23872": {
        "title": "Training-Free Looped Transformers",
        "authors": "Lizhang Chen; Jonathan Li; Chen Liang; Ni Lao; Qiang Liu",
        "display": "Training-Free Looped Xfmr",
        "venue": "arXiv",
    },
    "2605.16343": {
        "title": "LoopQ: Quantization for Recursive Transformers",
        "authors": "Rui Fang; Hsi-Wen Chen; Ming-Syan Chen",
        "display": "LoopQ",
        "venue": "arXiv",
    },
    "2602.07845": {
        "title": "Recurrent-Depth VLA: Implicit Test-Time Compute Scaling of Vision-Language-Action Models via Latent Iterative Reasoning",
        "authors": "Yalcin Tur; Jalal Naghiyev; Haoquan Fang; Wei-Chuan Tsai; Jiafei Duan; Dieter Fox; Ranjay Krishna",
        "display": "Recurrent-Depth VLA (RD-VLA)",
        "venue": "arXiv",
    },
    "2505.08243": {
        "title": "Training Strategies for Efficient Embodied Reasoning",
        "authors": "William Chen; Suneel Belkhale; Suvir Mirchandani; Oier Mees; Danny Driess; Karl Pertsch; Sergey Levine",
        "display": "ECoT-Lite (train-time reasoning)",
        "venue": "arXiv",
        "category_override": "Train-time Reasoning · Deploy No-CoT",
    },
    "2601.09708": {
        "title": "Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning",
        "authors": "Chi-Pin Huang; Yunze Man; Zhiding Yu; Min-Hung Chen; Jan Kautz; Yu-Chiang Frank Wang; Fu-En Yang",
        "display": "Fast-ThinkAct",
        "venue": "arXiv",
        "category_override": "Efficient / Adaptive CoT Compute (Explicit-Lang Plans→Actions)",
    },
    "2507.10524": {
        "title": "Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation",
        "authors": "Sangmin Bae; Yujin Kim; Reza Bayat; Sungnyun Kim; Jiyoun Ha; Tal Schuster; Adam Fisch; Hrayr Harutyunyan; Ziwei Ji; Aaron Courville; Se-Young Yun",
        "display": "MoR",
        "venue": "NeurIPS",
    },
}

FULL_17COL = {
    "VLA-IE-014": {
        "Track ID": "VLA-IE-014",
        "Year": "2025",
        "Venue / Source": "arXiv",
        "Title": "Training Strategies for Efficient Embodied Reasoning",
        "Authors": "William Chen; Suneel Belkhale; Suvir Mirchandani; Oier Mees; Danny Driess; Karl Pertsch; Sergey Levine",
        "Key Affiliation": "Stanford; Berkeley",
        "Paper Link": "https://arxiv.org/abs/2505.08243",
        "Code Link": "NA",
        "Method Category": "Train-time Reasoning · Deploy No-CoT (ECoT-Lite family)",
        "VLA Target": "Embodied CoT VLAs (ECoT-finetuned checkpoints)",
        "Training-Free?": "NO — requires reasoning supervision during training",
        "Reported Speedup": "Up to ~3× inference speedup over standard robot reasoning (author-reported, LIBERO-90, table 2 abstract)",
        "Primary Metric": "Task success rate (LIBERO-90) vs wall-clock inference time",
        "Evaluated On / Dataset": "LIBERO-90; ablations on RT-X-style robot reasoning variants",
        "Key Mechanism": "(1) Why ECoT works: representation learning, curricularization, expressivity; (2) 3 lightweight train-time reasoning recipes: single-step hint, plan-only, stepwise; (3) deployment: no explicit autoregressive CoT decoding → faster inference",
        "Relevance to BudgetLoop-VLA": "Direct training-style efficient reasoning CONTROL: we compare our frozen-training-free BudgetLoop against a train-time-supervised fast-ECoT-Lite baseline; their 3× speedup is the ceiling our training-free approach must approach.",
        "Gaps BudgetLoop Exploits": "ECoT-Lite needs training-time reasoning supervision (π_finetune NOT allowed in frozen setting); static recipe per task vs BudgetLoop dynamic K per step; no compute bank / loop / difficulty gating; grounded vs semantic CoT not tiered.",
        "Notes": "Commit 2.1 full-row rewrite; arXiv 2505.08243 verified; OLD Looped-Transformer / old-language-paper content removed.",
    },
    "VLA-IE-015": {
        "Track ID": "VLA-IE-015",
        "Year": "2026",
        "Venue / Source": "arXiv",
        "Title": "Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning",
        "Authors": "Chi-Pin Huang; Yunze Man; Zhiding Yu; Min-Hung Chen; Jan Kautz; Yu-Chiang Frank Wang; Fu-En Yang",
        "Key Affiliation": "NVIDIA; CMU; Academia Sinica",
        "Paper Link": "https://arxiv.org/abs/2601.09708",
        "Code Link": "NA",
        "Method Category": "Latent CoT Distillation / Verbalizable Compact Planning",
        "VLA Target": "Reasoning VLA (long-horizon, failure recovery, few-shot)",
        "Training-Free?": "NO — requires teacher CoT distillation + preference-guided training",
        "Reported Speedup": "Up to 89.3% inference-latency reduction over explicit-CoT baselines (author-reported §table on long-horizon sim/real tasks)",
        "Primary Metric": "Task success; latency p50/p95; few-shot sim2real adaptation accuracy; failure recovery rate",
        "Evaluated On / Dataset": "Long-horizon 3D tabletop sim + real robot; few-shot adaptation splits; failure recovery scenarios",
        "Key Mechanism": "(1) Verbalizable latent planning space (interpretable compressed plans not full language tokens); (2) Teacher CoT distillation on explicit-reasoning traces; (3) Preference-guided trajectory alignment for plan→action stability; (4) Long-horizon planning + failure recovery + few-shot transfer.",
        "Relevance to BudgetLoop-VLA": "Latent-CoT efficient-reasoning BASELINE for ablation P6: when BudgetLoop Deliberate-mode uses 2-step compressed planning (grounded-only, no semantic autoregressive tokens) it is a training-free approximation of Fast-ThinkAct distilled latent plan — no distillation cost, direct frozen weights.",
        "Gaps BudgetLoop Exploits": "Requires teacher+student distillation pipeline + preference data (CANNOT run on plain frozen checkpoint in 0-training setup); single-scheduler no compute bank / no K loop / no dynamic TTL-tiered cache across modalities; no forced latency-deadline hard-guard.",
        "Notes": "Commit 2.1 full-row rewrite; arXiv 2601.09708 Fast-ThinkAct verified; OLD loop-theory / sample-complexity content removed.",
    },
}

PENDING_TAG_TEMPLATES = {
    "VLA-IE-016": "VERIFICATION_STATUS=PENDING; authoritative_sources=0; Commit 2.1 Hotfix; arXiv/S2 search exact-title: 0 hits; do not treat as verified baseline",
    "VLA-IE-017": "VERIFICATION_STATUS=PENDING; authoritative_sources=0; Commit 2.1 Hotfix; arXiv/S2 search exact-title: 0 hits; do not treat as verified baseline",
}

TRACK_PATCHES: "dict[str, dict]" = {
    "VLA-IE-001": {"arxiv_id": "2506.07639"},
    "VLA-IE-002": {"arxiv_id": "2502.02175"},
    "VLA-IE-003": {"arxiv_id": "2506.10100"},
    "VLA-IE-004": {"arxiv_id": "2607.06370"},
    "VLA-IE-005": {"arxiv_id": "2605.29438"},
    "VLA-IE-006": {"arxiv_id": "2606.03784"},
    "VLA-IE-008": {"arxiv_id": "2407.08693"},
    "VLA-IE-009": {"arxiv_id": "2507.10524"},
    "VLA-IE-010": {"arxiv_id": "2604.21254"},
    "VLA-IE-011": {"arxiv_id": "2605.23872"},
    "VLA-IE-012": {"arxiv_id": "2605.16343"},
    "VLA-IE-013": {"arxiv_id": "2602.07845"},
    "VLA-IE-014": {"arxiv_id": "2505.08243"},
    "VLA-IE-015": {"arxiv_id": "2601.09708"},
}

_KNOWN_TITLES = [
    "Fast ECoT: Efficient Embodied Chain-of-Thought via Thoughts Reuse",
    "VLA-Cache: Efficient Vision-Language-Action Manipulation via Adaptive Token Caching",
    "EfficientVLA: Training-Free Acceleration and Compression for Vision-Language-Action Models",
    "ActionCache: Training-Free Acceleration for Vision-Language-Action Models with Action Caching and Refinement",
    "ElegantVLA: Learning When to Think for Efficient Vision-Language-Action Models",
    "Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation",
    "Robotic Control via Embodied Chain-of-Thought Reasoning",
    "Mixture-of-Recursions: Learning Dynamic Recursive Depths for Adaptive Token-Level Computation",
    "Hyperloop Transformers",
    "Training-Free Looped Transformers",
    "LoopQ: Quantization for Recursive Transformers",
    "Recurrent-Depth VLA: Implicit Test-Time Compute Scaling of Vision-Language-Action Models via Latent Iterative Reasoning",
    "Training Strategies for Efficient Embodied Reasoning",
    "Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning",
]

def normalize_notes(notes: str, FORBIDDEN_PHRASES: list[str]) -> str:
    if not notes:
        return ""
    s = notes
    for p in FORBIDDEN_PHRASES:
        s = s.replace(p, "")
    ids_collected = []
    ctv_any_pat = _re.compile(r"CANONICAL_TITLE_VERIFIED:", flags=_re.IGNORECASE)
    arxiv_id_pat = _re.compile(r'arXiv:([0-9]{4}\.[0-9]{5})')
    for m in ctv_any_pat.finditer(s):
        for mid in arxiv_id_pat.finditer(s, m.start()):
            ids_collected.append(mid.group(1))
            break
    ctv_stubborn = _re.compile(r"CANONICAL_TITLE_VERIFIED:[^|]*", flags=_re.IGNORECASE)
    s_clean = ctv_stubborn.sub("", s)
    for t in _KNOWN_TITLES:
        s_clean = s_clean.replace(t, "")
    s_clean = _re.sub(r"\s*\|\s*(\s*\|\s*)+", " | ", s_clean)
    pieces = _re.split(r"\s*\|\s*", s_clean)
    cleaned_pieces = []
    for p in pieces:
        ps = p.strip(" ;|")
        if ps:
            cleaned_pieces.append(ps)
    s_clean = " | ".join(cleaned_pieces).strip()
    ids = sorted(set(ids_collected))
    if ids:
        short_tag = (
            "CANONICAL_TITLE_VERIFIED: arXiv:" + ",".join(ids) +
            " @ 2026-08-06; ROADMAP commit 2+2.1 auditor-sync"
        )
        parts = [s_clean, short_tag] if s_clean else [short_tag]
        s_clean = " | ".join(parts)
    return s_clean.strip()


def _apply_once() -> int:
    with open(VLA_CSV, "r", encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
        fieldnames = list(rows[0].keys()) if rows else []
    n_patched = 0
    FORBIDDEN_PHRASES = [
        "Looped Transformers Are Better In-Context Learners",
        "Better In-Context Learners",
        "From Recurrent to Looped: A Unified View of Weight-Sharing",
        "Unified View of Weight-Sharing",
        "From Recurrent to Looped",
        "OLD_TITLE=",
    ]

    GLOBAL_BAD_REPLACEMENTS = {
        "1B non-loop": "single-depth 1B-param",
        "Generic Transformer": "General-purpose Transformer backbone",
    }
    for r in rows:
        r["Notes"] = normalize_notes(r.get("Notes") or "", FORBIDDEN_PHRASES)
        tid = r.get("Track ID", "")
        if tid in TRACK_PATCHES:
            meta_id = TRACK_PATCHES[tid]["arxiv_id"]
            M = CANONICAL[meta_id]
            r["Title"] = M["title"]
            r["Authors"] = M["authors"]
            if M.get("venue"):
                r["Venue / Source"] = M["venue"]
            if M.get("link"):
                r["Paper Link"] = M["link"]
            elif tid == "VLA-IE-002":
                r["Paper Link"] = "https://arxiv.org/abs/2502.02175"
            if M.get("reported_speedup"):
                r["Reported Speedup"] = M["reported_speedup"]
            if M.get("category_override"):
                r["Method Category"] = M["category_override"]
            tag = f"CANONICAL_TITLE_VERIFIED: arXiv:{meta_id} @ 2026-08-06; ROADMAP commit 2/7 auditor-sync"
            existing = (r.get("Notes") or "").strip()
            if tag not in existing:
                r["Notes"] = (existing + " | " + tag) if existing else tag
            n_patched += 1
        if tid in FULL_17COL:
            patch_17 = FULL_17COL[tid]
            for col, val in patch_17.items():
                if col in r:
                    r[col] = val
        if tid in PENDING_TAG_TEMPLATES:
            tag = PENDING_TAG_TEMPLATES[tid]
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
            if tid not in TRACK_PATCHES:
                n_patched += 1
        r["Notes"] = normalize_notes(r.get("Notes") or "", FORBIDDEN_PHRASES)
        for col, old_val in list(r.items()):
            if not old_val:
                continue
            new_val = old_val
            for bad, rep in GLOBAL_BAD_REPLACEMENTS.items():
                new_val = new_val.replace(bad, rep)
            if new_val != old_val:
                r[col] = new_val
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        w.writeheader()
        w.writerows(rows)
    os.replace(OUT, VLA_CSV)
    return n_patched


def main():
    SELF_TEST = len(sys.argv) >= 2 and sys.argv[1] == "--self-test-idempotent"

    if SELF_TEST:
        p = pathlib.Path(VLA_CSV)
        before_bytes = p.read_bytes()
        sha_before = hashlib.sha256(before_bytes).hexdigest()

        n1 = _apply_once()
        sha_run1 = hashlib.sha256(p.read_bytes()).hexdigest()

        n2 = _apply_once()
        after_bytes = p.read_bytes()
        sha_run2 = hashlib.sha256(after_bytes).hexdigest()

        total_rows = len(list(csv.DictReader(open(VLA_CSV, encoding="utf-8-sig"))))

        print(f"[self-test-idempotent] run-1 patched={n1}/{total_rows}  run-2 patched={n2}/{total_rows}")
        print(f"[self-test-idempotent] sha_before = {sha_before}")
        print(f"[self-test-idempotent] sha_run1   = {sha_run1}")
        print(f"[self-test-idempotent] sha_run2   = {sha_run2}")

        if sha_run1 != sha_run2:
            lines_r1 = before_bytes.decode("utf-8-sig").splitlines(keepends=True)
            lines_r2 = after_bytes.decode("utf-8-sig").splitlines(keepends=True)
            diff = list(difflib.unified_diff(lines_r1, lines_r2, lineterm="", n=3))
            print("[self-test-idempotent] FAIL: run-1 != run-2 output bytes! First diff lines:")
            for line in diff[:30]:
                print("  " + line)
            sys.exit(9)
        else:
            print("[self-test-idempotent] Idempotent OK (sha_run1 == sha_run2)")
        return

    n_patched = _apply_once()
    total_rows = len(list(csv.DictReader(open(VLA_CSV, encoding="utf-8-sig"))))
    print(f"[commit2-corrections] Patched {n_patched} / {total_rows} rows in-place.")

if __name__ == "__main__":
    main()
