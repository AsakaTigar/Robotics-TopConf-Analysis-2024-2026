# Auditor's Report — Robotics TopConf Analysis (v0.2, 2026-08-06)

> Auditor: Cross-model external review backend (xhigh reasoning).
> Scope: `AsakaTigar/Robotics-TopConf-Analysis-2024-2026` commit `aab11f8`
> Intended audience: repository owner; **this document is the source-of-truth for the next 7 corrective commits**.

---

## Executive verdict

**Direction worth pursuing, but the repository MUST NOT be cited publicly as a
credible Robotics-CoT paper library or research evidence yet.**

Composite scorecard:

| Dimension                         | Score |
| --------------------------------- | ----: |
| Topic potential                   |  8/10 |
| BudgetLoop-VLA method concept     |  7/10 |
| Paper-data trustworthiness        |  3/10 |
| Repository engineering quality    |  5/10 |
| Reproducibility                   |  4/10 |
| Public-positioning clarity        |  4/10 |

What already works and should be preserved:

- `data_quality/` · `research_tracks/` · `proposals/` · `scripts/` folder layout
- Bilingual README with top-of-page language switcher
- VLA Inference Efficiency track pulled out as a standalone research line
- BudgetLoop-VLA proposal separated from the general catalogue
- 2024 → 2025 → 2026 reverse order, baseline Gap natural-sentence mapping
- All DQ visual alerts removed from the public README UX (commit `decb1d6`)

**What is broken and blocks publication credibility:**

1. **19 / 120 rows = PLACEHOLDER_AUTHORS; 4 rows = REVIEW.** 15.8 % of the
   displayed catalogue is synthetic (`John Doe`, `Jane Smith`, `Bob Smith`,
   `Alice Johnson`, `Zhang San` patterns). **These rows still enter the paper
   counts, venue statistics and trend charts.** This is externally perceived
   as *fabricated entries*, not merely incomplete collection.
2. **Research-track CSV has multiple identity errors — canonical titles,
   arXiv IDs, authors and reported numbers cannot be trusted in their current
   form.** Concrete confirmed errors are enumerated in §2 below.
3. **The builder knows about `DATA_QUALITY=*` but does not actually quarantine
   rows.** Overview, venue counts, robot-type distributions all mix verified +
   placeholder rows. `Training-Free?` is matched by a brittle string set.

---

## 1. P0 fixes (commit 1 of roadmap — do these FIRST)

### 1.1 Physically quarantine synthetic / unverified rows

Current (2026-08-06) internal DQ counts from [`datasets/robotics_papers_2024_2026_analysis.csv`](datasets/robotics_papers_2024_2026_analysis.csv):

| Flag                              | Rows | Share |
| --------------------------------- | ---: | ----: |
| `DATA_QUALITY=PLACEHOLDER_AUTHORS`|   19 | 15.8% |
| `DATA_QUALITY=REVIEW`             |    3 |  2.5% |
| Clean / unflagged                 |   98 | 81.7% |
| **Total catalogue rows**          |  120 |      —|

**Required partition layout:**

```
datasets/
├── robotics_papers_2024_2026_analysis.csv   BACKWARD-COMPAT SOURCE OF TRUTH
├── verified_papers.csv                       ONLY rows with no DQ flag
├── pending_verification.csv                  PLACEHOLDER_AUTHORS + REVIEW
├── predicted_trends.csv                      2026-only rows (trend topics,
│                                             NOT yet accepted venue papers)
└── rejected_or_synthetic.csv                 (reserved for audit-validated
                                               rejections or deliberate
                                               synthetic rows)
```

Enforcement rules:

- `README.md` / `README.zh-CN.md` — **papers badge, venue stats, robot-type
  distribution, per-venue counts MUST BE sourced from verified_papers.csv**.
- `pending_verification.csv` MUST NOT contribute to paper totals, venue
  shares or trend charts.
- `predicted_trends.csv` lives in its own section, clearly demarcated, and
  is **NEVER counted in the "Total papers 2024–2025" badge or overview.**

### 1.2 Research-track CSV identity errors (confirmed; commit 2 of roadmap)

| Current label                  | Problem                                                   | Required correction                                                                                                                                                                                                  |
| ------------------------------ | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Fast ECoT                      | Non-canonical title + inflated 1.5–3× end-to-end claim    | Canonical title = **Fast ECoT: Efficient Embodied Chain-of-Thought via Thoughts Reuse** (arXiv:2506.07639). Paper reports up to ~7.5% latency reduction, NOT a 1.5–3× end-to-end speedup.                              |
| ECoT                           | Wrong arXiv ID `2501.12148` (a comms paper)               | Canonical title = **Robotic Control via Embodied Chain-of-Thought Reasoning**. Correct arXiv ID = **2407.08693**.                                                                                                     |
| VLA-IE-014 "Looped Transformers Are Better In-Context Learners" | `2505.08243` mismatch | `2505.08243` is **Training Strategies for Efficient Embodied Reasoning** (ECoT-Lite direction). Retitle accordingly OR relabel row.                                                                                  |
| VLA-IE-015 generic looped-Xfmr | `2601.09708` mismatch                                     | `2601.09708` is **Fast-ThinkAct** (efficient VLA reasoning track).                                                                                                                                                   |
| ERVLA                          | Model name used as paper title                            | Canonical title = **Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation** (arXiv:2606.03784). Model nickname goes in `summary` / `model_family` field, not `canonical_title`.                  |
| LoopQ / Hyperloop / RD-VLA     | Self-invented titles stored as if they were the paper one | Store the author-provided canonical title verbatim in `canonical_title`; put a one-line Chinese/English summarisation in a dedicated `display_summary` column.                                                         |

Additional harmonisation required for **ActionCache** speedup numbers vs the
updated draft; **VLA-Cache** and **ElegantVLA** canonical titles, reported
conditions and training-free flags.

### 1.3 Strict schema + verification_status enum (commit 3)

Mandatory new columns in the master CSV (added **in addition** to, not in
place of, the current Robot Type / Venue / … fields so existing scripts do
not break in one shot):

```text
paper_id                  stable, immutable key      e.g. "VLA-IE-003"
canonical_title           exact title from venue page / arXiv abstract
display_title             optional shortened title for README
authors                   semi-colon separated, surname-ordered, copied
                          verbatim from arXiv API or venue page
year                      integer
venue                     ICRA | IROS | RSS | CoRL | NeurIPS | ICML | arXiv
venue_status              workshop | main | accepted | preprint
arxiv_id                  2407.08693 (no abs/ prefix)
doi                       10.1109/ICRAxxxx...
paper_url                 (resolved final URL, not search)
code_url                  (repo or official project page)
version_checked           e.g. "arXiv v3, 2026-07-28"
verified_at               ISO date
verification_status       verified | partially_verified | pending | rejected
claim_source              paragraph-level pointer for every numerical claim
reported_hardware         (GPU / robot, batch, precision)
reported_speedup          (exact number + unit as reported by authors)
```

README-level filter (commit 1):

```python
PUBLIC_ROWS = [
    row for row in rows
    if row["verification_status"] == "verified"
]
```

Until `verification_status` exists, derive it from `DATA_QUALITY=*` Notes:

```text
no flag        -> verified
REVIEW         -> partially_verified
PLACEHOLDER_*  -> pending
```

### 1.4 Builder / CI hard gates (commit 4)

`scripts/validate_data.py` must pass before PR merge and before README build.

- ❌ Forbid `John Doe|Jane Smith|Bob Smith|Alice Johnson|Zhang San` in `authors`
  on any row with `verification_status=verified`.
- ❌ Forbid `verification_status=verified` rows with an empty `paper_url`.
- ❌ Forbid duplicate `arxiv_id` across all rows.
- ❌ Forbid empty `canonical_title`.
- ❌ Forbid `venue_status=accepted` without a non-empty `claim_source`.
- ❌ Forbid README files that are byte-different from the product of
  `scripts/build_readme.py` against the current CSVs (i.e. manual drift).

Training-Free enum — **stop ad-hoc string matching**. Introduce:

```python
TRAINING_FREE = {"yes", "partial", "no", "analysis", "unknown"}
```

Normalise on read from CSV (case-insensitive → canonical value), never
match an ever-growing list of string variants.

---

## 2. Position (commit 5)

**Stop positioning the landing page as a "general ICRA/IROS/RSS/CoRL awesome
list".** Diluting across UAV, SLAM, soft robots, surgery harms the one axis
where this repository already has momentum: **Embodied CoT / VLA reasoning /
test-time compute allocation / efficient VLA inference**.

Two acceptable new headline positions (pick one):

- (A) **Repository rename** → `Robotics-CoT-Atlas`
  Subtitle:
  > *A Verified Taxonomy and Benchmark Map of Explicit, Visual, Action and
  > Latent Reasoning for Robot Policies.*

- (B) Keep current repository slug but rewrite the H1:
  > **Embodied Chain-of-Thought and Test-Time Compute for Robotics** — a
  > verified catalogue and benchmark map.

Under either option, the legacy ICRA/IROS/RSS/CoRL general-robotics rows
move to:

```
catalog/topconf_general_robotics/robotics_papers_2024_2026_analysis.csv
```

and are NOT the front-page body any more.

### 2.1 Reasoning-mechanism classification, NOT robot-body classification

Replace the primary classifier. New primary axis for the front page:

| Tier            | Name                              | Anchor / starter paper                                        |
| --------------- | --------------------------------- | ------------------------------------------------------------- |
| 1               | Explicit language CoT             | ECoT (Robotic Control via Embodied CoT, 2407.08693)           |
| 2               | Visual CoT                        | CoT-VLA / visual-intermediate-reasoning lines                |
| 3               | Grounded / Action CoT             | ERVLA-style grounded action guidance decoupled from pure-semantic CoT |
| 4               | Latent / recurrent reasoning      | RD-VLA, looped transformer, recurrent-depth families         |
| 5               | Train-time reasoning, deploy no-CoT | ECoT-Lite (2505.08243) and similar                         |
| 6               | Efficient / adaptive CoT compute  | Fast ECoT, VLA-Cache, EfficientVLA, ActionCache, ElegantVLA  |

Per-paper enrichment fields to add for taxonomy credibility:

```text
reasoning_modality             explicit_lang | visual | grounded_action | latent | hybrid
reasoning_stage                train_only | deploy_only | train_and_deploy
reasoning_explicitness         high | medium | low | none
reasoning_granularity          task | subgoal | step | action_chunk | action
reasoning_action_coupling      decoupled | weakly_coupled | tightly_coupled | interleaved
test_time_compute              fixed | conditional | unbounded | budgeted
adaptive_compute               yes_bank | yes_threshold | yes_earlyexit | none
closed_loop_evaluation         yes_sim | yes_real | none
real_robot                     yes | no
latency_reported               ms | fps | steps_per_sec | relative_speedup | not_reported
control_frequency              Hz, or "N/A"
training_required              none (frozen) | light router only | full finetune | full pretrain
```

These 14 columns convert a paper list into a publishable taxonomy.

---

## 3. BudgetLoop-VLA method audit (commit 6)

### 3.1 What to KEEP — the single highest-potential element

**The re-framing from "how to reduce compute?" to "how to reallocate surplus
compute from easy steps to hard steps?" — the *accelerator → allocator* turn
— is novel enough to carry a paper submission.**

Reflex / Refresh / Deliberate triple-mode + cross-step compute bank is a
better contribution shape than isolated cache / pruning / early-exit.
`b_t = clip(b_{t-1} + B - c_t, b_min, b_max)`, stage-wise Go/No-Go and
failure-fallback rules already exist in the proposal.

### 3.2 Six holes that block submission

1. **No exact 1B ECoT-style VLA checkpoint specified.**
   Required: exact checkpoint name, param count, vision encoder, language
   backbone, action decoder, CoT token format, public-weights URL, loop
   insertion layers, cacheable tensors. Do NOT lock "1B" before the P0
   feasibility audit — OpenVLA is 7B, not 1B.

2. **Average latency bank ≠ hard real-time control deadline.**
   Two separate constraints, never conflate:
   ```text
   Long-term:   mean(c_t) ≤ B_avg
   Hard per-step:  c_t ≤ D_hard
   ```
   New primary KPIs — deadline miss rate, p99 latency, maximum latency,
   action jitter, control-interval variance, emergency fallback frequency.

3. **Do not mix FLOPs with milliseconds inside one bank.**
   Main experiment currency = *synchronised, end-to-end wall-clock ms,
   batch-size=1*. FLOPs, memory, energy are side metrics only.

4. **Not every difficulty signal is "free".**
   Mandatory per-signal table:
   ```text
   signal_latency_ms  required_module  available_from_base_fwd?
   additional_bytes   real_robot_availability?
   ```
   Baseline v0 signal set (only cheap ones):
     (a) action inconsistency across K repeats,
     (b) cache miss ratio,
     (c) hidden-state residual / norm delta.
   Everything else (grounding entropy, gripper-object distance, mini-refresh
   forward, attention entropy) lives in a v1+ aug config.

5. **"3-seed paired t-test on episode binary success" is statistically too weak.**
   Upgrade to: fixed-same-seed initial conditions; episode-success paired
   bootstrap / permutation test / mixed-effect logistic regression; latency
   episode-level bootstrap CI; ≥ 5 seeds; task-level AND episode-level CIs;
   multiplicity correction across budgets/thresholds/models.
   Do not gate on `p<0.05` alone — gate on:
     `Δsuccess ≥ 2pp` AND `95% CI excludes 0` AND `deadline_miss_rate ≤ baseline`.

6. **P0 cannot claim "Already passed our prior reading" on cache-hit and
   Reflex-share gates.** These numbers require checkpoint profiling + 50–100
   closed-loop episodes + per-field CoT change-rate logs. Relabel as
   `Status: UNVERIFIED` with evidence requirements enumerated.

---

## 4. Baseline matrix (commit 7)

Core 12 baselines; do not skip any or BudgetLoop-VLA collapses to
"cache + heuristic gating + loop" in reviewer eyes:

| #  | Baseline                                                                 |
|----|--------------------------------------------------------------------------|
| 1  | Full-reasoning VLA, no acceleration at all                              |
| 2  | Fixed shallow / fixed K=1                                                |
| 3  | Cache-only                                                               |
| 4  | Fast ECoT                                                                |
| 5  | VLA-Cache                                                                |
| 6  | ActionCache                                                              |
| 7  | ElegantVLA-style dynamic per-module scheduler                           |
| 8  | Threshold scheduler WITHOUT the cross-step bank                         |
| 9  | Bank WITHOUT the looped-deliberate mechanism                            |
| 10 | Loop WITHOUT the cross-step bank                                        |
| 11 | Oracle difficulty allocation (ceiling / impossible in practice)         |
| 12 | Random allocation, same average budget (negative control)               |

Key scientific claim to isolate in Commit 7 ablation:

> **Given the same mean compute envelope and the same difficulty estimator, a
> temporally-banked policy strictly outperforms a stepwise threshold
> scheduler on success rate without increasing deadline misses.**

This is the BudgetLoop-specific contribution — not the individual existence
of cache, gating or loop.

---

## 5. Target repository skeleton (roadmap end-state)

```
Robotics-CoT-Atlas/
├── README.md  README.zh-CN.md
├── CITATION.cff
├── CONTRIBUTING.md
├── docs/
│   ├── taxonomy.md
│   ├── inclusion_criteria.md
│   ├── verification_protocol.md
│   └── benchmark_protocol.md
├── data/
│   ├── verified_papers.csv
│   ├── pending_papers.csv
│   ├── reported_results.csv
│   └── claim_evidence.csv
├── tracks/
│   ├── explicit_cot/
│   ├── visual_cot/
│   ├── grounded_action_cot/
│   ├── latent_reasoning/
│   └── efficient_reasoning/
├── proposals/
│   └── budgetloop_v2.md
├── schemas/
│   └── paper.schema.json
├── scripts/
│   ├── validate_data.py
│   ├── verify_arxiv_ids.py
│   ├── check_duplicates.py
│   └── build_readme.py
├── tests/
└── .github/workflows/
    └── validate.yml
```

## 6. Final instruction to the repo maintainer

**Do not add more generic general-robotics papers horizontally.** The
highest-value path is:

> *Make this a verified Robotics-CoT taxonomy + VLA-inference benchmark map,
> anchored by a concrete and statistically-sound BudgetLoop-VLA experimental
> plan.*

Once placeholder rows are quarantined, paper-identity errors fixed, and the
BudgetLoop-VLA model-carrier + evaluation protocol locked down, the
repository graduates from an auto-generated Awesome List to a research
asset usable for related-work writing, experiment design, or even a
standalone survey / benchmark submission.
