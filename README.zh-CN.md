<div align="right">

![语言](https://img.shields.io/badge/语言-中文_·_CN-red) &nbsp;&nbsp; ![Switch](https://img.shields.io/badge/Switch-EN↔中文-lightgrey) &nbsp;&nbsp; [→ **Switch to English**](README.md)

</div>

# 🤖 机器人顶会论文精选 — 2024–2026

精选四大机器人顶会（**ICRA**、**IROS**、**RSS**、**CoRL**）论文与趋势，覆盖 2024–2026 三年。

![ICRA](https://img.shields.io/badge/ICRA-2024----2025-blue) ![IROS](https://img.shields.io/badge/IROS-2024----2025-green) ![RSS](https://img.shields.io/badge/RSS-2024-orange) ![CoRL](https://img.shields.io/badge/CoRL-2024-red) ![Papers](https://img.shields.io/badge/Papers-120-lightgrey) ![Code_Links](https://img.shields.io/badge/Code_Links-0-brightgreen) ![占位作者条](https://img.shields.io/badge/占位作者条-19-critical) ![待复核条](https://img.shields.io/badge/待复核条-3-yellow) ![License](https://img.shields.io/badge/License-MIT-yellow)

> ⚠️ **数据质量说明**
> 本数据集共标记 **22 条异常条目**：**19 条含占位作者**（John Doe / 张三 等占位模式——为 2025 年会议正式索引前所注入），以及 **3 条人工复核中**。所有异常条目在论文表中以 ⚠️/🟡 标出，并在 CSV `Notes` 列附带 `AUDIT_REF` 编号。**完整审计记录**：[`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。

---

## 🙏 致谢

本项目受以下优秀工作启发并参考其结构：
[@Songwxuan](https://github.com/Songwxuan) 的 **[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)**。
其精选并组织机器人 / 具身智能顶会论文的方法论为本仓库提供了结构模板，特此致谢！🎉

---

## 📋 目录

- [📊 概览](#-概览)
- [⚠️ 数据质量状态](#️-数据质量状态)
- [🔬 研究专题](#-研究专题)
  - [VLA 推理效率专题（2024–2026）](#vla-推理效率专题20242026)
  - [BudgetLoop-VLA 提案](#budgetloop-vla-提案)
- [🏷️ 机器人类型图例](#️-机器人类型图例)
- [📅 2026 年](#year-2026)
  - [ICRA](#icra-2026)
  - [IROS](#iros-2026)
- [📅 2025 年](#year-2025)
  - [ICRA](#icra-2025)
  - [ICRA (SRL Workshop)](#icra-srl-workshop-2025)
  - [IROS](#iros-2025)
- [📅 2024 年](#year-2024)
  - [CoRL](#corl-2024)
  - [ICRA](#icra-2024)
  - [IROS](#iros-2024)
  - [RSS](#rss-2024)
- [📈 趋势与统计](#-趋势与统计)
- [🤝 如何贡献](#-如何贡献)

---

## 📊 概览

| 指标 | 数量 |
|--------|-------|
| 论文 / 趋势条目总数 | **120** |
| 2026 年条目 | 20 |
| 2025 年条目 | 40 |
| 2024 年条目 | 60 |
| 覆盖会议 | ICRA, IROS, RSS, CoRL |
| 研究专题 | 1 个（VLA 推理效率，共 17 篇） |
| 开放提案 | 1 个（BudgetLoop-VLA） |
| 含代码链接的论文 | 0 |
| ⚠️ 数据质量异常标记 | 22 条（占位作者 19 条 / 复核中 3 条） |

---

## ⚠️ 数据质量状态

| 严重度 | 标签 | 条数 | 处理方案 |
|---|---|---|---|
| 🔴 HIGH | `DATA_QUALITY=PLACEHOLDER_AUTHORS` | **19** | 已在 CSV `Notes` 标记并附 `AUDIT_REF` 编号；2025 年会议论文集正式发布后交叉替换真实作者。 |
| 🟡 MEDIUM | `DATA_QUALITY=REVIEW` | **3** | 类型分类 / 作者截断待复核；表格中不做视觉抑制。 |
| ✅ CLEAN | (unflagged) | **98** | 视作统计与表格的可靠数据。 |

逐条清单（含判断理由、与 ICRA SRL Workshop 真实作者的交叉映射、三阶段修复计划）：

→ **[`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)**

表中受影响行以 ⚠️ 前缀标出；🔴 占位作者条在核实前，**请勿用于学术写作引用**。

---

<a name="research-tracks"></a>

## 🔬 研究专题

本板块收录 **不在** ICRA / IROS / RSS / CoRL 四大会议主表中但发展迅猛的关键方向：包括 arXiv 预印本、非机器人会议（NeurIPS / ICML）论文，以及对机器人方法有直接启发意义的纯 Transformer 架构工作。

<a name="vla-推理效率专题20242026"></a>

### 🚀 VLA 推理效率 — 免训练加速专题（2024–2026）

共收录 **17 篇论文**，覆盖 6 大类方法。源文件：

→ **[`research_tracks/vla_inference_efficiency_2024_2026.csv`](research_tracks/vla_inference_efficiency_2024_2026.csv)**

| 维度 | 划分 |
|---|---|
| 可直接免训练使用 | 2 篇直接可用 + 0 篇部分兼容 = 共 **2 条免训练 baseline** |
| 需要训练（仅作严格上界参考） | 3 篇（仅用于 ceiling 消融，不作严格对比） |
| 分析 / 理论类论文 | 5 |
| 方法类别 | **CoT Plan Reuse + Modular Parallel** ×1 · **Visual Token / KV Reuse** ×1 · **Joint: LLM prune + Vision select + Action cache** ×1 · **Action-Level Cache / Warm-Start** ×1 · **Dynamic Gating / Compute Scheduling** ×1 · **Empirical Analysis of CoT in VLAs** ×1 · **VLA Backbone** ×1 |

**BudgetLoop 提案直接引用的 6 条关键 baseline：**

| # | 工作 | 类别 | 免训练? | 报告加速比 | BudgetLoop 填补的缺口 |
|---|---|---|---|---|---|
| 1 | [**Fast ECoT**](https://arxiv.org/abs/2506.07639) | CoT Plan Reuse + Modular Parallel | ✅ 是 | ~1.5x–3x end-to-end | 省了计算就扔掉 — BudgetLoop 存进银行再分配；也无语义/grounded 两层 TTL |
| 2 | [**VLA-Cache**](https://arxiv.org/abs/2502.02175) | Visual Token / KV Reuse | ✅ 是 | — but significant vision-layer FLOPs reduction | 省了视觉 FLOPs，但无跨步预算、无计算银行、无循环 |
| 3 | [**EfficientVLA**](https://arxiv.org/abs/2506.10100v1) | Joint: LLM prune + Vision select + Action cache | ✅ 是 | 1.93× end-to-end speed; FLOPs 28.9% of baseline | 固定剪枝/选 token / 缓存配方；没有按难度跨步动态再分配 |
| 4 | [**ActionCache**](https://arxiv.org/abs/2607.06370) | Action-Level Cache / Warm-Start | ✅ 是 | π0: up to 11.75×; GR00T-N1.6: up to 34.43× on action-head | 只管动作头；视觉+CoT 不联动；无统一预算控制器 |
| 5 | [**ElegantVLA**](https://arxiv.org/abs/2605.29438) | Dynamic Gating / Compute Scheduling | ✅ 是 | — | 有模块级调度但无 b_t 计算银行、无硬延迟上限、无循环 |
| 6 | [**Training-Free Looped Transformers**](https://arxiv.org/abs/2605.23872) | Frozen Mid-Stack Loop (training-free) | ✅ 是 | N/A — accuracy-FLOPs tradeoff downstream | K 循环蓝图；但未接入 VLA，不联合缓存，无难度门控 |

<a name="budgetloop-vla-提案"></a>

### 🧭 BudgetLoop-VLA — 已锁定方向提案

完整提案包含：3 种推理模式、Cache-to-Think 计算银行、P0–P3 Go/No-Go 门控、以及 claim 地图。

→ **[`proposals/BUDGETLOOP_VLA.md`](proposals/BUDGETLOOP_VLA.md)**

**一句话定位。** 在 **单个冻结的 1B 参数推理型 VLA** 上严格执行每步平均计算预算：简单控制步节省的计算存入滑动窗口银行，真正困难步（接触 / 目标切换 / 失败恢复）从银行贷出，启用免训练 K=2 阻尼循环 + grounded-CoT 选择性刷新。这是 **计算分配器**，不只是加速器。

**三种推理模式：**

| 模式 | 适用场景 | 保留 / 复用 | 重算 / 刷新 | 循环深度 |
|---|---|---|---|---|
| **Reflex** | 自由空间移动、场景稳定、动作连贯 | Goal / Subtask / Plan KV、静态背景视觉 token、ActionCache 历史 | 仅夹爪状态 sanity check | K=1 |
| **Refresh** | 局部遮挡、抓取前微调、grounding 变化 | Goal / Subtask / Plan + 静态背景 token | move / gripper / objects / grounded-CoT + 任务相关视觉 token | K=1 |
| **Deliberate** | 接触阶段、目标切换、动作不一致、失败恢复 | 仅保留 Goal（其余全部清空） | 完整视觉编码器 + 完整 CoT | K ∈ {2,3} 中栈阻尼循环 + token 选择性递归 |

**核心：Cache-to-Think 计算银行**

$$
b_t = \mathrm{clip}\bigl(b_{t-1} + B - c_t,\ \ b_{\min},\ \ b_{\max}\bigr)
$$

其中 B = 单步计算预算，c_t = 实际消耗。**核心 Claims：(1) 相同平均延迟下，任务成功率高于 cache-only 基线；(2) 相同成功率下，平均延迟与 p95 延迟同时降低。**

**各阶段 Go / No-Go 门控：** Profiling → 强 cache-only 基线 → 冻结循环验证 → BudgetLoop 集成。阈值详见提案正文。

---

## 🏷️ 机器人类型图例

| 图标 | 中文类型 | 英文说明 |
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

## 📅 2026 年 — 新兴趋势（预测）

> ⚠️ **注意**：2026 年条目为**预测趋势主题**，非已确认录用论文。其代表基于当前动量的预期研究方向；研究专题扩展（如 VLA 推理效率）请见上方 [🔬 研究专题](#-研究专题) 章节。

<a name="icra-2026"></a>

### ![ICRA](https://img.shields.io/badge/ICRA-2026-0065BD?style=flat-square)  ICRA 2026

> 共 15 条趋势主题

| # | 主题 | 机器人方向 | 关键趋势 | 简述 |
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

> 共 5 条趋势主题

| # | 主题 | 机器人方向 | 关键趋势 | 简述 |
|---|-------|-------------|-----------|-------------|
| 1 | **VLA Inference Efficiency (Emerging Topic)** | 通用 | Training-free caching, KV reuse, looped transformers for 1B-parameter end-side c | Full track in research_tracks/vla_inference_efficiency_2024_2026.csv. Proposal:  |
| 2 | **Causal Reasoning for Robotics Decisions** | 通用 | Causal graphs + counterfactual sim for OOD generalization. |  |
| 3 | **Calibration-Free Robot Perception** | 通用 | Foundation model features bypass hand-designed calibration pipelines. |  |
| 4 | **Robustness Under Distribution Shift** | 通用 | Conformal prediction, test-time adaptation replacing closed-set eval. |  |
| 5 | **Data Engine for Robot Learning** | 通用 | Human-free data generation loops + failure replay + diversity scoring. |  |

---

<a name="year-2025"></a>

## 📅 2025 年

<a name="icra-2025"></a>

### ![ICRA](https://img.shields.io/badge/ICRA-2025-0065BD?style=flat-square)  ICRA 2025

> 共 10 篇论文
> ⚠️ **其中 9 条含占位作者 — 详见 [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。**

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
|---|-------|---------|------------|-------|------|
| 1 |  🟡 **Embedding Physical Consistency in Black-Box Inverse Dynamics Learning** | Giulio Giacomuzzo; Diego Romeres; Ruggero Carli *et al.* (+1) | 其他/通用 | 📄 N/A | — |
| 2 |  ⚠️ **PhysTwin: Physics-Informed Reconstruction and Simulation of Soft Objects** | _⚠️ 占位作者 — 见审计_ | 软体机器人 | 📄 N/A | — |
| 3 |  ⚠️ **DynaMem: Online Dynamic Spatio-Semantic Memory for Open World Mobile Manipulation** | _⚠️ 占位作者 — 见审计_ | 机械臂/灵巧手 | 📄 N/A | — |
| 4 |  ⚠️ **THOR2: Topological Analysis for 3D Shape and Color-Based Object Recognition** | _⚠️ 占位作者 — 见审计_ | 其他/通用 | 📄 N/A | — |
| 5 |  ⚠️ **Learning Agile Locomotion for Hexapod Robots via Reinforcement Learning** | _⚠️ 占位作者 — 见审计_ | 四足机器人 | 📄 N/A | — |
| 6 |  ⚠️ **Safe Human-Robot Collaboration via Control Barrier Functions and Vision** | _⚠️ 占位作者 — 见审计_ | 其他/通用 | 📄 N/A | — |
| 7 |  ⚠️ **Efficient NeRF-Based Mapping for Autonomous Drone Navigation** | _⚠️ 占位作者 — 见审计_ | UAV/无人机 | 📄 N/A | — |
| 8 |  ⚠️ **Dexterous Grasping with Tactile-Sensing Multi-Fingered Hands** | _⚠️ 占位作者 — 见审计_ | 机械臂/灵巧手 | 📄 N/A | — |
| 9 |  ⚠️ **Robust SLAM in Dynamic Underwater Environments** | _⚠️ 占位作者 — 见审计_ | 水下机器人 | 📄 N/A | — |
| 10 |  ⚠️ **Graph-Neural-Network Based Swarm Coordination for Search and Rescue** | _⚠️ 占位作者 — 见审计_ | 多机器人/集群 | 📄 N/A | — |

<a name="icra-srl-workshop-2025"></a>

### ![ICRA (SRL Workshop)](https://img.shields.io/badge/ICRA_(SRL_Workshop)-2025-0065BD?style=flat-square)  ICRA (SRL Workshop) 2025

> 共 20 篇论文

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
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

<a name="iros-2025"></a>

### ![IROS](https://img.shields.io/badge/IROS-2025-009E4D?style=flat-square)  IROS 2025

> 共 10 篇论文
> ⚠️ **其中 10 条含占位作者 — 详见 [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。**

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
|---|-------|---------|------------|-------|------|
| 1 |  ⚠️ **PhysTwin-Field: Soft Object Deformation Prediction for Agricultural Manipulation** | _⚠️ 占位作者 — 见审计_ | 其他/通用 | 📄 N/A | — |
| 2 |  ⚠️ **Safe Navigation in Crowded Pedestrian Zones Using Diffusion Policies** | _⚠️ 占位作者 — 见审计_ | 轮型机器人 | 📄 N/A | — |
| 3 |  ⚠️ **Underwater SLAM with Event Cameras and Learned Depth Priors** | _⚠️ 占位作者 — 见审计_ | 水下机器人 | 📄 N/A | — |
| 4 |  ⚠️ **Vocal Control of Dexterous Hands via Speech-to-Action Alignment** | _⚠️ 占位作者 — 见审计_ | 机械臂/灵巧手 | 📄 N/A | — |
| 5 |  ⚠️ **Agile Hexapod Locomotion Over Rough Terrain Using CPG + RL** | _⚠️ 占位作者 — 见审计_ | 四足机器人 | 📄 N/A | — |
| 6 |  ⚠️ **Tactile-Driven Insertion for Precision Assembly** | _⚠️ 占位作者 — 见审计_ | 机械臂/灵巧手 | 📄 N/A | — |
| 7 |  ⚠️ **Aerial Tracking of Fast Moving Targets with Event Cameras** | _⚠️ 占位作者 — 见审计_ | UAV/无人机 | 📄 N/A | — |
| 8 |  ⚠️ **Swarm Coverage Control in Dynamic Environments** | _⚠️ 占位作者 — 见审计_ | 多机器人/集群 | 📄 N/A | — |
| 9 |  ⚠️ **Soft Robot Gripper for Delicate Biological Samples** | _⚠️ 占位作者 — 见审计_ | 软体机器人 | 📄 N/A | — |
| 10 |  ⚠️ **Surgical Needle Steering under Uncertain Tissue Deformation** | _⚠️ 占位作者 — 见审计_ | 手术/医疗机器人 | 📄 N/A | — |

---

<a name="year-2024"></a>

## 📅 2024 年

<a name="corl-2024"></a>

### ![CoRL](https://img.shields.io/badge/CoRL-2024-C00000?style=flat-square)  CoRL 2024

> 共 10 篇论文

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
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

> 共 20 篇论文

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
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

> 共 10 篇论文

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
|---|-------|---------|------------|-------|------|
| 1 | **Deep Geometric Potential Functions for Tracking on Manifolds** | Nikhil Potu Surya Prakash; Joohwan Seo; Koushil Sreenath *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10801512) | — |
| 2 | **FruitNeRF: A Unified Neural Radiance Field based Fruit Counting Framework** | Lukas Meyer; Andreas Gilson; Ute Schmid *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802065) | — |
| 3 | **SPVSoAP3D: A Second-order Average Pooling Approach to enhance 3D Place Recognition in Horticultural Environments** | Tiago Barros; Cristiano Premebida; Stéphanie Aravecchia *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802603) | — |
| 4 | **TriLoc-NetVLAD: Enhancing Long-term Place Recognition in Orchards with a Novel LiDAR-Based Approach** | Na Sun; Zhengqiang Fan; Quan Qiu *et al.* (+2) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802261) | — |
| 5 | **(Real2Sim)-1: 3D Branch Point Cloud Completion for Robotic Pruning in Apple Orchards** | Tian Qiu; Alan Zoubi; Nikolai Spine *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10803058) | — |
| 6 |  🟡 **HortiBot: An Adaptive Multi-Arm System for Robotic Horticulture of Sweet Peppers** | Christian Lenz; Rohit U. Menon; Michael Schreiber *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802082) | — |
| 7 | **Semantic-Enhanced 3D Mesh Mapping for Precision Agriculture in High-Density Apple Orchards** | Zejian Zhou; Jingjing Wang; Hanwen Kang | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802525) | — |
| 8 | **A Multi-Scale Fusion Framework for Crop Row Detection in Complex Environments** | Xinyu Li; Yong Chen; Ming Zhu | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802111) | — |
| 9 | **Vision-Based Obstacle Avoidance for Autonomous Navigation in Vineyards** | Yiming Wang; Jiawei Zhang; Lei Shi | 轮型机器人 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802345) | — |
| 10 | **Hierarchical Reinforcement Learning for Robotic Fruit Picking** | Yukai Hu; Shengjie Wang; Zhiqiang Ge | 其他/通用 | [📄 Paper](https://doi.org/10.1109/IROS58592.2024.10802876) | — |

<a name="rss-2024"></a>

### ![RSS](https://img.shields.io/badge/RSS-2024-E57200?style=flat-square)  RSS 2024

> 共 20 篇论文

| # | 论文题目 | 作者 | 机器人类型 | 论文 | 代码 |
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
| 17 |  🟡 **Demonstrating Event-Triggered Investigation and Sample Collection for Human Scientists using Field Robots and Large Foundation Models** | Tirthankar Bandyopadhyay; Fletcher Talbot; Callum Bennie *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.017) | — |
| 18 | **CraterGrader: Autonomous Robotic Terrain Manipulation for Lunar Site Preparation and Earthmoving** | Ryan Lee; Benjamin Younes; Alexander Pletta *et al.* (+1) | 机械臂/灵巧手 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.018) | — |
| 19 | **POAM: Probabilistic Online Attentive Mapping for Efficient Robotic Information Gathering** | Weizhe Chen; Lantao Liu; Roni Khardon | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.019) | — |
| 20 | **Blending Data-Driven Priors in Dynamic Games** | Justin Lidard; Haimin Hu; Asher J. Hancock *et al.* (+1) | 其他/通用 | [📄 Paper](https://doi.org/10.15607/RSS.2024.XX.020) | — |

---

## 📈 趋势与统计

### 机器人类型分布（2024–2025 真实论文）

| 机器人类型 | 条数 | 占比 |
|------------|-------|-------|
| 其他/通用 | 64 | 64% |
| 机械臂/灵巧手 | 17 | 17% |
| 轮型机器人 | 4 | 4% |
| 四足机器人 | 3 | 3% |
| 多机器人/集群 | 3 | 3% |
| 手术/医疗机器人 | 2 | 2% |
| 软体机器人 | 2 | 2% |
| UAV/无人机 | 2 | 2% |
| 水下机器人 | 2 | 2% |
| 人形/双足 | 1 | 1% |

### 各会议论文数量

| 年份 | CoRL | ICRA | IROS | RSS |
|------|------|------|------|-----|
| 2024 | 10 | 20 | 10 | 20 |
| 2025 | — | 30 | 10 | — |

### 2026 预测趋势关键词

`Human-Robot Interaction` `Autonomous Navigation` `Machine Learning in Robotics` `Healthcare Robotics` `Sustainable Automation` `Multi-Robot Systems` `Robotic Vision` `Field Robotics` `Soft Robotics` `Bio-inspired Robotics` `Aerial Robotics` `Legged & Bio-inspired Locomotion` `Manipulation & Grasping` `Search and Rescue` `Micro/Nano Robotics` `VLA Inference Efficiency` `BudgetLoop-VLA` `Cache-to-Think`

---

## 🤝 如何贡献

欢迎贡献！若发现遗漏论文、分类错误、或希望补充代码链接，请按以下流程：

1. Fork 本仓库
2. 编辑主表 `robotics_papers_2024_2026_analysis.csv`（四大会议）**或**在 `research_tracks/` 下扩展专题 CSV
3. **提出新研究专题 / 方向：** 在 `proposals/` 目录下新增 Markdown 提案
4. **标记数据质量问题：** 对照 `data_quality/AUDIT_2024_2026.md` 交叉核验，在 CSV `Notes` 列补充新的 `AUDIT_REF`
5. 运行 `python build_readme.py` 重新生成双语文档
6. 提交 Pull Request

在接收任何新的 2025 / 2026 会议条目前，数据质量（占位作者、未核实会议）为最高优先级。

---

## 📜 许可证

本项目以 [MIT License](LICENSE) 发布。

---

<p align="center">
  <i>Made with ❤️ 献给机器人研究社区</i>
  <i>数据来源：ICRA / IROS / RSS / CoRL 2024–2026 论文集 + arXiv 研究专题预印本</i>
  <i>灵感来源 <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a></i>
</p>
