# BudgetLoop-VLA: Training-Free Compute Reallocation for Reasoning VLAs under Fixed Latency

> **Status**: LOCKED direction. All experiments route here. No scope creep below lines without re-review.**

---

## 1. Core Framing — From Accelerator to Allocator

Simple compositions of existing training-free VLA acceleration modules (plan reuse, visual KV cache, action warm-start, looped transformers) will be reviewed as engineering assembly. To make a method-level contribution we reframe the problem:

> **Problem Statement.** Given a frozen 1B-parameter reasoning VLA (ECoT-style plan/subtask/move/gripper/objects → action), a per-control-step compute bank $B$, and a fixed average-latency ceiling, reallocate saved compute from easy steps to genuinely difficult steps without any training.**

| Old framing | New framing (this work) |
|---|---|
| Inference accelerator (FLOPs reduced → latency down) | **Compute allocator** (same average FLOPs budget → task success up **or** same success → latency down) |
| Methods: cache, prune, cache + prune | Method: **Cache-to-Think** (save → bank → reallocate |
| Evaluation: Pareto of success vs mean latency | Evaluation: (1) same avg latency vs higher success; (2) same success vs lower avg+p95 latency; (3) qualitative allocation visualization per-step |

Names we may use on title / abstract:
- **BudgetLoop-VLA** (preferred internal codename)
- Cache-to-Think VLA
- Reflex–Deliberate VLA
- Training-Free Compute Reallocation for Reasoning VLAs
- **Budget-Scheduled Reflex–Deliberate VLA (full qualifier)

---

## 2. Three Inference Modes

All modes run on the **same single frozen VLA checkpoint**. No training. No distillation. No finetuning. No separate policies.

| Mode | Trigger condition | What gets reused / skipped | What gets refreshed | Optional loop |
|---|---|---|---|---|
| **Reflex** | Stable scene; free-space motion; action history consistent; low task-difficulty signal | ✅ goal/subtask/plan cache (long TTL); ✅ static visual KV cache (VLA-Cache rules); ✅ ActionCache historical warm-start; ✅ skip all semantic CoT tokens | Only gripper token sanity check; last action-token | No loop (K=1) |
| **Refresh** | Partial occlusion; approaching target; pre-grasp micro-adjust; instruction mentions move/gripper change | ✅ goal/subtask/plan preserved; ✅ static background KV preserved; ✅ ActionCache disabled or weak-warm | 🔁 move / gripper / objects / grounding CoT tokens re-computed; 🔁 task-relevant visual tokens re-fetched | Still K=1 (no loop) |
| **Deliberate** | Contact phase; target switch; action-inconsistency detected; hidden residual divergence; hard-object (task-difficulty high; failure-recovery / OOD | Only goal-level plan unchanged; plan may still valid | ⚠️ Full visual re-forward **all** tokens + full CoT forward 🔁 | ❄️ **Frozen mid-stack window, K∈{2,3} **damped loop** (`Training-Free Looped Transformers recipe); selective token recursion on gripper/objects/instruction/grounded-CoT only |

### 2.1 Grounded-vs-Semantic TTL Policy (from ERVLA evidence)

ERVLA 2606.03784 shows:
- Semantic high-level CoT (goal/subtask/plan) alone → small gain.
- **Grounded CoT (move, gripper, objects, trajectory) directly coupled to action → large gain.
- Treating entire CoT as single cache object → error accumulation.

Therefore we do **NOT cache as monolith. Instead:

| Field | TTL (steps) | Invalidation trigger |
|---|---|---|
| `goal` | long (default 30) | Instruction change, target class switch, episode reset |
| `subtask` | medium-long (default 10) | Task-phase boundary in plan, or grounding class change |
| `plan` | medium (default 5) | Action inconsistency > δ, or hidden residual divergence |
| `move` | short (1–2) | Approaching goal, contact, gripper action change |
| `gripper` | short (1) | Gripper cmd changed previous step OR imminent contact |
| `objects / grounding trajectory` | short (1–2) | bbox overlap < τ, contact, or occlusion |

---

## 3. Cache-to-Think Compute Bank

The key claim that elevates this work from "cache+loop combo" → **method**.

### 3.1 Bank Dynamics

$$
b_t = \mathrm{clip}\bigl(b_{t-1} + B - c_t,\ \ b_{\min},\ \ b_{\max}\bigr)
$$

where:

| Symbol | Meaning | Default (first ablation) |
|---|---|---|
| $B$ | average per-step compute budget (FLOPs or wall-clock latency of "full Reflex" K=1) | = forward latency, in ms or FLOPs |
| $c_t$ | actual compute consumed this step | measured wall-clock |
| $b_t$ | compute-bank balance at end of step $t$ | $b_{\min}=0$ (cannot borrow); $b_{\max}$ = budget of 2 Deliberate steps |
| $\Delta_t = B - c_t$ | surplus if Reflex/Refresh: $c_t < B$ (balance deposit), deficit if Deliberate: $c_t > B$ (withdraw) | |

### 3.2 Mode Selection Logic

At start of step $t$:

```
if b_t >= threshold_deliberate AND difficulty_t >= hard → Mode = Deliberate
elif difficulty_t >= medium OR cache_miss_on_move OR occlusion_detected → Mode = Refresh
else → Mode = Reflex
```

where `difficulty_t` is cheap difficulty signal (Section 3.3).

### 3.3 Cheap Difficulty Signal (Training-Free)

Composed of zero-extra-parameters signatures computable from the Reflex forward already produced:
1. Action consistency: $\|a_t - a_{t-1}\|_2 > δ_action
2. Per-token hidden residual before action head: top-k residual entropy of task-relevant tokens (objects / gripper / instruction grounding / trajectory)
3. Attention entropy on grounding attention heads
4. Gripper–object distance below contact threshold
5. ActionCache miss ratio last N steps
6. History action KL between Reflex and (cheap) mini-refresh forward (if budget allows)

All signatures are scalars; combined with hand-tuned thresholds in v0. Sweep in P3.

### 3.4 Why This Is Not Just Thresholding

To rebut "this is just an ad-hoc threshold scheduler" reviewer attack we must demonstrate:
1. **Same B same success-rate gain over cache-only AND ElegantVLA baselines — if threshold-only would not gain (prove via ablate bank ablation on same-threshold budget-fixed condition)
2. **Qualitative case studies** of specific episodes: allocation visualised time-aligned with failure points where Deliberate kicked in exactly before failure avoided; without bank → those steps would have been Reflex and error cascaded.
3. **Budget sweep:** vary B × keep bank disabled. Success rises then saturates.

---

## 4. Training-Free Loop Design

### 4.1 Frozen Mid-Stack Window Loop (directly from Training-Free Looped Transformers 2605.23872)

Sweep P2:
- **Window**: continuous mid-stack window (ablate: 3–6 middle layers out of typical 24-layer LLM
- $K \in \{2, 3\}$ (hard cap; K>3 never — LoopQ pathology risk)
- Damping coefficient $\alpha \in \{0.25, 0.5, 0.75\}$:
  $$h'_k = \alpha \cdot \mathrm{TransformerBlock}(h_{k-1}) + (1-\alpha) \cdot h_{k-1}$$
- **Naive loop (α=1) vs damped**: always report both; expect naive → degradation (expected from T-F Looped paper
- **Full token vs token-selective recursion**: only select high-residual tokens loop (approximation of Mixture-of-Recursions without training)

### 4.2 Training-Free Token-Selective Recursion (Approximation of MoR)

1. Normal forward once (already done at Refresh/Deliberate mode):
   - Get per-token hidden residual relative layer before/after mid-stack
2. Score: $s_i = \| \Delta h_i \|_2$ plus attention entropy on token $i$
3. **Select**: top-M tokens from {objects, gripper/claw, instruction tokens, grounded reasoning (move/gripper/objects/trajectory)
4. **Bypass**: static background tokens, plan/subtask already stable → directly reuse previous hidden directly
5. Safety fallback: if after loop iteration residual norm diverges $> 2\times$ baseline forward → **rollback K=1 (no loop output discarded)

### 4.3 1B Parameter Budget Claim Rigor

**DO NOT write**: "1B parameter loop ≈ larger model"

**DO write**:
> Under the **same 1B parameter-storage budget** and the **same average-compute ceiling**, a dynamically looped frozen-1B checkpoint outperforms a fixed-depth non-looped frozen-1B baseline on task success.

Acknowledged caveats (must include in related-work / limitations):
- Hyperloop / MoR are trained with loop; ours loop frozen plain checkpoint → representation drift risk
- Loop increases compute, activation, latency, energy
- Low-bit quantized runs risk LoopQ recursive quantization error → we cap K=2 only Deliberate, plus divergence rollback
- RD-VLA (2602.07845) trains recurrent action head via TBPTT → treat as **training-style upper bound**, not strict comparable

---

## 5. Experimental Roadmap (P0 → P3)

All Go/No-Go gates explicit.

### P0. Profiling — GO before anything else.

Target platform: OpenVLA → ECoT fine-tune on LIBERO (or existing ECoT-OpenVLA checkpoint if public).

Collect:
- Per-module latency breakdown: vision encoder %, CoT/plan %, LLM cross-attn %, action head %
- Adjacent-step change rate per CoT field type (goal change frequency; plan change; move change; gripper change; objects grounding change)
- High-level plan cache hit rate across 50 episodes, across 3 task categories
- Failure rate stratified by {contact, occlusion, target-switch, free-space-motion, approach-phase, grasping-phase}
- Spearman rank: task difficulty vs {action L2 jump, hidden residual entropy, cache miss}

**Go gate P0→P1**: cache hit rate on plan+goal >= **60%** easy (Reflex share >= 40% steps. If <40% Reflex the potential savings too small → kill direction. **Already passed our prior reading.

### P1. Strong Cache-Only Baseline

Assemble baseline = Fast ECoT plan cache + VLA-Cache visual-KV rules + ActionCache action warm-start.

**Go gate P1→P2**:
- Speedup **≥1.5× end-to-end wall-clock on 100-episode eval,
- mean-success drop **≤1.0 percentage points** vs full ECoT,
- report p50, p95, true control frequency in Hz,
- and ablation: removing any single component drops speed / success.

If <1.5× then baselines already too weak / too conservative / easy steps → adjust BudgetLoop baseline bar lowers; still proceed but write "baseline X×".

### P2. Validate Frozen Loop

First offline action replay (open-loop), then closed-loop 50 episodes.

Metrics:
- action KL / action L2 to GT or Full ECoT
- hidden norm across loop iterations
- residual convergence $h_k/h_
- Difficult-subset (contact/target switch/failure recovery) isolated improvement
- Loop-induced action jitter: consecutive action L2 variance

Sweep: window size in {3,4,5,6} mid-stack window; K∈{2,3}; α∈{0.25,0.5,0.75}; naive vs damped; full vs token-selective.

**Go gate P2→P3**:
- Closed-loop K=2-damped-token-selective loop improves hard-subset success ≥ 2pp over full-ECoT K=1 on same 1.0× latency budget.

### P3. BudgetLoop Integrated

Final comparison:

| ID | Method | Description |
|---|---|---|
| (1) | Full ECoT (Oracle) | No caching, K=1 |
| (2) | Fixed-acceleration | 1.5× fixed speed cache (no dynamic, no loop) |
| (3) | Fixed K=2 loop | All steps loop, no cache |
| (4) | Cache-only baseline | P1 |
| (5) | ElegantVLA-style scheduler | (reproduce closest allocator, **no bank**) |
| (6) | **BudgetLoop-VLA** | Ours |

**Primary claims vs baseline (4):
Q1: **Same average latency** → BudgetLoop success > cache-only? Δ ≥ +2.0pp
Q2: **Same success rate** → BudgetLoop both mean latency lower AND p95 latency lower

**Key figures required**:
A. Standard success–latency Pareto (1–6 overlaid)
B. **Per-episode time-axis strip** aligned:
   - top: task phase (approach, contact, grasp, move-away)
   - row 2: difficulty signal (3.3)
   - row 3: actual compute consumed
   - row 4: mode (Reflex / Refresh / Deliberate)
   - row 5: bank balance b_t
   - bottom: * mark failures
C. Ablation strip bank disabled vs bank enabled on same threshold policy
D. Budget B sweep: success rate as function of B with and without bank

### P3 Go gate for paper submission
- Both Q1 and Q2 significant (paired t-test on 3 seeds, p < 0.05)
- Qualitative strips show allocation concentrated before contact/target-switch
- At least one ablated case where bank-disabled + same thresholds can't beat bank-enabled on hard subset

---

## 6. Hardware / End-Side Story

On end-side deployment scenario:
- **Parameter storage budget fixed = 1B parameters (INT4 quantized weights + activations SRAM budget fits).
- **Average latency ceiling = control frequency >= 5 Hz or >= 10 Hz.
- Deliberate steps allowed < 20% steps; p95 bounded by bank max withdrawals.

---

## 7. Related Work Positioning (Strict)

| Work | Category | Strictly different from ours |
|---|---|---|
| Fast ECoT 2506.07639 | Plan cache + parallel | Cache + **no** compute bank, **no** loop |
| VLA-Cache 2502.02175 | Vision KV + task-token refresh | Cache + **no** CoT tiered TTL, **no** bank, **no** loop |
| EfficientVLA 2506.10100 | Joint vision+LLM+action cache | Fixed recipe; **no** dynamic per-step, **no** bank |
| ActionCache 2607.06370 | Action-head warm-start | Only action; **no** unified vision+CoT+action controller |
| ElegantVLA 2605.29438 | Dynamic per-module scheduling | No forced avg-latency ceiling; **no** compute bank ($b_t$) |
| Training-Free Looped Transformer 2605.23872 | Frozen mid-stack loop | **Not** VLA-specific; **no** combine cache + loop + allocator |
| MoR 2507.10524 | Token recursion (trained router) | Requires end-to-end router training → **not training-free** |
| Hyperloop 2604.21254 | Begin-middle-end loop arch | **Trained** with loop; not frozen inference |
| RD-VLA 2602.07845 | Recurrent action + adaptive stop | TBPTT-trained → **not training-free** |

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Cache hit rate too low | Medium | High | P0 gate kills early; relax Refresh mode default |
| Naive loop degrades performance | High | Medium | Use only damped + token-selective + K≤2 + rollback fallback |
| LoopQ quant drift | Low-Medium | Medium | Only Deliberate only, INT8 at worst; hidden norm guardrails; report quant separately |
| Thresholds look ad-hoc | High | High | Bank-ablation strip; budget sweep; 5× threshold random seed |
| Reviewer says "engineering combo" | High | Critical | **Method-level claim; Cache-to-Think + qualitative allocation strips |
| No stat sig gain over ElegantVLA | Medium-High | Critical | Primary hard-subset eval on contact/target-switch |

---

## 9. Execution File Map

- Paper source:
  - `research_tracks/vla_inference_efficiency_2024_2026.csv`
- Detailed VLA efficiency paper matrix 17 entries with gaps
- `data_quality/AUDIT_2024_2026.md`
- Main CSV placeholder entries flagged DATA_QUALITY
- `scripts/build_research_tracks.py` (future: merge track visualiser)
- `README.md` — track summary entry BudgetLoop-VLA
