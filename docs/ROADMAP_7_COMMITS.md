# 7-Commit Corrective Roadmap (AsakaTigar/Robotics-TopConf-Analysis-2024-2026)

> Source: `docs/AUDIT_REPORT.md` · Auditor date: 2026-08-06 · Start commit: `aab11f8`
>
> Rule: **Each commit is atomic. Do not squash adjacent commits.** Each one has
> a single clearly-verifiable exit gate described below.

---

## Commit 1 — `quarantine placeholder and unverified entries`

**Why.** 19/120 catalogue rows contain placeholder-author patterns (`John Doe`,
`Jane Smith`, `Bob Smith`, `Alice Johnson`, `Zhang San`). 3 more are
`DATA_QUALITY=REVIEW`. These rows still inflate every public counter in the
repository, which gives the external impression of fabricated entries, not
merely an incomplete collection. The correct fix is **physical quarantine**,
not yet another warning banner.

**Scope of change.**

| Before (flat)                                       | After (partitioned)                                                                                |
| --------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| `datasets/robotics_papers_2024_2026_analysis.csv`   | `datasets/robotics_papers_2024_2026_analysis.csv` — **immutable backward-compatible master source** |
| (all 120 rows rendered in the README)               | `datasets/verified_papers.csv` — only rows with **no DQ flag** in `Notes` (~97–98 rows)             |
|                                                     | `datasets/pending_verification.csv` — `PLACEHOLDER_AUTHORS` ∪ `REVIEW` rows (~22)                  |
|                                                     | `datasets/predicted_trends.csv` — `Year=2026` rows (trend topics, NOT accepted venue papers)        |
|                                                     | `datasets/rejected_or_synthetic.csv` — reserved (empty on commit 1)                                 |

`scripts/build_readme.py` refactor:

1. New helper `partition_rows(all_rows) -> (verified, pending, predicted)`.
2. README badge strip, Overview table, venue counts, robot-type distribution
   and the Trends-by-Venue yearly matrix **all read `verified` only**.
3. Badge strip adds three clearly-labelled pills:
   - `Verified` (brightgreen, ~98 rows)
   - `Pending` (yellow, ~22 rows — not red alert; it's a pipeline status)
   - `Predicted` (informational, ~2026 count only)
4. "## 📅 2026 — Emerging Trends (Predicted)" section reads from
   `predicted_trends.csv` and its title explicitly reads "Predicted", never
   counted in the Total papers badge.
5. **No `verification_status` column yet** (that is commit 3). The partition
   in commit 1 is 100 % derived from the existing `Notes` + `Year` fields.

**Exit gates for commit 1.**

- [ ] `Grep README.md README.zh-CN.md "John Doe\|Jane Smith\|Bob Smith\|Alice Johnson\|Zhang San"` returns **0 matches**.
- [ ] Verified badge count matches `datasets/verified_papers.csv` exactly.
- [ ] The "Total" Overview row = `datasets/verified_papers.csv` row count (no longer 120).
- [ ] 2026 rows still display, in their own demarcated section, and do not enter venue statistics.
- [ ] Old `datasets/robotics_papers_2024_2026_analysis.csv` still exists exactly as before (backward compat).

---

## Commit 2 — `correct canonical titles, arXiv IDs, authors and reported numbers`

**Why.** Research-track identity errors (wrong arXiv IDs, wrong canonical
titles, nicknames treated as titles, mis-attributed speedup numbers)
invalidate the evidence chain of the VLA track. The auditor flagged 6
confirmed cases plus a harmonisation request for 3 more.

**Concrete cases to resolve, in order (see AUDIT_REPORT §1.2):**

1. Fast ECoT → canonical title `Fast ECoT: Efficient Embodied Chain-of-Thought via Thoughts Reuse`, arXiv `2506.07639`. Report "up to ~7.5 % latency reduction" in the `reported_speedup` field; **delete any 1.5–3× end-to-end prose**.
2. ECoT → arXiv `2407.08693`, canonical title `Robotic Control via Embodied Chain-of-Thought Reasoning`. Delete `2501.12148` reference.
3. VLA-IE-014 → decide if the row is "Training Strategies for Efficient Embodied Reasoning (ECoT-Lite) arXiv `2505.08243`" or the Looped-Xfmr paper. If it is ECoT-Lite, retitle; if not, swap `arxiv_id`.
4. VLA-IE-015 → re-label as `Fast-ThinkAct`, arXiv `2601.09708`, efficient-VLA-reasoning bucket.
5. ERVLA → canonical title `Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation` (arXiv `2606.03784`). Move nickname `ERVLA` to a new `model_family` / `summary` field.
6. LoopQ / Hyperloop / RD-VLA → separate `canonical_title` from a new `display_summary`. Author-given canonical titles are stored verbatim.
7. ActionCache → speedup numbers aligned to latest public draft version; note `version_checked`.
8. VLA-Cache → canonical title + speedup + training-free flag re-verified against latest draft.
9. ElegantVLA → canonical title + training condition + scheduler description harmonised.

**Exit gates for commit 2.**

- [ ] Auditor's 6 named identity cases resolved one-by-one; decisions recorded in `docs/data_verification_log_2026_08.md`.
- [ ] Every row in `research_tracks/vla_inference_efficiency_2024_2026.csv` has a non-empty `arxiv_id` that resolves to a 200 on `https://arxiv.org/abs/<id>`.
- [ ] No duplicate `arxiv_id` inside the VLA track CSV.
- [ ] `reported_speedup` field: every numeric claim cites an author-given number and unit, never a free-text multiple that is unsupported by the abstract.

---

## Commit 3 — `introduce strict CSV schema and verification_status`

**Why.** So far DQ state is encoded as ad-hoc strings inside a free-form
`Notes` column. This makes `build_readme.py` filters brittle and blocks the
CI gates (commit 4). Replace implicit with explicit.

**Add schema-enforced columns** (do NOT drop old columns in commit 3; add
alongside, migrate one field at a time). Fields enumerated in
AUDIT_REPORT §1.3:

```text
paper_id  canonical_title  display_title  authors  year  venue  venue_status
arxiv_id  doi  paper_url  code_url  version_checked  verified_at
verification_status  claim_source  reported_hardware  reported_speedup
```

`verification_status` values (enum, case-insensitive on CSV read):

```text
verified | partially_verified | pending | rejected
```

Back-population rule in commit 3 for existing rows:

| Old `Notes` content                                         | `verification_status` |
| ----------------------------------------------------------- | --------------------- |
| No `DATA_QUALITY=*` flag, year ∈ {2024,2025}                | `partially_verified`  |
| `DATA_QUALITY=REVIEW`                                       | `partially_verified`  |
| `DATA_QUALITY=PLACEHOLDER_AUTHORS`                          | `pending`             |
| Year=2026, trend                                            | `pending`             |

**Marking a row `verified` is a manual per-row action after identity audit**
— only rows that passed commit 2's VLA identity audit plus a 2024/2025
back-population sweep receive `verification_status = verified`.

**Exit gates for commit 3.**

- [ ] Both master CSV and VLA-track CSV carry the new columns.
- [ ] `verification_status` contains only the 4 enum values; no empty cells.
- [ ] A schema file `schemas/paper.schema.json` exists and can validate the CSV (use `csv-schema` or equivalent lightweight validator).
- [ ] `scripts/build_readme.py` now reads from the explicit enum, no longer greps `Notes` for `DATA_QUALITY=*` strings.

---

## Commit 4 — `add validation CI and README consistency test`

**Why.** Without automated gates, commits 1–3 regress immediately on the next
manual CSV edit. This commit introduces `scripts/validate_data.py` and a
GitHub Actions workflow.

**Hard gates listed in AUDIT_REPORT §1.4:**

1. ❌ Author field on any `verified` row matches `John Doe|Jane Smith|Bob Smith|Alice Johnson|Zhang San`.
2. ❌ `verification_status=verified` with empty `paper_url`.
3. ❌ Duplicate `arxiv_id` across any row (pending OR verified — catches accidental dupes too).
4. ❌ Empty `canonical_title`.
5. ❌ `venue_status=accepted` with empty `claim_source`.
6. ❌ `README.md != build_readme.py` output — block PR merge if the on-disk README is older than the CSV or generator.

**CI file:** `.github/workflows/validate.yml` — runs on every push to `main`
and on every PR.

**Exit gates for commit 4.**

- [ ] A workflow file exists in `.github/workflows/validate.yml`.
- [ ] `python scripts/validate_data.py` runs in CI; exit 0 on current main after applying commits 1–3.
- [ ] `scripts/validate_data.py` intentionally-failing inputs (duplicate arXiv, placeholder author on a verified row, etc.) produce exit-code ≠ 0.
- [ ] README-drift check: `scripts/validate_data.py --readme-build-check` fails if READMEs differ from fresh build output.

---

## Commit 5 — `reframe landing page around Robotics CoT taxonomy`

**Why.** The current homepage position ("Robotics Top Conference Papers —
ICRA/IROS/RSS/CoRL") is too broad and does not match where the repository
actually has momentum (Embodied CoT, reasoning VLA, test-time compute,
adaptive inference). Broadening dilutes the core message.

**Choose ONE of two headline options** (per AUDIT_REPORT §2):

- (A) Rename the repository to `Robotics-CoT-Atlas`.
  Subtitle:
  > *A Verified Taxonomy and Benchmark Map of Explicit, Visual, Action and
  > Latent Reasoning for Robot Policies.*

- (B) Keep slug, rewrite H1:
  > **Embodied Chain-of-Thought and Test-Time Compute for Robotics** — a
  > verified catalogue and benchmark map.

Either way, legacy general-robotics 4-venue rows move under

```
catalog/topconf_general_robotics/
```

and are **not** on the first screen of the landing README.

**Primary classifier on the landing page becomes the reasoning-mechanism
taxonomy (AUDIT_REPORT §2.1), NOT the robot-body classifier.** Six top-level
tracks: Explicit-Language CoT / Visual CoT / Grounded-Action CoT /
Latent-Recurrent Reasoning / Train-Time-Reasoning Deploy-No-CoT /
Efficient-Adaptive-CoT-Compute. Each track links to its sub-page under
`tracks/<slug>/`.

**Exit gates for commit 5.**

- [ ] H1 and sub-title of `README.md` and `README.zh-CN.md` no longer claim to be a general 4-venue topconference awesomelist.
- [ ] First 2 screens of the README describe the 6 reasoning-mechanism tracks, not robot bodies.
- [ ] General-robotics legacy data lives under `catalog/topconf_general_robotics/`, clearly demarcated as archive / reference.
- [ ] Bilingual language switcher still works top-right (never regress this).

---

## Commit 6 — `rewrite BudgetLoop proposal with exact checkpoint, hard deadlines and statistically valid evaluation`

**Why.** BudgetLoop-VLA's core idea (accelerator → allocator) has submission
potential, but the current proposal carries six blocking scientific holes
enumerated in AUDIT_REPORT §3.2. They must be resolved before any GPU
minutes are spent on real training.

**Ordered fixes inside `proposals/budgetloop_v2.md`:**

1. **Specify the exact checkpoint carrier.** Never say "frozen 1B ECoT VLA" without
   a name. Fill: checkpoint name · param count · vision encoder · language
   backbone · action decoder · CoT token format · public weights URL · loop
   insertion layers · cacheable tensors. Do NOT lock "1B" without the P0
   feasibility audit (OpenVLA is 7B — this needs resolving).

2. **Split budget constraints into mean + hard.** `mean(c_t) ≤ B_avg` and
   `c_t ≤ D_hard` on separate lines. Add new KPIs table: deadline miss
   rate, p99 latency, maximum latency, action jitter, control-interval
   variance, emergency fallback frequency.

3. **Unify the bank currency.** Master currency = synchronised end-to-end
   wall-clock ms @ batch size = 1. FLOPs, memory, energy live in a separate
   supplementary-metrics table.

4. **Per-difficulty-signal cost table.** Signal v0 set (only cheap ones):
   action inconsistency across K repeats, cache miss ratio, hidden-state
   residual/norm delta. Augment signals (grounding entropy, gripper-object
   distance, mini-refresh forward, attention entropy) → v1+, with per-signal
   latency, memory and module-availability rows filled.

5. **Statistical evaluation protocol upgrade.** ≥ 5 independent seeds;
   episode-success paired bootstrap + permutation test + mixed-effect logistic
   regression; latency episode-level bootstrap CI; task- and episode-level
   CIs both reported; multiplicity correction across
   budgets/thresholds/models. Pass gating is `Δ success ≥ 2 percentage
   points` ∧ `95 % CI excludes 0` ∧ `deadline_miss_rate ≤ baseline` — NOT
   a naked `p < 0.05`.

6. **Remove "Already passed our prior reading" claims.** Replace with
   `Status: UNVERIFIED` + explicit evidence list (checkpoint profiler,
   50–100 closed-loop episodes, per-field CoT change-rate logs, cache-hit
   distribution).

**Exit gates for commit 6.**

- [ ] Every one of the 6 blocking fixes has a visibly-completed sub-section in `proposals/budgetloop_v2.md`.
- [ ] No "1B" claim survives without a concrete checkpoint URL.
- [ ] New statistical evaluation table explicitly lists the 6 reporting columns and the 3-way passing gate.
- [ ] Difficulty-signal cost table exists with v0/v1 tiers separated.

---

## Commit 7 — `add benchmark matrix and executable baseline roadmap`

**Why.** Without 12 baselines the BudgetLoop contribution collapses to
"cache + heuristic gating + loop engineering" in any competent reviewer's
mind. The 12 baselines are not optional.

**Full baseline matrix (AUDIT_REPORT §4):**

| #  | Baseline                                                     | Tier / purpose                   |
|----|--------------------------------------------------------------| ---------------------------------|
| 1  | Full-reasoning VLA, no acceleration                         | Upper-reference accuracy         |
| 2  | Fixed shallow / fixed K=1                                    | Fixed-compute lower baseline     |
| 3  | Cache-only (KV / token / vision cache as applicable)        |                                  |
| 4  | Fast ECoT                                                    | Existing efficient explicit-CoT  |
| 5  | VLA-Cache                                                    | Existing cache-VLA baseline      |
| 6  | ActionCache                                                  | Action-head acceleration baseline|
| 7  | ElegantVLA-style dynamic per-module scheduler                | Dynamic-scheduling baseline      |
| 8  | Threshold scheduler, **no cross-step bank**                  | ← *key ablation control*         |
| 9  | **Bank enabled, loop disabled**                              | ← *key ablation control*         |
| 10 | **Loop enabled, bank disabled**                              | ← *key ablation control*         |
| 11 | Oracle difficulty allocation (ceiling)                       | Upper bound (unrealistic)        |
| 12 | Random allocation with same mean budget (negative control)   | Baseline sanity check            |

**Primary scientific claim — ablation #8 + #9 + #10 isolate it:**

> *Given the same mean compute envelope and the same difficulty estimator, a
> temporally-banked policy strictly outperforms a stepwise threshold
> scheduler on success rate without increasing deadline misses.*

This claim is BudgetLoop-VLA's unique contribution. **Commit 7 explicitly
marks it as the headline result in `docs/benchmark_protocol.md`.**

**Exit gates for commit 7.**

- [ ] Baseline matrix (#1–#12) lives in `docs/benchmark_protocol.md` and in `proposals/budgetloop_v2.md § Baselines`.
- [ ] Headline unique-contribution claim is stated verbatim above, highlighted, and cross-linked to the ablation rows #8/#9/#10.
- [ ] Each baseline carries a one-line "why it exists" entry so reviewers never argue BudgetLoop is a mere re-implementation soup.
- [ ] `scripts/benchmark_roadmap.py` (or equivalent executable table) reports: checkpoint, environment, #episodes, failure modes, target D_hard / B_avg for each of the 12 rows.

---

## End-state repository skeleton (all 7 commits applied)

```
Robotics-CoT-Atlas/
├── README.md   README.zh-CN.md
├── CITATION.cff   CONTRIBUTING.md
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
└── .github/workflows/validate.yml
```
