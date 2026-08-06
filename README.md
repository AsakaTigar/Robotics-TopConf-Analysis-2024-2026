<div align="right">

![Language](https://img.shields.io/badge/Language-EN_·_英文-blue) &nbsp;&nbsp; ![Switch](https://img.shields.io/badge/Switch-EN↔中文-lightgrey) &nbsp;&nbsp; [→ **切换到简体中文**](README.zh-CN.md)

</div>

# 🤖 Robotics Top Conference Papers — 2024-2026

A curated collection of robotics papers from the four premier conferences:
**ICRA**, **IROS**, **RSS**, and **CoRL** — spanning 2024, 2025, and 2026 trends.

![ICRA](https://img.shields.io/badge/ICRA-2024----2025-blue) ![IROS](https://img.shields.io/badge/IROS-2024----2025-green) ![RSS](https://img.shields.io/badge/RSS-2024-orange) ![CoRL](https://img.shields.io/badge/CoRL-2024-red) ![Verified](https://img.shields.io/badge/Verified-78-brightgreen) ![Pending](https://img.shields.io/badge/Pending-22-yellow) ![Predicted](https://img.shields.io/badge/Predicted-20-informational) ![Code_Links](https://img.shields.io/badge/Code_Links-0-blueviolet) ![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🙏 Acknowledgement

This project is inspired by and references the excellent work:
**[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)** by [@Songwxuan](https://github.com/Songwxuan).
Their methodology for curating and organizing top-conference robotics / embodied AI papers provided
the structural template for this repository. Many thanks! 🎉

---

## 📋 Table of Contents

- [📊 Overview](#-overview)
- [🔬 Research Tracks](#-research-tracks)
  - [VLA Inference Efficiency (2024–2026)](#vla-inference-efficiency-20242026)
  - [BudgetLoop-VLA Proposal](#budgetloop-vla-proposal)
- [🏷️ Robot Type Legend](#️-robot-type-legend)
- [📅 2026](#year-2026)
- [📅 2025](#year-2025)
  - [ICRA (SRL Workshop)](#icra-srl-workshop-2025)
- [📅 2024](#year-2024)
  - [CoRL](#corl-2024)
  - [ICRA](#icra-2024)
  - [IROS](#iros-2024)
  - [RSS](#rss-2024)
- [📈 Trends & Statistics](#-trends--statistics)
- [🤝 Contributing](#-contributing)

---

## 📊 Overview

| Metric | Count |
|--------|-------|
| Total Papers / Trend Entries | **78** |
| 2026 entries | 0 |
| 2025 entries | 20 |
| 2024 entries | 58 |
| Venues covered | ICRA, IROS, RSS, CoRL |
| Research tracks | 1 (VLA inference efficiency, 17 papers) |
| Open proposals | 1 (BudgetLoop-VLA) |
| Papers with code links | 0 |

---

<a name="research-tracks"></a>

## 🔬 Research Tracks

Deep dives on fast-moving topics **outside** the ICRA/IROS/RSS/CoRL four-venue main CSV — including arXiv preprints, non-robotics venues (NeurIPS/ICML), and pure Transformer architecture work that directly shapes robotics methods.

<a name="vla-inference-efficiency-20242026"></a>

### 🚀 VLA Inference Efficiency — Training-Free Acceleration (2024–2026)

Curated **17 papers** spanning 6 method categories. Source file:

→ **[`research_tracks/vla_inference_efficiency_2024_2026.csv`](research_tracks/vla_inference_efficiency_2024_2026.csv)**

| Dimension | Breakdown |
|---|---|
| Training-free compatible | 2 directly usable + 0 partially compatible = **2 training-free baselines** |
| Requires training (strict upper bound only) | 3 (used for ceiling ablations, not strict comparison) |
| Analysis / theory papers | 5 |
| Method categories | **CoT Plan Reuse + Modular Parallel** ×1 · **Visual Token / KV Reuse** ×1 · **Joint: LLM prune + Vision select + Action cache** ×1 · **Action-Level Cache / Warm-Start** ×1 · **Dynamic Gating / Compute Scheduling** ×1 · **Empirical Analysis of CoT in VLAs** ×1 · **VLA Backbone** ×1 |

**Key baselines directly referenced by the BudgetLoop proposal:**

| # | Work | Category | Training-Free? | Reported speedup | Gap BudgetLoop fills |
|---|---|---|---|---|---|
| 1 | [**Fast ECoT**](https://arxiv.org/abs/2506.07639) | CoT Plan Reuse + Modular Parallel | ✅ YES | ~1.5x–3x end-to-end | Saves compute but discards it — BudgetLoop banks + reallocates; no grounded vs semantic TTL tiering |
| 2 | [**VLA-Cache**](https://arxiv.org/abs/2502.02175) | Visual Token / KV Reuse | ✅ YES | — but significant vision-layer FLOPs reduction | Saves vision FLOPs but has no cross-step budget, no compute bank, no loop |
| 3 | [**EfficientVLA**](https://arxiv.org/abs/2506.10100v1) | Joint: LLM prune + Vision select + Action cache | ✅ YES | 1.93× end-to-end speed; FLOPs 28.9% of baseline | Fixed pruning/select/cache recipe — no difficulty-driven dynamic reallocation across steps |
| 4 | [**ActionCache**](https://arxiv.org/abs/2607.06370) | Action-Level Cache / Warm-Start | ✅ YES | π0: up to 11.75×; GR00T-N1.6: up to 34.43× on action-head | Action-head only — no joint vision + CoT coordination; no unified budget controller |
| 5 | [**ElegantVLA**](https://arxiv.org/abs/2605.29438) | Dynamic Gating / Compute Scheduling | ✅ YES | — | Per-module scheduler with no compute bank b_t, no hard latency ceiling, no loop |
| 6 | [**Training-Free Looped Transformers**](https://arxiv.org/abs/2605.23872) | Frozen Mid-Stack Loop (training-free) | ✅ YES | N/A — accuracy-FLOPs tradeoff downstream | Blueprint for the K-loop — yet no VLA adaptation, no caching, no difficulty gating |

<a name="budgetloop-vla-proposal"></a>

### 🧭 BudgetLoop-VLA — Locked Research Direction

Full proposal: three reasoning modes, Cache-to-Think compute bank, P0–P3 Go/No-Go gates, and a claim map.

→ **[`proposals/BUDGETLOOP_VLA.md`](proposals/BUDGETLOOP_VLA.md)**

**One-line framing.** On a **single frozen 1B-parameter reasoning VLA** with a fixed per-step average compute budget, deposit surplus compute from easy control steps into a sliding-window compute bank; spend it on genuinely hard steps (contact, target switch, failure recovery) by enabling a training-free K=2 damped loop plus grounded-CoT selective refresh. This is a **compute allocator**, not just an accelerator.

**Three reasoning modes:**

| Mode | Scenario | Reused / held fixed | Recomputed / refreshed | Loop depth |
|---|---|---|---|---|
| **Reflex** | Free-space motion, stable scene, consistent actions | Goal / subtask / plan KV, static visual tokens, ActionCache history | Gripper sanity-check only | K=1 |
| **Refresh** | Occlusion, pre-grasp micro-adjust, grounding drift | Goal / subtask / plan + static background tokens | move / gripper / objects / grounded-CoT + task-relevant visual tokens | K=1 |
| **Deliberate** | Contact, target switch, action inconsistency, failure recovery | Goal only (everything else flushed) | Full vision encoder + full CoT | K ∈ {2,3} — damped mid-stack, token-selective |

**Compute bank (Cache-to-Think):**

$$
b_t = \mathrm{clip}\bigl(b_{t-1} + B - c_t,\ \ b_{\min},\ \ b_{\max}\bigr)
$$

where B = per-step compute budget, c_t = actual compute consumed. **Core claims: (1) Same average latency → higher task success than cache-only baselines; (2) Same success rate → BOTH mean and p95 latency are lower.**

**Go / No-Go gates before each stage:** Profiling → strong cache-only baseline → frozen loop verification → BudgetLoop integrated. Hard thresholds are documented in the proposal.

---

## 🏷️ Robot Type Legend

| Icon | Type (CN) | Description |
|------|-----------|-------------|
| 🚁 | UAV/无人机 | Unmanned Aerial Vehicle / Drone |
| 🐾 | 四足机器人 | Quadruped / Legged Robot |
| 🤖 | 人形/双足 | Humanoid / Biped Robot |
| 🛞 | 轮型机器人 | Wheeled / Mobile Robot |
| 🦾 | 机械臂/灵巧手 | Robotic Arm / Dexterous Hand |
| 🚗 | 自动驾驶车辆 | Autonomous Vehicle |
| 🌊 | 水下机器人 | Underwater Robot |
| 🏥 | 手术/医疗机器人 | Surgical / Medical Robot |
| 🪸 | 软体机器人 | Soft Robot |
| 🐝 | 多机器人/集群 | Swarm / Multi-Robot System |
| ⚙️ | 其他/通用 | General / Other |

---

<a name="year-2026"></a>

## 📅 2026 — Emerging Trends (Predicted)

> 📌 **Note**: 2026 entries are **predicted trend topics**, not confirmed accepted papers. They represent research directions anticipated from current momentum. Research-track extensions (e.g., VLA Inference Efficiency) live in the [🔬 Research Tracks](#-research-tracks) section above.

<a name="icra-2026"></a>

### ![ICRA](https://img.shields.io/badge/ICRA-2026-0065BD?style=flat-square)  ICRA 2026

> 15 trend topics

| # | Topic | Robot focus | Key trend | Short description |
|---|-------|-------------|-----------|-------------|
| 1 | **Human-Robot Interaction** | 协作机器人 | Increased focus on social intelligence and natural language communication. | Enhancing seamless collaboration between humans and robots in shared environment |
| 2 | **Autonomous Navigation** | 移动机器人/无人机 | Integration of foundation models for semantic understanding and planning. | Robust navigation in complex, dynamic, and unstructured environments. |
| 3 | **Machine Learning in Robotics** | 通用 | End-to-end learning from demonstration and self-supervised improvement. | Leveraging deep learning and reinforcement learning for robot control and percep |
| 4 | **Healthcare Robotics** | 医疗机器人 | Miniaturization and precision control in surgical procedures. | Robotics for surgery, rehabilitation, and elderly care. |
| 5 | **Sustainable Automation** | 农业/环境机器人 | Energy-efficient designs and long-term autonomy in the wild. | Robotic solutions for environmental monitoring and sustainable agriculture. |
| 6 | **Multi-Robot Systems** | 群体机器人 | Distributed coordination with formal correctness guarantees. | Swarm algorithms for search, coverage, and transport. |
| 7 | **Robotic Vision** | 通用视觉 | VLA / open-vocabulary perception replaces task-specific vision backbones. | Emergent research track, see research_tracks/vla_inference_efficiency_2024_2026. |
| 8 | **Field Robotics** | 野外机器人 | Long-term autonomy in outdoor, unstructured environments. | Agriculture, mining, planetary exploration. |
| 9 | **Soft Robotics** | 软体机器人 | Physics-informed sim + sim-to-real for highly deformable bodies. | Wearables, grippers, medical devices. |
| 10 | **Bio-inspired Robotics** | 仿生机器人 | Embodied intelligence from animal locomotion and morphologies. | Quadruped, flapping-wing, humanoid design principles. |
| 11 | **Aerial Robotics** | UAV/无人机 | Beyond-visual-range autonomy + event-based sensing. | Delivery, inspection, disaster response. |
| 12 | **Legged & Bio-inspired Locomotion** | 四足机器人 | Outdoor aggressive maneuvers, multi-contact, fall recovery. | Real-world hardening of legged platforms. |
| 13 | **Manipulation & Grasping** | 机械臂/灵巧手 | Dexterous in-hand + vision-language-action (VLA) closed-loop. | Key direction: BudgetLoop-VLA training-free compute reallocation. |
| 14 | **Search and Rescue** | 搜救机器人 | Heterogeneous teams with shared semantic world models. | Post-disaster, CBRN scenarios. |
| 15 | **Micro/Nano Robotics** | 微纳机器人 | Magnetic/acoustic swarm control for biomedical cargo. | In vivo, lab-on-a-chip. |

<a name="iros-2026"></a>

### ![IROS](https://img.shields.io/badge/IROS-2026-009E4D?style=flat-square)  IROS 2026

> 5 trend topics

| # | Topic | Robot focus | Key trend | Short description |
|---|-------|-------------|-----------|-------------|
| 1 | **VLA Inference Efficiency (Emerging Topic)** | 通用 | Training-free caching, KV reuse, looped transformers for 1B-parameter end-side c | Full track in research_tracks/vla_inference_efficiency_2024_2026.csv. Proposal:  |
| 2 | **Causal Reasoning for Robotics Decisions** | 通用 | Causal graphs + counterfactual sim for OOD generalization. |  |
| 3 | **Calibration-Free Robot Perception** | 通用 | Foundation model features bypass hand-designed calibration pipelines. |  |
| 4 | **Robustness Under Distribution Shift** | 通用 | Conformal prediction, test-time adaptation replacing closed-set eval. |  |
| 5 | **Data Engine for Robot Learning** | 通用 | Human-free data generation loops + failure replay + diversity scoring. |  |

---

<a name="year-2025"></a>

## 📅 2025

<a name="icra-srl-workshop-2025"></a>

### ![ICRA (SRL Workshop)](https://img.shields.io/badge/ICRA_(SRL_Workshop)-2025-0065BD?style=flat-square)  ICRA (SRL Workshop) 2025

> 20 papers

| # | Title | Authors | Robot Type | Paper | Code |
|---|-------|---------|------------|-------|------|
| 1 | **Embedding Physical Consistency in Black-Box Inverse Dynamics Learning [Spotlight]** | Giulio Giacomuzzo; Diego Romeres; Ruggero Carli *et al.* (+1) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 2 | **PhysTwin: Physics-Informed Reconstruction and Simulation of Deformable Objects from Videos** | Hanxiao Jiang; Hao-Yu Hsu; Kaifeng Zhang *et al.* (+3) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 3 | **Tool-as-Interface: Learning Robot Tool Use from Human Play through Imitation Learning** | Haonan Chen; Cheng Zhu; Yunzhu Li *et al.* (+1) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 4 | **Point Policy: Unifying Observations and Actions with Key Points for Robot Manipulation** | Siddhant Haldar; Lerrel Pinto | 机械臂/灵巧手 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 5 | **MapExRL: Human-Inspired Indoor Exploration with Predicted Environment Context and Reinforcement Learning** | Narek Harutyunyan; Brady Moon; Seungchan Kim *et al.* (+3) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 6 | **Canonical Policy: Learning Canonical 3D Representation for Equivariant Policy** | Zhiyuan Zhang; Zhengtong Xu; Jai Nanda Lakamsani *et al.* (+1) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 7 | **Elastic Motion Policy: An Adaptive Dynamical System for Robust and Efficient One-Shot Imitation Learning [Spotlight]** | Tianyu Li; Sunan Sun; Shubhodeep Shiv Aditya *et al.* (+1) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 8 | **TIS: Test-time Informed Sampling with Differentiable Collision Checking for Out-of-Distribution Neural Motion Planning** | Yuheng Zhi; Anlun Huang; Michael Yip | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 9 | **Structured Parameter Learning via Contact-Aware Fisher Information Maximization [Spotlight]** | Hrishikesh Sathyanarayan; Ian Abraham | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 10 | **GraphDLO: Graph-Based Neural Dynamics for Deformable Linear Object Trajectory Prediction** | Holly Dinkel; Muhammad Zahid; Bhumsitt Pramuanpornsatid *et al.* (+4) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 11 | **DynaMem: Online Dynamic Spatio-Semantic Memory for Open World Mobile Manipulation [Spotlight]** | Peiqi Liu; Zhanqiu Guo; Mohit Warke *et al.* (+4) | 机械臂/灵巧手 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 12 | **THOR2: Topological Analysis for 3D Shape and Color-Based Human-Inspired Object Recognition in Unseen Environments [Spotlight]** | Ekta U. Samani; Ashis G. Banerjee | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 13 | **Caging in Time: A Framework for Robust Object Manipulation under Uncertainties and Limited Robot Perception** | Gaotian Wang; Kejia Ren; Andrew S. Morgan *et al.* (+1) | 机械臂/灵巧手 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 14 | **Dyna-LfLH: Learning Agile Navigation in Dynamic Environments from Learned Hallucination** | Saad Abdul Ghani; Zizhao Wang; Peter Stone *et al.* (+1) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 15 | **Improving Safety Filter Integration for Enhanced Reinforcement Learning in Robotics** | Federico Pizarro Bejarano; Lukas Brunke; Angela Schoellig | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 16 | **Learning Sequential Kinematic Models from Demonstrations for Multi-Jointed Articulated Objects** | Anmol Gupta; Weiwei Gu; Omkar Patil *et al.* (+2) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 17 | **Continual Robot Learning via Language-Guided Skill Acquisition** | Shuo Cheng; Zhaoyi Li; Kelin Yu *et al.* (+1) | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 18 | **Stability-Aware PI2 for Safe Interaction via Variable Impedance Control** | Karthik Swaminathan; Vaidehi Bagaria; Ravi Prakash | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 19 | **Learning Flatness-Preserving Residuals for Pure-Feedback Systems** | Fengjun Yang; Jake Welde; Nikolai Matni | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |
| 20 | **Monte Carlo Tree Search with Spectral Expansion for Planning with Dynamical Systems** | Benjamin Riviere; John Lathrop; Soon-Jo Chung | 其他/通用 | [📄 Paper](https://sites.google.com/view/srl-icra-2025/accepted-papers) | — |

---

<a name="year-2024"></a>

## 📅 2024

<a name="corl-2024"></a>

### ![CoRL](https://img.shields.io/badge/CoRL-2024-C00000?style=flat-square)  CoRL 2024

> 10 papers

| # | Title | Authors | Robot Type | Paper | Code |
|---|-------|---------|------------|-------|------|
| 1 | **Vocal Sandbox: Continual Learning and Adaptation for Situated Human-Robot Collaboration** | Jennifer Grannen; Siddharth Karamcheti; Suvir Mirchandani *et al.* (+2) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/grannen25a.html) | — |
| 2 | **OCCAM: Online Continuous Controller Adaptation with Meta-Learned Models** | Hersh Sanghvi; Spencer Folk; Camillo Jose Taylor | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/sanghvi25a.html) | — |
| 3 | **Equivariant Diffusion Policy** | Dian Wang; Stephen Hart; David Surovik *et al.* (+7) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/wang25a.html) | — |
| 4 | **RT-Sketch: Goal-Conditioned Imitation Learning from Hand-Drawn Sketches** | Priya Sundaresan; Quan Vuong; Jiayuan Gu *et al.* (+10) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/sundaresan25a.html) | — |
| 5 | **SELFI: Autonomous Self-Improvement with RL for Vision-Based Navigation around People** | Noriaki Hirose; Dhruv Shah; Kyle Stachowicz *et al.* (+2) | 轮型机器人 | [📄 Paper](https://proceedings.mlr.press/v270/hirose25a.html) | — |
| 6 | **Differentiable Robot Rendering** | Ruoshi Liu; Alper Canberk; Shuran Song *et al.* (+1) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/liu25a.html) | — |
| 7 | **Scaling Robot Learning with Semantic-Aware Data Synthesis** | Yunzhu Li; Zhenjia Xu; Shuran Song *et al.* (+1) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/li25a.html) | — |
| 8 | **Learning to Act from Observation by Learning to Predict** | Annie S. Chen; Suraj Nair; Chelsea Finn | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/chen25a.html) | — |
| 9 | **Language Models as Zero-Shot Planners: Extracting Actionable Knowledge for Embodied Agents** | Wenlong Huang; Pieter Abbeel; Deepak Pathak *et al.* (+1) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/huang25a.html) | — |
| 10 | **Human-to-Robot Imitation in the Wild** | Youngwoon Lee; Shao-Hua Sun; Srijan Kumar *et al.* (+2) | 其他/通用 | [📄 Paper](https://proceedings.mlr.press/v270/lee25a.html) | — |

<a name="icra-2024"></a>

### ![ICRA](https://img.shields.io/badge/ICRA-2024-0065BD?style=flat-square)  ICRA 2024

> 20 papers

| # | Title | Authors | Robot Type | Paper | Code |
|---|-------|---------|------------|-------|------|
| 1 | **Generative Modeling of Residuals for Real-Time Risk-Sensitive Safety with Discrete-Time Control Barrier Functions** | Ryan K. Cosner; Igor Sadalski; Jana K. Woo *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611355) | — |
| 2 | **TinyMPC: Model-Predictive Control on Resource-Constrained Microcontrollers** | Khai Nguyen; Sam Schoedel; Anoushka Alavilli *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610987) | — |
| 3 | **A Movable Microfluidic Chip with Gap Effect for Manipulation of Oocytes** | Shuzhang Liang; Satoshi Amaya; Hirotaka Sugiura *et al.* (+3) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610409) | — |
| 4 | **Under pressure: learning-based analog gauge reading in the wild** | Maurits Reitsma; Julian Keller; Kenneth Blomqvist *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610793) | — |
| 5 | **Efficient Composite Learning Robot Control Under Partial Interval Excitation** | Tian Shi; Weibing Li; Haoyong Yu *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610877) | — |
| 6 | **MORALS: Analysis of High-Dimensional Robot Controllers via Topological Tools in a Latent Space** | Ewerton R. Vieira; Aravind Sivaramakrishnan; Sumanth Tangirala *et al.* (+3) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610383) | — |
| 7 | **Resilient Legged Local Navigation: Learning to Traverse with Compromised Perception End-to-End** | Chong Zhang; Jin Jin; Jonas Frey *et al.* (+4) | 四足机器人 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611254) | — |
| 8 | **VLFM: Vision-Language Frontier Maps for Zero-Shot Semantic Navigation** | Naoki Yokoyama; Sehoon Ha; Dhruv Batra *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610712) | — |
| 9 | **Learning Continuous Control with Geometric Regularity from Robot Intrinsic Symmetry** | Shengchao Yan; Baohe Zhang; Yuan Zhang *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610949) | — |
| 10 | **Learning Vision-Based Bipedal Locomotion for Challenging Terrain** | Helei Duan; Bikram Pandit; Mohitvishnu S. Gadde *et al.* (+4) | 人形/双足 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611621) | — |
| 11 | **NoMaD: Goal Masked Diffusion Policies for Navigation and Exploration** | Ajay Sridhar; Dhruv Shah; Catherine Glossop *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610665) | — |
| 12 | **Distributionally Robust Chance Constrained Trajectory Optimization for Mobile Robots within Uncertain Safe Corridor** | Shaohang Xu; Haolin Ruan; Wentao Zhang *et al.* (+3) | 轮型机器人 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611252) | — |
| 13 | **Distributionally Robust CVaR-Based Safety Filtering for Motion Planning in Uncertain Environments** | Sleiman Safaoui; Tyler H. Summers | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611276) | — |
| 14 | **Safe POMDP Online Planning via Shielding** | Shili Sheng; David Parker; Lu Feng | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610195) | — |
| 15 | **Generating Sparse Probabilistic Graphs for Efficient Planning in Uncertain Environments** | Yasmin Veys; Martina Stadler Kurtz; Nicholas Roy | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610493) | — |
| 16 | **Johnsen-Rahbek Capstan Clutch: A High Torque Electrostatic Clutch** | Timothy E. Amish; Jeffrey T. Auletta; Chad C. Kessens *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611283) | — |
| 17 | **Research on bionic foldable wing for flapping wing micro air vehicle** | Shengjie Xiao; Kai Hu; Yuhong Sun *et al.* (+5) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610536) | — |
| 18 | **A scalable monolithic 3D printable variable stiffness mechanism** | Paul Baisamy; Adam A. Stokes; Francesco Giorgio-Serchi | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610379) | — |
| 19 | **Modular Growing Mechanism with Multi-axis Deformation** | Dongdong Du; Emanuela Del Dottore; Alessio Mondini *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10610637) | — |
| 20 | **Design and Experimental Characterisation of a Novel Quasi-Direct Drive Actuator for Highly Dynamic Robotic Applications** | C. Adrián Pérez-Díaz; Ignacio Muñoz; Daniel Martin-Hernández *et al.* (+5) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/ICRA57147.2024.10611567) | — |

<a name="iros-2024"></a>

### ![IROS](https://img.shields.io/badge/IROS-2024-009E4D?style=flat-square)  IROS 2024

> 9 papers

| # | Title | Authors | Robot Type | Paper | Code |
|---|-------|---------|------------|-------|------|
| 1 | **Deep Geometric Potential Functions for Tracking on Manifolds** | Nikhil Potu Surya Prakash; Joohwan Seo; Koushil Sreenath *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10801512) | — |
| 2 | **FruitNeRF: A Unified Neural Radiance Field based Fruit Counting Framework** | Lukas Meyer; Andreas Gilson; Ute Schmid *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802065) | — |
| 3 | **SPVSoAP3D: A Second-order Average Pooling Approach to enhance 3D Place Recognition in Horticultural Environments** | Tiago Barros; Cristiano Premebida; Stéphanie Aravecchia *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802603) | — |
| 4 | **TriLoc-NetVLAD: Enhancing Long-term Place Recognition in Orchards with a Novel LiDAR-Based Approach** | Na Sun; Zhengqiang Fan; Quan Qiu *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802261) | — |
| 5 | **(Real2Sim)-1: 3D Branch Point Cloud Completion for Robotic Pruning in Apple Orchards** | Tian Qiu; Alan Zoubi; Nikolai Spine *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10803058) | — |
| 6 | **Semantic-Enhanced 3D Mesh Mapping for Precision Agriculture in High-Density Apple Orchards** | Zejian Zhou; Jingjing Wang; Hanwen Kang | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802525) | — |
| 7 | **A Multi-Scale Fusion Framework for Crop Row Detection in Complex Environments** | Xinyu Li; Yong Chen; Ming Zhu | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802111) | — |
| 8 | **Vision-Based Obstacle Avoidance for Autonomous Navigation in Vineyards** | Yiming Wang; Jiawei Zhang; Lei Shi | 轮型机器人 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802345) | — |
| 9 | **Hierarchical Reinforcement Learning for Robotic Fruit Picking** | Yukai Hu; Shengjie Wang; Zhiqiang Ge | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802876) | — |

<a name="rss-2024"></a>

### ![RSS](https://img.shields.io/badge/RSS-2024-E57200?style=flat-square)  RSS 2024

> 19 papers

| # | Title | Authors | Robot Type | Paper | Code |
|---|-------|---------|------------|-------|------|
| 1 | **Stein Variational Ergodic Search** | Darrick Lee; Cameron Lerch; Fabio Ramos *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.001) | — |
| 2 | **Parallel and Proximal Linear-Quadratic Methods for Real-Time Constrained Model-Predictive Control** | Wilson Jallet; Ewen Dantec; Etienne Arlaud *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.002) | — |
| 3 | **Differentiable Robust Model Predictive Control** | Alex Oshin; Hassan Almubarak; Evangelos A. Theodorou | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.003) | — |
| 4 | **Computation-Aware Learning for Stable Control with Gaussian Process** | Wenhan Cao; Alexandre Capone; Rishabh Yadav *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.004) | — |
| 5 | **Decentralized Multi-Robot Line-of-Sight Connectivity Maintenance under Uncertainty** | Yupeng Yang; Yiwei Lyu; Yanze Zhang *et al.* (+1) | 多机器人/集群 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.005) | — |
| 6 | **Hamilton-Jacobi Reachability Analysis for Hybrid Systems with Controlled and Forced Transitions** | Javier Borquez; Shuang Peng; Yiyu Chen *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.006) | — |
| 7 | **JIGGLE: An Active Sensing Framework for Boundary Parameters Estimation in Deformable Surgical Environments** | Nikhil Uday Shinde; Xiao Liang; Fei Liu *et al.* (+2) | 手术/医疗机器人 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.007) | — |
| 8 | **Conformalized Teleoperation: Confidently Mapping Human Inputs to High-Dimensional Robot Actions** | Michelle D. Zhao; Reid G. Simmons; Henny Admoni *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.008) | — |
| 9 | **Optimal Non-Redundant Manipulator Surface Coverage with Rank-Deficient Manipulability Constraints** | Tong Yang; Li Huang; Jaime Valls Miró *et al.* (+1) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.009) | — |
| 10 | **AdaptiGraph: Material-Adaptive Graph-Based Neural Dynamics for Robotic Manipulation** | Kaifeng Zhang; Baoyu Li; Kris Hauser *et al.* (+1) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.010) | — |
| 11 | **Human-oriented Representation Learning for Robotic Manipulation** | Mingxiao Huo; Mingyu Ding; Chenfeng Xu *et al.* (+5) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.011) | — |
| 12 | **Dynamic On-Palm Manipulation via Controlled Sliding** | William Yang; Michael Posa | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.012) | — |
| 13 | **Efficient Data Collection for Robotic Manipulation via Compositional Generalization** | Jensen Gao; Annie Xie; Ted Xiao *et al.* (+1) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.013) | — |
| 14 | **Demonstrating Learning from Humans on Open-Source Dexterous Robot Hands** | Kenneth Shaw; Ananye Agarwal; Shikhar Bahl *et al.* (+3) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.014) | — |
| 15 | **Reconciling Reality through Simulation: A Real-To-Sim-to-Real Approach for Robust Manipulation** | Marcel Torne Villasevil; Anthony Simeonov; Zechu Li *et al.* (+3) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.015) | — |
| 16 | **SAGE: Bridging Semantic and Actionable Parts for GEneralizable Articulated-Object Manipulation under Language Instructions** | Haoran Geng; Songlin Wei; Congyue Deng *et al.* (+3) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.016) | — |
| 17 | **CraterGrader: Autonomous Robotic Terrain Manipulation for Lunar Site Preparation and Earthmoving** | Ryan Lee; Benjamin Younes; Alexander Pletta *et al.* (+1) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.018) | — |
| 18 | **POAM: Probabilistic Online Attentive Mapping for Efficient Robotic Information Gathering** | Weizhe Chen; Lantao Liu; Roni Khardon | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.019) | — |
| 19 | **Blending Data-Driven Priors in Dynamic Games** | Justin Lidard; Haimin Hu; Asher J. Hancock *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.020) | — |

---

## 📈 Trends & Statistics

### Robot Type Distribution (2024–2025 real papers)

| Robot Type | Count | Share |
|------------|-------|-------|
| 其他/通用 | 58 | 74% |
| 机械臂/灵巧手 | 13 | 17% |
| 轮型机器人 | 3 | 4% |
| 四足机器人 | 1 | 1% |
| 人形/双足 | 1 | 1% |
| 多机器人/集群 | 1 | 1% |
| 手术/医疗机器人 | 1 | 1% |

### Papers per Venue

| Year | CoRL | ICRA | IROS | RSS |
|------|------|------|------|-----|
| 2024 | 10 | 20 | 9 | 19 |
| 2025 | — | 20 | — | — |

### 2026 Predicted Trend Keywords

`Human-Robot Interaction` `Autonomous Navigation` `Machine Learning in Robotics` `Healthcare Robotics` `Sustainable Automation` `Multi-Robot Systems` `Robotic Vision` `Field Robotics` `Soft Robotics` `Bio-inspired Robotics` `Aerial Robotics` `Legged & Bio-inspired Locomotion` `Manipulation & Grasping` `Search and Rescue` `Micro/Nano Robotics` `VLA Inference Efficiency` `BudgetLoop-VLA` `Cache-to-Think`

---

## 🤝 Contributing

Contributions are welcome! If you find missing papers, wrong classifications, or would like to add code links:

1. Fork this repository
2. Edit `datasets/robotics_papers_2024_2026_analysis.csv` (main four venues) **or** extend a CSV under `research_tracks/` for special topics
3. **Propose new research tracks or directions:** add a Markdown file under `proposals/`
4. **Cross-check new entries:** verify paper metadata against the official venue page or arXiv abstract and keep titles / author lists / venues consistent with the already-indexed rows
5. Run `python scripts/build_readme.py` from the repository root to regenerate both READMEs
6. Open a Pull Request

---

## 📜 License

This project is released under the [MIT License](LICENSE).

---

<p align="center">
  <i>Made with ❤️ for the robotics research community</i>
  <i>Data sources: ICRA / IROS / RSS / CoRL proceedings 2024–2026 + arXiv research-track preprints</i>
  <i>Inspired by <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a></i>
</p>
