# Data Verification Log — 2026-08-06 (Commit 2 / 7)

Canonical-title / arXiv-id / author / reported-numbers auditor sync, targeting
the 9 identity-errors + 3 speedup/number corrections flagged in
`docs/AUDIT_REPORT.md` §P0 line items ①–③.

## Method

For every flagged paper we re-query the arXiv Atom API
(`export.arxiv.org/api/query?id_list=...`) and treat the returned `<entry>` as
the single source of truth for: canonical title, author list, and venue
(accept-date will come in the schema verification commit).

Script used: `scripts/arXiv_verify_commit2.py`
Patch script (reproducible): `scripts/apply_commit2_corrections.py`

## Per-Row Decisions

### Auditor P0 item ②(a) — 6 canonical-title / identity mismatches

| Track ID     | Old title / arXiv id (WRONG)                                 | New (arXiv Atom ← truth)                                                                                                                                                                                                                        | Evidence                                                                                                                                                                                                  |
|--------------|--------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **VLA-IE-001 Fast ECoT** | "Fast Embodied Chain-of-Thought via Cross-Step Plan Reuse, Modular Parallelism and Asynchronous Scheduling"; speedup "~1.5x-3x end-to-end"; 2506.07639 | **Title**: `Fast ECoT: Efficient Embodied Chain-of-Thought via Thoughts Reuse`; authors Duan / Zhang / Geng / Liu / Boedecker / Xiaoxuan Lu; **Reported Speedup** replaced with author-given _"Up to ~7.5% end-to-end latency reduction (LIBERO + OpenVLA-ECoT)"_ | arXiv feed 2506.07639 title field exact match; speedup "~1.5x-3x" is not in abstract or paper (self-inserted by a prior reviewer) and is **deleted** entirely; replaced with the author-reported ~7.5% claim. |
| **VLA-IE-008 ECoT — CRITICAL** | Linked to **2501.12148** `Deep Unfolding of Fixed-Point Based Algorithm for WSR Maximization` (a **wireless communications** paper — NOT robotics) | **arXiv id 2407.08693**; title: `Robotic Control via Embodied Chain-of-Thought Reasoning`; authors Zawalski / Chen / Pertsch / Mees / Finn / Levine | Direct cross-ref from the ECoT family; 2501.12148 authors: Hauffen / Tan / Caire (comm theory) — not a robotics work. This was the single highest-severity error in the dataset; "ECoT link = wrong field" corrected entirely. |
| **VLA-IE-014** | Title `Looped Transformers Are Better In-Context Learners`; arXiv 2505.08243. | arXiv 2505.08243 returns `Training Strategies for Efficient Embodied Reasoning` (Chen / Belkhale / Mirchandani / Mees / Driess / Pertsch / Levine — embodied-CoT family). Renamed; category reassigned to Train-time Reasoning · Deploy No-CoT (ECoT-Lite). | **Auditor correct**: "Better In-Context Learners" is a different paper from a different arXiv id (general language LM loop). 2505.08243 is unambiguously embodied reasoning. |
| **VLA-IE-015** | Title `From Recurrent to Looped: A Unified View of Weight-Sharing`; Venue=ICLR; arXiv 2601.09708. | arXiv 2601.09708 returns `Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning` (Huang / Man / Yu / Chen / Kautz / Frank Wang / Fu-En Yang). Renamed; venue downgraded from ICLR → arXiv (acceptance not verified); category moved to Efficient / Adaptive CoT Compute. | Auditor mismatch confirmed 100%. "Unified View of Weight Sharing" — text does not exist anywhere in 2601.09708's title, summary or authors. |
| **VLA-IE-006 ERVLA** | Title = `ERVLA` (nickname stored in Title column); arXiv 2606.03784 OK | Canonical title: `Revisiting Embodied Chain-of-Thought for Generalizable Robot Manipulation` (12 authors, Sun et al. Tsinghua). Nickname `ERVLA` kept as display metadata, Title column holds the official string now. | Standard nickname-vs-title audit. |
| **VLA-IE-010 / IE-012 / IE-013 (Hyperloop / LoopQ / RD-VLA self-invented short titles)** | Hyperloop = `Hyperloop: Efficient Recurrent…` (custom); LoopQ = `LoopQ: Drift-Aware Quantization…` (custom); RD-VLA = `RD-VLA: Recurrent Decoding …` (custom) | All three reverted to arXiv Atom canonical strings: `Hyperloop Transformers` (2604.21254); `LoopQ: Quantization for Recursive Transformers` (2605.16343); `Recurrent-Depth VLA: Implicit Test-Time Compute Scaling of Vision-Language-Action Models via Latent Iterative Reasoning` (2602.07845). Custom nicknames survive only as sort/display helpers (Track Name). | Auditor's "self-summary as canonical title" flag applied uniformly: authors own the title column. |

### Auditor P0 item ②(b) — 3 reported-speedup / number harmonisations

| Track ID       | Old (user-inserted)                                                                        | New (canonical, kept from the original feed when the authors state a number)                                                             | Evidence                                                                                                                                                                                                  |
|----------------|-------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **VLA-IE-001** | `~1.5x – 3x end-to-end` (NOT author-sourced, auditor said FALSE)                          | **Deleted** the fabricated claim entirely. Replaced with the author-abstract wording: _"Up to ~7.5% end-to-end latency reduction (author-reported §1) on LIBERO + OpenVLA-ECoT; old ~1.5x–3x NOT cited."_ | Authors' abstract 2506.07639 never uses the phrase "1.5x" or "3x". 1.5–3× was inserted by a prior data curator without a source. Auditor was correct.                                                     |
| **VLA-IE-004 ActionCache** | Reported speedup `π0: 11.75×; GR00T-N1.6: 34.43× latency improvement (table 2)`             | **Kept author-reported numbers** (are present in the latest ActionCache preprint tables); appended `CANONICAL_NUMBERS_VERIFIED: 2607.06370 v1` audit log tag to Notes only — numbers unchanged.              | Numbers match what is in 2607.06370 Table 2; no fabrication here — only sync-tag added.                                                                                                                    |
| **VLA-IE-002 VLA-Cache / VLA-IE-005 ElegantVLA** | Title stored as a self-invented one-paragraph prose summary.                               | Title column swapped for the arXiv Atom feed canonical titles exactly. Speedup numbers **kept as-is** (are table-based in the authors' paper) but re-tagged `CANONICAL_TITLE_VERIFIED: …`.                  | Auditor P0 item ②(b) explicitly called out these three for "canonical-title + latest-version number synchronisation". Titles fixed; numbers deferred to Commit 3/7 (schema verification_status). |

## Overall Audit Gate for Commit 2

- [x] All 9 auditor-flagged identity mismatches re-synced to the arXiv Atom feed verbatim.
- [x] Fabricated VLA-IE-001 "1.5x–3x" claim **physically deleted** from the CSV and replaced with the author-reported ~7.5%.
- [x] VLA-IE-008's **wrong-arXiv-id (comm-theory 2501.12148 → robotics ECoT 2407.08693)** corrected + link swapped.
- [x] All patched rows receive a `CANONICAL_TITLE_VERIFIED: arXiv:<id> @ 2026-08-06; ROADMAP commit 2/7 auditor-sync; OLD_TITLE=<truncated>` Notes tag so every correction is traceable.
- [x] No rows added or deleted (strict 17-row track count preserved — only field edits).
- [x] Patch is reproducible via `scripts/apply_commit2_corrections.py`; no hand-edit of CSVs.

## Commit 2.1 Hotfix Supplement

### 6.1 VLA-IE-014 (arXiv 2505.08243) — Full 17-column decision

| Track ID | Year | Venue / Source | Title | Authors | Key Affiliation | Paper Link | Code Link | Method Category | VLA Target | Training-Free? | Reported Speedup | Primary Metric | Evaluated On / Dataset | Key Mechanism | Relevance to BudgetLoop-VLA | Gaps BudgetLoop Exploits | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VLA-IE-014 | 2025 | arXiv | Training Strategies for Efficient Embodied Reasoning | William Chen; Suneel Belkhale; Suvir Mirchandani; Oier Mees; Danny Driess; Karl Pertsch; Sergey Levine | Stanford; Berkeley | https://arxiv.org/abs/2505.08243 | NA | Train-time Reasoning · Deploy No-CoT (ECoT-Lite family) | Embodied CoT VLAs (ECoT-finetuned checkpoints) | NO — requires reasoning supervision during training | Up to ~3× inference speedup over standard robot reasoning (author-reported, LIBERO-90, table 2 abstract) | Task success rate (LIBERO-90) vs wall-clock inference time | LIBERO-90; ablations on RT-X-style robot reasoning variants | (1) Why ECoT works: representation learning, curricularization, expressivity; (2) 3 lightweight train-time reasoning recipes: single-step hint, plan-only, stepwise; (3) deployment: no explicit autoregressive CoT decoding → faster inference | Direct training-style efficient reasoning CONTROL: we compare our frozen-training-free BudgetLoop against a train-time-supervised fast-ECoT-Lite baseline; their 3× speedup is the ceiling our training-free approach must approach. | ECoT-Lite needs training-time reasoning supervision (π_finetune NOT allowed in frozen setting); static recipe per task vs BudgetLoop dynamic K per step; no compute bank / loop / difficulty gating; grounded vs semantic CoT not tiered. | Commit 2.1 full-row rewrite; arXiv 2505.08243 verified; OLD Looped-Transformer/ICL content removed. |

```quote
Robot chain-of-thought reasoning (CoT) -- wherein a model predicts helpful intermediate representations before choosing actions -- provides an effective method for improving the generalization and performance of robot policies, especially vision-language-action models (VLAs). While such approaches have been shown to improve performance and generalization, they suffer from core limitations, like needing specialized robot reasoning data and slow inference speeds. To design new robot reasoning approaches that address these issues, a more complete characterization of why reasoning helps policy performance is critical. We hypothesize several mechanisms by which robot reasoning improves policies -- (1) better representation learning, (2) improved learning curricularization, and (3) increased expressivity -- then devise simple variants of robot CoT reasoning to isolate and test each one. We find that learning to generate reasonings does lead to better VLA representations, while attending to the reasonings aids in actually leveraging these features for improved action prediction. Our results provide us with a better understanding of why CoT reasoning helps VLAs, which we use to introduce two simple and lightweight alternative recipes for robot reasoning. Our proposed approaches achieve significant performance gains over non-reasoning policies, state-of-the-art results on the LIBERO-90 benchmark, and a 3x inference speedup compared to standard robot reasoning.
```

### 6.2 VLA-IE-015 (arXiv 2601.09708) — Full 17-column decision

| Track ID | Year | Venue / Source | Title | Authors | Key Affiliation | Paper Link | Code Link | Method Category | VLA Target | Training-Free? | Reported Speedup | Primary Metric | Evaluated On / Dataset | Key Mechanism | Relevance to BudgetLoop-VLA | Gaps BudgetLoop Exploits | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| VLA-IE-015 | 2026 | arXiv | Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning | Chi-Pin Huang; Yunze Man; Zhiding Yu; Min-Hung Chen; Jan Kautz; Yu-Chiang Frank Wang; Fu-En Yang | NVIDIA; CMU; Academia Sinica | https://arxiv.org/abs/2601.09708 | NA | Latent CoT Distillation / Verbalizable Compact Planning | Reasoning VLA (long-horizon, failure recovery, few-shot) | NO — requires teacher CoT distillation + preference-guided training | Up to 89.3% inference-latency reduction over explicit-CoT baselines (author-reported §table on long-horizon sim/real tasks) | Task success; latency p50/p95; few-shot sim2real adaptation accuracy; failure recovery rate | Long-horizon 3D tabletop sim + real robot; few-shot adaptation splits; failure recovery scenarios | (1) Verbalizable latent planning space (interpretable compressed plans not full language tokens); (2) Teacher CoT distillation on explicit-reasoning traces; (3) Preference-guided trajectory alignment for plan→action stability; (4) Long-horizon planning + failure recovery + few-shot transfer. | Latent-CoT efficient-reasoning BASELINE for ablation P6: when BudgetLoop Deliberate-mode uses 2-step compressed planning (grounded-only, no semantic autoregressive tokens) it is a training-free approximation of Fast-ThinkAct distilled latent plan — no distillation cost, direct frozen weights. | Requires teacher+student distillation pipeline + preference data (CANNOT run on plain frozen checkpoint in 0-training setup); single-scheduler no compute bank / no K loop / no dynamic TTL-tiered cache across modalities; no forced latency-deadline hard-guard. | Commit 2.1 full-row rewrite; arXiv 2601.09708 Fast-ThinkAct verified; OLD loop-theory / sample-complexity content removed. |

```quote
Vision-Language-Action (VLA) tasks require reasoning over complex visual scenes and executing adaptive actions in dynamic environments. While recent studies on reasoning VLAs show that explicit chain-of-thought (CoT) can improve generalization, they suffer from high inference latency due to lengthy reasoning traces. We propose Fast-ThinkAct, an efficient reasoning framework that achieves compact yet performant planning through verbalizable latent reasoning. Fast-ThinkAct learns to reason efficiently with latent CoTs by distilling from a teacher, driven by a preference-guided objective to align manipulation trajectories that transfers both linguistic and visual planning capabilities for embodied control. This enables reasoning-enhanced policy learning that effectively connects compact reasoning to action execution. Extensive experiments across diverse embodied manipulation and reasoning benchmarks demonstrate that Fast-ThinkAct achieves strong performance with up to 89.3% reduced inference latency over state-of-the-art reasoning VLAs, while maintaining effective long-horizon planning, few-shot adaptation, and failure recovery.
```

### 6.3 VLA-IE-016 / IE-017 — Search evidence + pending decision

Search evidence capture script: `scripts/tmp_task1_fetch_full.py`

#### IE-016: Efficient Diffusion Policy via Progressive Latent Refinement (claimed venue CoRL 2025)

| Source | Query | Hits (total) | Top-1 evidence | Hit-count |
|---|---|---|---|---|
| (a) arXiv ti: exact title | `ti:"Efficient Diffusion Policy via Progressive Latent Refinement"` | 0 | — | 0 |
| (b) Semantic Scholar Graph API | `query=Efficient+Diffusion+Policy+via+Progressive+Latent+Refinement` (HTTP 429 rate-limited, treated as 0) | 0 | — | 0 |
| (c) GitHub repo title-exact search | Skipped per spec (cost / auth-free search unavailable) | N/A | not searched (cost / auth-free search unavailable) | N/A |

- **authoritative_sources (a+b) = 0**
- **DECISION = pending_verification** (COMMIT 2.1 downgrade)
- VERIFICATION_STATUS override: NO PAPER LINK + placeholder authors "(related action acceleration)"

#### IE-017: Anytime-RT: Anytime Vision-Language-Action Control with Controllable Compute Ceiling (claimed venue RSS 2025)

| Source | Query | Hits (total) | Top-1 evidence | Hit-count |
|---|---|---|---|---|
| (a) arXiv ti: exact title | `ti:"Anytime-RT: Anytime Vision-Language-Action Control with Controllable Compute Ceiling"` | 0 | — | 0 |
| (b) Semantic Scholar Graph API | `query=Anytime-RT+Anytime+Vision-Language-Action+Control+with+Controllable+Compute+Ceiling` (HTTP 429 rate-limited, treated as 0) | 0 | — | 0 |
| (c) GitHub repo title-exact search | Skipped per spec (cost / auth-free search unavailable) | N/A | not searched (cost / auth-free search unavailable) | N/A |

- **authoritative_sources (a+b) = 0**
- **DECISION = pending_verification** (COMMIT 2.1 downgrade)
- VERIFICATION_STATUS override: NO PAPER LINK + placeholder authors "(related anytime-VLA)"

### 6.4 17-row training_requirement enumeration assignment

Enum set (size=8): `{ training_free, frozen_model_controller_only, requires_finetuning, requires_distillation, trained_architecture, analysis_only, reference_backbone, unknown }`

| Track ID | Training-Free display text (from CSV column 11) | training_requirement enum |
|---|---|---|
| VLA-IE-001 Fast ECoT | YES (no training) | training_free |
| VLA-IE-002 VLA-Cache | YES (inference only) | training_free |
| VLA-IE-003 EfficientVLA | YES (inference-only recipe) | training_free |
| VLA-IE-004 ActionCache | YES (flow-based replay, no training) | training_free |
| VLA-IE-005 ElegantVLA | YES (lightweight scorer, no training) | training_free |
| VLA-IE-006 ERVLA | N/A (analysis paper) | analysis_only |
| VLA-IE-007 OpenVLA | Pretrained checkpoints only | reference_backbone |
| VLA-IE-008 ECoT | Requires CoT fine-tuning | requires_finetuning |
| VLA-IE-009 Mixture-of-Recursions | NO (light router trained end-to-end) | trained_architecture |
| VLA-IE-010 Hyperloop | NO (architecture trained from scratch with loop) | trained_architecture |
| VLA-IE-011 Training-Free Looped Transformers | YES — fully frozen | frozen_model_controller_only |
| VLA-IE-012 LoopQ | N/A (analysis) | analysis_only |
| VLA-IE-013 RD-VLA | NO — TBPTT trains recurrent action head | requires_finetuning |
| VLA-IE-014 (from §6.1 decision) | NO — requires reasoning supervision during training | requires_finetuning |
| VLA-IE-015 (from §6.2 decision) | NO — requires teacher CoT distillation + preference-guided training | requires_distillation |
| VLA-IE-016 (search DECISION pending override) | YES (inference scheduling) + NO PAPER LINK + placeholder authors → VERIFICATION_STATUS=PENDING | unknown |
| VLA-IE-017 (search DECISION pending override) | YES (cascaded policies) + NO PAPER LINK + placeholder authors → VERIFICATION_STATUS=PENDING | unknown |

## Commit 2.1 Hotfix Gates Stdout (2026-08-07 01:34:44)
<pre>
GATE1=[PASS]
GATE2=[PASS]
GATE3=[PASS]
GATE4=[PASS]
GATE5=[PASS]
GATE6=[PASS]
GATE7=[PASS]

================= COMMIT 2.1 EXIT-GATES SUMMARY =================
GATE1 (IE014 semantic               ): PASS — GATE1 CmdA reverse count=0 (expect=0)
GATE2 (IE015 semantic               ): PASS — GATE2 CmdA reverse count=0 (expect=0)
GATE3 (016/017 pending isolation    ): PASS — GATE3 CmdA README mentions 016/017 count=0 (expect=0)
GATE4 (TF enum TOP==TABLE dedupe    ): PASS — GATE4 README top-check rc=0 stdout='TOP= 6
YES= 6'
GATE5 (Notes idempotent CTV≤1       ): PASS — GATE5 idempotent-check rc=0
GATE6 (git cleanup ignore           ): PASS — GATE6 git ls-files .arXiv_tmp_commit2.csv → '' (expect empty)
GATE7 (partitions + build success   ): PASS — GATE7 partition counts rc=0 stdout='VERIFIED=78 PENDING=22 PREDICTED=20 SUM=120'
OVERALL: 7/7 GREEN

</pre>

## Commit 2.1 Hotfix Gates Stdout (2026-08-07 01:38:10)
<pre>
GATE1=[PASS]
GATE2=[PASS]
GATE3=[PASS]
GATE4=[PASS]
GATE5=[PASS]
GATE6=[PASS]
GATE7=[PASS]

================= COMMIT 2.1 EXIT-GATES SUMMARY =================
GATE1 (IE014 semantic               ): PASS — GATE1 CmdA reverse count=0 (expect=0)
GATE2 (IE015 semantic               ): PASS — GATE2 CmdA reverse count=0 (expect=0)
GATE3 (016/017 pending isolation    ): PASS — GATE3 CmdA README mentions 016/017 count=0 (expect=0)
GATE4 (TF enum TOP==TABLE dedupe    ): PASS — GATE4 README top-check rc=0 stdout='TOP= 6
YES= 6'
GATE5 (Notes idempotent CTV≤1       ): PASS — GATE5 idempotent-check rc=0
GATE6 (git cleanup ignore           ): PASS — GATE6 git ls-files .arXiv_tmp_commit2.csv → '' (expect empty)
GATE7 (partitions + build success   ): PASS — GATE7 partition counts rc=0 stdout='VERIFIED=78 PENDING=22 PREDICTED=20 SUM=120'
OVERALL: 7/7 GREEN

</pre>
