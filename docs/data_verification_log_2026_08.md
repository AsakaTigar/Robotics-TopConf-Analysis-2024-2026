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
