"""Generate bilingual README from the main CSV + research tracks.

Outputs:
  - README.md         (English, default GitHub landing)
  - README.zh-CN.md   (Simplified Chinese mirror)

Both files carry a top-of-page language-switcher badge that points at
the other file, matching standard bilingual GitHub repository UX.
"""
import csv, os
from collections import defaultdict, Counter

BASE    = os.path.dirname(os.path.abspath(__file__))
CSV_MAIN = os.path.join(BASE, "robotics_papers_2024_2026_analysis.csv")
CSV_VLA  = os.path.join(BASE, "research_tracks", "vla_inference_efficiency_2024_2026.csv")
OUT_EN   = os.path.join(BASE, "README.md")
OUT_ZH   = os.path.join(BASE, "README.zh-CN.md")

# ── Translation dictionary (UI strings only; CSV content is never translated) ─
TRANSLATIONS = {
    "en": {
        "header_title": "# 🤖 Robotics Top Conference Papers — 2024-2026",
        "header_desc": "A curated collection of robotics papers from the four premier conferences:\n**ICRA**, **IROS**, **RSS**, and **CoRL** — spanning 2024, 2025, and 2026 trends.",
        "lang_en": "English",
        "lang_zh": "简体中文",
        "badge_placeholder": "Placeholder_Papers",
        "badge_review": "Review_Flagged",
        "dq_banner_title": "⚠️ **Data Quality Notice**",
        "dq_banner_body": lambda dq_total,dq_placeholder,dq_review:
            f"This dataset carries **{dq_total} flagged entries**: **{dq_placeholder} with placeholder authors** (John Doe / Zhang San patterns — injected before 2025 venues were indexed) and **{dq_review} flagged for review**. All are marked ⚠️/🟡 in paper tables and carry an `AUDIT_REF` in the CSV `Notes` column. **Full audit**: [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md).",
        "ack_title": "## 🙏 Acknowledgement",
        "ack_body": """This project is inspired by and references the excellent work:
**[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)** by [@Songwxuan](https://github.com/Songwxuan).
Their methodology for curating and organizing top-conference robotics / embodied AI papers provided
the structural template for this repository. Many thanks! 🎉""",
        "toc_title": "## 📋 Table of Contents",
        "toc_overview": "[📊 Overview](#-overview)",
        "toc_dq":       "[⚠️ Data Quality Status](#️-data-quality-status)",
        "toc_rt":       "[🔬 Research Tracks](#-research-tracks)",
        "toc_vla":      "[VLA Inference Efficiency (2024–2026)](#vla-inference-efficiency-20242026)",
        "toc_bl":       "[BudgetLoop-VLA Proposal](#budgetloop-vla-proposal)",
        "toc_legend":   "[🏷️ Robot Type Legend](#️-robot-type-legend)",
        "toc_year_prefix": "[📅 {y}](#year-{y})",
        "toc_venue_prefix": "[{v}](#{sub}-{y})",
        "toc_trends":   "[📈 Trends & Statistics](#-trends--statistics)",
        "toc_contrib":  "[🤝 Contributing](#-contributing)",
        "overview_title": "## 📊 Overview",
        "ov_metric": "Metric",
        "ov_count": "Count",
        "ov_total": "Total Papers / Trend Entries",
        "ov_year_entries": "{y} entries",
        "ov_venues": "Venues covered",
        "ov_tracks": "Research tracks",
        "ov_tracks_val": lambda n: f"1 (VLA inference efficiency, {n} papers)",
        "ov_proposals": "Open proposals",
        "ov_proposals_val": "1 (BudgetLoop-VLA)",
        "ov_code": "Papers with code links",
        "ov_dq_flagged": lambda dq_total,dq_placeholder,dq_review: f"⚠️ Data-quality flagged",
        "ov_dq_flagged_val": lambda dq_total,dq_placeholder,dq_review: f"{dq_total} ({dq_placeholder} placeholder authors, {dq_review} review)",
        "dq_title": "## ⚠️ Data Quality Status",
        "dq_severity": "Severity",
        "dq_tag": "Tag",
        "dq_count": "Count",
        "dq_res": "Resolution",
        "dq_high_res": "Marked in CSV `Notes`; carrying `AUDIT_REF`; to be cross-replaced once 2025 proceedings publish.",
        "dq_med_res":  "Type-classification or authorship-truncation review; not suppressed.",
        "dq_clean_res": "Treated as ground truth for stats / tables.",
        "dq_full_title": "Full itemized list with rationale, cross-references to SRL Workshop real-author counterparts, and remediation plan:",
        "dq_warn_cite": "Affected rows in paper tables carry a ⚠️ prefix. Do not cite the 🔴 placeholder-author entries in academic writing before verification.",
        "rt_title": "## 🔬 Research Tracks",
        "rt_intro": "Dedicated deep-dives on fast-moving topics **outside** the ICRA/IROS/RSS/CoRL four-venue main CSV — including arXiv preprints, non-robotics venues (NeurIPS/ICML), and pure Transformer architecture work that informs robotics methods.",
        "vla_title": "### 🚀 VLA Inference Efficiency — Training-Free Acceleration (2024–2026)",
        "vla_intro": lambda n: f"Curated **{n} papers** spanning 6 method categories. Source file:",
        "vla_dim": "Dimension",
        "vla_bd": "Breakdown",
        "vla_tf_compat": lambda yes,partial: f"Training-free compatible",
        "vla_tf_compat_val": lambda yes,partial: f"{yes} directly usable + {partial} partial = **{yes+partial} training-free baseline pool**",
        "vla_tf_no": "Trained (strict upper bounds only)",
        "vla_tf_no_val": lambda no: f"{no} (used for ceiling ablations not strict comparison)",
        "vla_analysis": "Analysis / theory papers",
        "vla_categories": "Method categories",
        "vla_top_intro": "**Key baselines referenced by the BudgetLoop proposal:**",
        "vla_top_h_work": "Work",
        "vla_top_h_cat": "Category",
        "vla_top_h_tf": "Training-Free?",
        "vla_top_h_sp": "Reported speedup",
        "vla_top_h_gap": "Gap BudgetLoop fills",
        "vla_tf_yes": "✅ YES",
        "vla_tf_no_": "❌ NO",
        "vla_tf_other": lambda v: f"🟡 {v}",
        "bl_title": "### 🧭 BudgetLoop-VLA — Locked Research Direction",
        "bl_intro": "Full proposal with 3 modes, Cache-to-Think bank, P0–P3 gates, and claim map:",
        "bl_oneline": """**One-line framing.** Under a fixed per-step average compute budget on a **single frozen 1B-parameter reasoning VLA**, deposit surplus compute from easy control steps into a sliding-window compute bank; re-deposit it into genuinely difficult steps (contact / target-switch / failure-recovery) by enabling a training-free K=2 damped loop + grounded CoT selective refresh. This is a **compute allocator**, not just an accelerator.""",
        "bl_3m_title": "**Three modes:**",
        "bl_3m_h_mode": "Mode",
        "bl_3m_h_scenario": "Scenario",
        "bl_3m_h_reused": "Reused",
        "bl_3m_h_refreshed": "Refreshed",
        "bl_3m_h_loop": "Loop depth",
        "bl_3m_reflex_s":      "Free-space motion, stable scene, actions consistent",
        "bl_3m_reflex_reused": "goal/subtask/plan, static visual KV, ActionCache",
        "bl_3m_reflex_refr":   "Gripper sanity only",
        "bl_3m_refresh_s":     "Occlusion, pre-grasp micro-adjust, grounding change",
        "bl_3m_refresh_reused":"goal/subtask/plan + static background",
        "bl_3m_refresh_refr":  "move / gripper / objects / grounded-CoT + task-relevant visual tokens",
        "bl_3m_delib_s":       "Contact, target switch, action inconsistency, failure recovery",
        "bl_3m_delib_reused":  "goal only",
        "bl_3m_delib_refr":    "Full vision + full CoT",
        "bl_3m_delib_loop":    "K∈{2,3} damped mid-stack, token-selective",
        "bl_bank_title": "**Core bank:**",
        "bl_bank_claim": """with B = per-step budget, c_t = actual compute consumed. **Claims: (1) same avg latency → higher task success than cache-only baselines; (2) same success → both mean AND p95 latency lower.**""",
        "bl_gates_title": "**Go / No-Go gates before each stage:** Profiling → strong cache-only baseline → frozen loop → BudgetLoop integrated. See proposal for thresholds.",
        "legend_title": "## 🏷️ Robot Type Legend",
        "legend_h_icon": "Icon",
        "legend_h_cn":   "Type (CN)",
        "legend_h_desc": "Description",
        "year_trend_title": "## 📅 {y} — Emerging Trends (Predicted)",
        "year_trend_note": "⚠️ **Note**: 2026 entries are **predicted trend topics**, not confirmed accepted papers.\nThey represent anticipated research directions based on current momentum.\nResearch-track extensions (e.g. VLA Inference Efficiency) live in the [🔬 Research Tracks](#-research-tracks) section above.",
        "year_title": "## 📅 {y}",
        "venue_count_plain": lambda n: f"{n} papers",
        "venue_count_trend": lambda n: f"{n} trend topics",
        "venue_ph_warn": lambda n: f"⚠️ **{n} entries carry placeholder authors — see [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md).**",
        "trend_h_num": "#",
        "trend_h_topic": "Topic",
        "trend_h_rt":    "Robot Focus",
        "trend_h_kw":    "Key Trend",
        "trend_h_desc":  "Description",
        "paper_h_num":   "#",
        "paper_h_title": "Title",
        "paper_h_auth":  "Authors",
        "paper_h_rt":    "Robot Type",
        "paper_h_paper": "Paper",
        "paper_h_code":  "Code",
        "paper_ph_auth": "_⚠️ Placeholder — see audit_",
        "trends_title":  "## 📈 Trends & Statistics",
        "trends_rt_dist": "### Robot Type Distribution (2024-2025 papers)",
        "trends_rt_type": "Robot Type",
        "trends_rt_count": "Count",
        "trends_rt_share": "Share",
        "trends_per_venue": "### Papers per Venue",
        "trends_pv_year": "Year",
        "trends_2026kw":   "### 2026 Predicted Trend Keywords",
        "contrib_title":   "## 🤝 Contributing",
        "contrib_intro": "Contributions are welcome! If you find missing papers, wrong classifications,\nor want to add code links:",
        "contrib_step_1": "Fork this repository",
        "contrib_step_2": "Edit `robotics_papers_2024_2026_analysis.csv` (main venues) **or** extend CSVs inside `research_tracks/` for special topics",
        "contrib_step_3": "**Propose new research tracks or directions:** add a file under `proposals/`",
        "contrib_step_4": "**Flag data quality issues:** cross-check against the audit at `data_quality/AUDIT_2024_2026.md` and add new `AUDIT_REF` markers in CSV Notes",
        "contrib_step_5": "Run `python build_readme.py` to regenerate the README",
        "contrib_step_6": "Submit a Pull Request",
        "contrib_dq_note": "Data quality (placeholder authors, unverified venues) takes highest priority before any new 2025/2026 venue entries are accepted.",
        "license_title": "## 📜 License",
        "license_body": "This project is licensed under the [MIT License](LICENSE).",
        "footer_line1": "Made with ❤️ for the robotics research community",
        "footer_line2": "Data sourced from ICRA, IROS, RSS, CoRL proceedings (2024–2026) plus arXiv research-track preprints.",
        "footer_line3": 'Inspired by <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a>',
    },
    "zh-CN": {
        "header_title": "# 🤖 机器人顶会论文精选 — 2024–2026",
        "header_desc": "精选四大机器人顶会（**ICRA**、**IROS**、**RSS**、**CoRL**）论文，覆盖 2024–2026 研究趋势。",
        "lang_en": "English",
        "lang_zh": "简体中文",
        "badge_placeholder": "占位作者条",
        "badge_review": "待复核条",
        "dq_banner_title": "⚠️ **数据质量说明**",
        "dq_banner_body": lambda dq_total,dq_placeholder,dq_review:
            f"本数据集共标记 **{dq_total} 条异常条目**：其中 **{dq_placeholder} 条含占位作者**（John Doe / 张三模式 — 在 2025 年会议正式录用名单发布前为占位注入）以及 **{dq_review} 条待复核**。所有异常条目在论文表中以 ⚠️/🟡 标出，并在 CSV 的 `Notes` 列附 `AUDIT_REF` 编号。**完整审计**：[`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。",
        "ack_title": "## 🙏 致谢",
        "ack_body": """本项目受并引用以下优秀工作的启发：
[@Songwxuan](https://github.com/Songwxuan) 的 **[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)**。
其精选并组织顶会机器人 / 具身智能论文的方法论为本仓库提供了结构模板，特此致谢！🎉""",
        "toc_title": "## 📋 目录",
        "toc_overview": "[📊 概览](#-概览)",
        "toc_dq":       "[⚠️ 数据质量状态](#️-数据质量状态)",
        "toc_rt":       "[🔬 研究专题](#-研究专题)",
        "toc_vla":      "[VLA 推理效率专题（2024–2026）](#vla-推理效率专题20242026)",
        "toc_bl":       "[BudgetLoop-VLA 提案](#budgetloop-vla-提案)",
        "toc_legend":   "[🏷️ 机器人类型图例](#️-机器人类型图例)",
        "toc_year_prefix": "[📅 {y} 年](#year-{y})",
        "toc_venue_prefix": "[{v}](#{sub}-{y})",
        "toc_trends":   "[📈 趋势与统计](#-趋势与统计)",
        "toc_contrib":  "[🤝 贡献方式](#-贡献方式)",
        "overview_title": "## 📊 概览",
        "ov_metric": "指标",
        "ov_count": "数量",
        "ov_total": "论文 / 趋势条目总数",
        "ov_year_entries": "{y} 年条目",
        "ov_venues": "覆盖会议",
        "ov_tracks": "研究专题数",
        "ov_tracks_val": lambda n: f"1 个（VLA 推理效率，共 {n} 篇）",
        "ov_proposals": "开放提案数",
        "ov_proposals_val": "1 个（BudgetLoop-VLA）",
        "ov_code": "含代码链接的论文",
        "ov_dq_flagged": lambda dq_total,dq_placeholder,dq_review: f"⚠️ 数据质量异常标记",
        "ov_dq_flagged_val": lambda dq_total,dq_placeholder,dq_review: f"{dq_total}（占位作者 {dq_placeholder} 条，待复核 {dq_review} 条）",
        "dq_title": "## ⚠️ 数据质量状态",
        "dq_severity": "严重度",
        "dq_tag": "标签",
        "dq_count": "条数",
        "dq_res": "解决方案",
        "dq_high_res": "已在 CSV `Notes` 标记并附带 `AUDIT_REF`；待 2025 年会议论文集正式发布后交叉替换真实作者。",
        "dq_med_res":  "类型分类或作者截断待复核；未在表格中视觉抑制。",
        "dq_clean_res": "视作统计 / 表格的可靠数据。",
        "dq_full_title": "逐条带理由的完整清单（含与 ICRA SRL Workshop 真实作者的交叉映射与修复计划）：",
        "dq_warn_cite": "论文表中受影响行以 ⚠️ 前缀标出。🔴 占位作者条未经验证前请勿用于学术写作引用。",
        "rt_title": "## 🔬 研究专题",
        "rt_intro": "本板块收录 **不属于** ICRA/IROS/RSS/CoRL 四大会主表、但发展迅速的重要方向：包括 arXiv 预印本、非机器人会议（NeurIPS/ICML）论文、以及对机器人方法有直接启发的纯 Transformer 架构工作。",
        "vla_title": "### 🚀 VLA 推理效率 — 免训练加速专题（2024–2026）",
        "vla_intro": lambda n: f"共收录 **{n} 篇论文**，覆盖 6 大类方法。源文件：",
        "vla_dim": "维度",
        "vla_bd":  "分布",
        "vla_tf_compat": lambda yes,partial: f"可直接免训练使用",
        "vla_tf_compat_val": lambda yes,partial: f"{yes} 篇可直接用 + {partial} 篇部分可用 = 共 **{yes+partial} 篇免训练 baseline 池**",
        "vla_tf_no": "需要训练（仅作严格上界）",
        "vla_tf_no_val": lambda no: f"{no} 篇（仅用于 ceiling 消融，不作严格对比）",
        "vla_analysis": "分析 / 理论类论文",
        "vla_categories": "方法类别",
        "vla_top_intro": "**BudgetLoop 提案引用的关键 baseline：**",
        "vla_top_h_work": "工作",
        "vla_top_h_cat":  "方法类别",
        "vla_top_h_tf":   "免训练?",
        "vla_top_h_sp":   "报告加速比",
        "vla_top_h_gap":  "BudgetLoop 填补的缺口",
        "vla_tf_yes": "✅ 是",
        "vla_tf_no_": "❌ 否",
        "vla_tf_other": lambda v: f"🟡 {v}",
        "bl_title": "### 🧭 BudgetLoop-VLA — 锁定方向提案",
        "bl_intro": "完整提案包含 3 模式表、Cache-to-Think 银行、P0–P3 Go/No-Go 门控与 claim 地图：",
        "bl_oneline": """**一句话定义。** 在 **单个冻结的 1B 参数推理型 VLA** 上，严格执行每步平均计算预算；简单控制步节省的计算存入滑动窗口计算银行，真正困难步（接触 / 目标切换 / 失败恢复）从银行贷出计算，开启免训练 K=2 阻尼循环 + grounded CoT 选择性刷新。这是一个 **计算分配器**，不只是加速器。""",
        "bl_3m_title": "**三种推理模式：**",
        "bl_3m_h_mode":      "模式",
        "bl_3m_h_scenario":  "使用场景",
        "bl_3m_h_reused":    "复用内容",
        "bl_3m_h_refreshed": "刷新内容",
        "bl_3m_h_loop":      "循环深度",
        "bl_3m_reflex_s":      "自由空间移动、场景稳定、动作连续",
        "bl_3m_reflex_reused": "goal/subtask/plan、静态视觉 KV、ActionCache",
        "bl_3m_reflex_refr":   "仅夹爪 sanity check",
        "bl_3m_refresh_s":     "局部遮挡、抓取前微调、视觉 grounding 变化",
        "bl_3m_refresh_reused":"goal/subtask/plan + 静态背景",
        "bl_3m_refresh_refr":  "move / gripper / objects / grounded-CoT + 任务相关视觉 token",
        "bl_3m_delib_s":       "接触、目标切换、动作不一致、失败恢复",
        "bl_3m_delib_reused":  "仅保留 goal",
        "bl_3m_delib_refr":    "完整视觉 + 完整 CoT",
        "bl_3m_delib_loop":    "K∈{2,3} 中栈阻尼 + token 选择性递归",
        "bl_bank_title": "**核心计算银行：**",
        "bl_bank_claim": """其中 B = 单步预算，c_t = 实际消耗。**核心 Claims：(1) 相同平均延迟下，任务成功率高于 cache-only 基线；(2) 相同成功率下，平均延迟与 p95 延迟同时降低。**""",
        "bl_gates_title": "**各阶段 Go / No-Go 门控：** Profiling → 强 cache-only 基线 → 冻结循环验证 → BudgetLoop 集成。阈值见提案正文。",
        "legend_title": "## 🏷️ 机器人类型图例",
        "legend_h_icon": "图标",
        "legend_h_cn":   "类型（中文）",
        "legend_h_desc": "英文说明",
        "year_trend_title": "## 📅 {y} 年 — 新兴趋势（预测）",
        "year_trend_note": "⚠️ **注意**：2026 年条目为**预测趋势主题**，非已确认录用论文。它们代表基于当前动量的预期研究方向。研究专题扩展（如 VLA 推理效率）见上方 [🔬 研究专题](#-研究专题) 章节。",
        "year_title": "## 📅 {y} 年",
        "venue_count_plain": lambda n: f"共 {n} 篇论文",
        "venue_count_trend": lambda n: f"共 {n} 条趋势主题",
        "venue_ph_warn": lambda n: f"⚠️ **其中 {n} 条含占位作者 — 详见 [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。**",
        "trend_h_num":   "#",
        "trend_h_topic": "主题",
        "trend_h_rt":    "机器人方向",
        "trend_h_kw":    "关键趋势",
        "trend_h_desc":  "描述",
        "paper_h_num":   "#",
        "paper_h_title": "论文题目",
        "paper_h_auth":  "作者",
        "paper_h_rt":    "机器人类型",
        "paper_h_paper": "论文",
        "paper_h_code":  "代码",
        "paper_ph_auth": "_⚠️ 占位作者 — 见审计_",
        "trends_title":  "## 📈 趋势与统计",
        "trends_rt_dist": "### 机器人类型分布（2024-2025 真实论文）",
        "trends_rt_type": "机器人类型",
        "trends_rt_count": "条数",
        "trends_rt_share": "占比",
        "trends_per_venue": "### 各会议论文数量",
        "trends_pv_year": "年份",
        "trends_2026kw":   "### 2026 预测趋势关键词",
        "contrib_title":   "## 🤝 贡献方式",
        "contrib_intro": "欢迎贡献！若发现遗漏论文、分类错误、或希望补充代码链接：",
        "contrib_step_1": "Fork 本仓库",
        "contrib_step_2": "编辑主表 `robotics_papers_2024_2026_analysis.csv`（四大会议）**或**在 `research_tracks/` 下扩展专题 CSV",
        "contrib_step_3": "**提出新研究专题或方向：** 在 `proposals/` 下新增提案文件",
        "contrib_step_4": "**标记数据质量问题：** 参考 `data_quality/AUDIT_2024_2026.md` 进行交叉核验，并在 CSV `Notes` 列新增 `AUDIT_REF` 标记",
        "contrib_step_5": "运行 `python build_readme.py` 重新生成 README",
        "contrib_step_6": "提交 Pull Request",
        "contrib_dq_note": "在接收任何新的 2025/2026 会议条目前，数据质量（占位作者、未核实会议）为最高优先级。",
        "license_title": "## 📜 许可证",
        "license_body": "本项目以 [MIT License](LICENSE) 发布。",
        "footer_line1": "Made with ❤️ 献给机器人研究社区",
        "footer_line2": "数据来源：ICRA / IROS / RSS / CoRL 2024–2026 正式论文集 + arXiv 研究专题预印本",
        "footer_line3": '灵感来源 <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a>',
    },
}

# TOC anchor mapping: EN → zh-CN (keeps GitHub anchor IDs in sync for the switcher)
ANCHOR_OVERVIEW = {"en": "-overview", "zh-CN": "-概览"}
ANCHOR_DQ       = {"en": "-data-quality-status", "zh-CN": "-数据质量状态"}
ANCHOR_RT       = {"en": "-research-tracks", "zh-CN": "-研究专题"}
ANCHOR_VLA      = {"en": "vla-inference-efficiency-20242026", "zh-CN": "vla-推理效率专题20242026"}
ANCHOR_BL       = {"en": "budgetloop-vla-proposal", "zh-CN": "budgetloop-vla-提案"}
ANCHOR_LEGEND   = {"en": "-robot-type-legend", "zh-CN": "-机器人类型图例"}
ANCHOR_TRENDS   = {"en": "-trends--statistics", "zh-CN": "-趋势与统计"}
ANCHOR_CONTRIB  = {"en": "-contributing", "zh-CN": "-贡献方式"}

# ── Load data once (global; never translated) ──────────────────────────────
rows     = list(csv.DictReader(open(CSV_MAIN, encoding="utf-8-sig")))
vla_rows = list(csv.DictReader(open(CSV_VLA, encoding="utf-8-sig"))) if os.path.exists(CSV_VLA) else []

data = defaultdict(lambda: defaultdict(list))
for r in rows:
    data[r["Year"]][r["Venue"]].append(r)

total       = len(rows)
code_found  = sum(1 for r in rows if r["Code Link"] not in ("NA", "N/A", ""))
years_present = sorted(data.keys())
dq_placeholder = sum(1 for r in rows if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in r.get("Notes",""))
dq_review      = sum(1 for r in rows if r.get("Notes","").startswith("DATA_QUALITY=REVIEW"))
dq_total       = dq_placeholder + dq_review

# ── Helpers (language-agnostic) ────────────────────────────────────────────
def badge(label, msg, color):
    label_ = label.replace("-", "--").replace(" ", "_")
    msg_   = msg.replace("-", "--").replace(" ", "_")
    return f"![{label}](https://img.shields.io/badge/{label_}-{msg_}-{color})"

def paper_link_md(link, title):
    return f"[📄 Paper]({link})" if (link and link not in ("NA","N/A","")) else "📄 N/A"

def code_link_md(link):
    return f"[💻 Code]({link})" if (link and link not in ("NA","N/A","")) else "—"

def dq_badge(notes):
    if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in notes: return " ⚠️ "
    if "DATA_QUALITY=REVIEW" in notes:              return " 🟡 "
    return ""

def robot_emoji(rt):
    mapping = {
        "UAV/无人机": "🚁", "四足机器人": "🐾", "人形/双足": "🤖",
        "轮型机器人": "🛞", "机械臂/灵巧手": "🦾", "自动驾驶车辆": "🚗",
        "水下机器人": "🌊", "手术/医疗机器人": "🏥", "软体机器人": "🪸",
        "多机器人/集群": "🐝",
    }
    for k, v in mapping.items():
        if k in rt: return f"{v} {rt}"
    return rt

def shorten_authors(authors):
    parts = [a.strip() for a in authors.split(";")]
    if len(parts) > 3:
        return "; ".join(parts[:3]) + f" *et al.* (+{len(parts)-3})"
    return authors

def lang_switcher_badges(current_lang):
    """Top-of-page bilingual switcher. Clickable with standard shields badges."""
    en_target = "README.md"
    zh_target = "README.zh-CN.md"
    active = badge("Language", "🌐 EN", "blue")  if current_lang == "en"    else badge("语言", "🌐 中文", "red")
    en = f"[![EN](https://img.shields.io/badge/{'🇬🇧_EN' if current_lang!='en' else '🇬🇧_EN_active'}-brightgreen)]({en_target} \"Switch to English\")"
    zh = f"[![中文](https://img.shields.io/badge/{'🇨🇳_中文' if current_lang!='zh-CN' else '🇨🇳_中文_已选中'}-red)]({zh_target} \"切换到简体中文\")"
    # Standard two-pill layout: current-language pill + switch pill
    current = badge("Language" if current_lang == "en" else "语言",
                    "EN · 英文" if current_lang == "en" else "中文 · CN",
                    "blue" if current_lang == "en" else "red")
    switch  = (f"[→ **Switch to English**]({en_target})"  if current_lang == "zh-CN"
          else  f"[→ **切换到简体中文**]({zh_target})")
    return f"{current} &nbsp;&nbsp; {badge('Switch', 'EN↔中文', 'lightgrey')} &nbsp;&nbsp; {switch}"

# ── Legend map (shared; UI strings translated in header) ───────────────────
legend_map = {
    "UAV/无人机":       ("🚁", "Unmanned Aerial Vehicle / Drone"),
    "四足机器人":        ("🐾", "Quadruped / Legged Robot"),
    "人形/双足":        ("🤖", "Humanoid / Biped Robot"),
    "轮型机器人":        ("🛞", "Wheeled / Mobile Robot"),
    "机械臂/灵巧手":     ("🦾", "Robotic Arm / Dexterous Hand"),
    "自动驾驶车辆":      ("🚗", "Autonomous Vehicle"),
    "水下机器人":        ("🌊", "Underwater Robot"),
    "手术/医疗机器人":   ("🏥", "Surgical / Medical Robot"),
    "软体机器人":        ("🪸", "Soft Robot"),
    "多机器人/集群":     ("🐝", "Swarm / Multi-Robot System"),
    "其他/通用":        ("⚙️", "General / Other"),
}

trend_keywords = [
    "Human-Robot Interaction", "Autonomous Navigation", "Machine Learning in Robotics",
    "Healthcare Robotics", "Sustainable Automation", "Multi-Robot Systems",
    "Robotic Vision", "Field Robotics", "Soft Robotics", "Bio-inspired Robotics",
    "Aerial Robotics", "Legged & Bio-inspired Locomotion", "Manipulation & Grasping",
    "Search and Rescue", "Micro/Nano Robotics", "VLA Inference Efficiency",
    "BudgetLoop-VLA", "Cache-to-Think",
]

# ── Core build function ─────────────────────────────────────────────────────
def build(lang: str) -> str:
    T = TRANSLATIONS[lang]
    L = []

    # 0. Language switcher (always first so GitHub renders at the very top)
    L.append('<div align="right">')
    L.append("")
    L.append(lang_switcher_badges(lang))
    L.append("")
    L.append('</div>')
    L.append("")

    # 1. Header
    L.append(T["header_title"])
    L.append("")
    L.append(T["header_desc"])
    L.append("")

    venue_badges = [
        badge("ICRA", "2024--2025", "blue"),
        badge("IROS", "2024--2025", "green"),
        badge("RSS",  "2024", "orange"),
        badge("CoRL", "2024", "red"),
        badge("Papers", str(total), "lightgrey"),
        badge("Code_Links", str(code_found), "brightgreen"),
    ]
    if dq_placeholder:
        venue_badges.append(badge(T["badge_placeholder"], str(dq_placeholder), "critical"))
    if dq_review:
        venue_badges.append(badge(T["badge_review"], str(dq_review), "yellow"))
    venue_badges.append(badge("License", "MIT", "yellow"))
    L.append(" ".join(venue_badges))
    L.append("")

    # 2. DQ banner
    if dq_total > 0:
        L.append(f"> {T['dq_banner_title']}")
        body = T["dq_banner_body"](dq_total, dq_placeholder, dq_review)
        L.append(f"> {body}")
        L.append("")

    # 3. Acknowledgement
    L.append("---"); L.append("")
    L.append(T["ack_title"]); L.append("")
    for ln in T["ack_body"].splitlines(): L.append(ln)
    L.append("")

    # 4. TOC
    L.append("---"); L.append("")
    L.append(T["toc_title"]); L.append("")
    L.append(f"- {T['toc_overview']}")
    L.append(f"- {T['toc_dq']}")
    L.append(f"- {T['toc_rt']}")
    L.append(f"  - {T['toc_vla']}")
    L.append(f"  - {T['toc_bl']}")
    L.append(f"- {T['toc_legend']}")
    for y in years_present:
        L.append(f"- {T['toc_year_prefix'].format(y=y)}")
        for v in sorted(data[y].keys()):
            sub = v.lower().replace(" ", "-").replace("(", "").replace(")", "")
            L.append(f"  - {T['toc_venue_prefix'].format(v=v, sub=sub, y=y)}")
    L.append(f"- {T['toc_trends']}")
    L.append(f"- {T['toc_contrib']}")
    L.append("")

    # 5. Overview
    L.append("---"); L.append("")
    L.append(T["overview_title"]); L.append("")
    L.append(f"| {T['ov_metric']} | {T['ov_count']} |")
    L.append("|--------|-------|")
    L.append(f"| {T['ov_total']} | **{total}** |")
    for y in years_present:
        cnt = sum(len(v) for v in data[y].values())
        L.append(f"| {T['ov_year_entries'].format(y=y)} | {cnt} |")
    L.append(f"| {T['ov_venues']} | ICRA, IROS, RSS, CoRL |")
    L.append(f"| {T['ov_tracks']} | {T['ov_tracks_val'](len(vla_rows))} |")
    L.append(f"| {T['ov_proposals']} | {T['ov_proposals_val']} |")
    L.append(f"| {T['ov_code']} | {code_found} |")
    if dq_total:
        L.append(f"| {T['ov_dq_flagged'](dq_total,dq_placeholder,dq_review)} | "
                 f"{T['ov_dq_flagged_val'](dq_total,dq_placeholder,dq_review)} |")
    L.append("")

    # 6. Data Quality
    L.append("---"); L.append("")
    L.append(T["dq_title"]); L.append("")
    L.append(f"| {T['dq_severity']} | {T['dq_tag']} | {T['dq_count']} | {T['dq_res']} |")
    L.append("|---|---|---|---|")
    if dq_placeholder:
        L.append(f"| 🔴 HIGH | `DATA_QUALITY=PLACEHOLDER_AUTHORS` | **{dq_placeholder}** | {T['dq_high_res']} |")
    if dq_review:
        L.append(f"| 🟡 MEDIUM | `DATA_QUALITY=REVIEW` | **{dq_review}** | {T['dq_med_res']} |")
    L.append(f"| ✅ CLEAN | (unflagged) | **{total-dq_total}** | {T['dq_clean_res']} |")
    L.append("")
    L.append(T["dq_full_title"]); L.append("")
    L.append("→ **[`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)**"); L.append("")
    L.append(T["dq_warn_cite"]); L.append("")

    # 7. Research Tracks
    L.append("---"); L.append("")
    L.append(f'<a name="research-tracks"></a>'); L.append("")
    L.append(T["rt_title"]); L.append("")
    L.append(T["rt_intro"]); L.append("")

    # 7.1 VLA track
    L.append(f'<a name="{ANCHOR_VLA[lang]}"></a>'); L.append("")
    L.append(T["vla_title"]); L.append("")
    L.append(T["vla_intro"](len(vla_rows))); L.append("")
    L.append("→ **[`research_tracks/vla_inference_efficiency_2024_2026.csv`](research_tracks/vla_inference_efficiency_2024_2026.csv)**"); L.append("")

    if vla_rows:
        cat_counter = Counter(r["Method Category"] for r in vla_rows if r.get("Method Category"))
        tf_counter  = Counter(r.get("Training-Free?","UNKNOWN") for r in vla_rows)
        def _tf(counter, keys): return sum(counter.get(k,0) for k in keys)
        tf_yes     = _tf(tf_counter, ["YES (no training)","YES","YES — fully frozen"])
        tf_partial = _tf(tf_counter, ["PARTIAL"])
        tf_no      = _tf(tf_counter, ["NO","NO (light router trained end-to-end)",
                                      "NO — TBPTT trains recurrent action head",
                                      "NO (architecture trained from scratch with loop)"])
        tf_analysis = sum(v for k,v in tf_counter.items() if k.startswith("N/A")) + tf_counter.get("N/A (analysis paper)",0)

        L.append(f"| {T['vla_dim']} | {T['vla_bd']} |")
        L.append("|---|---|")
        L.append(f"| {T['vla_tf_compat'](tf_yes,tf_partial)} | {T['vla_tf_compat_val'](tf_yes,tf_partial)} |")
        L.append(f"| {T['vla_tf_no']} | {T['vla_tf_no_val'](tf_no)} |")
        L.append(f"| {T['vla_analysis']} | {tf_analysis} |")
        cats = " · ".join(f"**{c}** ×{n}" for c,n in cat_counter.most_common(7))
        L.append(f"| {T['vla_categories']} | {cats} |")
        L.append("")

        top_ids = {"VLA-IE-001","VLA-IE-002","VLA-IE-003","VLA-IE-004","VLA-IE-005","VLA-IE-011"}
        top_rows = [r for r in vla_rows if r.get("Track ID") in top_ids]
        if top_rows:
            L.append(T["vla_top_intro"]); L.append("")
            L.append(f"| # | {T['vla_top_h_work']} | {T['vla_top_h_cat']} | {T['vla_top_h_tf']} | {T['vla_top_h_sp']} | {T['vla_top_h_gap']} |")
            L.append("|---|---|---|---|---|---|")
            for i, r in enumerate(sorted(top_rows, key=lambda x: x["Track ID"]), 1):
                gap = (r.get("Gaps BudgetLoop Exploits") or "see CSV")[:70]
                link = r.get("Paper Link") or ""
                title = r.get("Title","").split(":")[0].strip()
                speed = r.get("Reported Speedup") or "—"
                tf = r.get("Training-Free?","—")
                if "YES" in tf:         tf_md = T["vla_tf_yes"]
                elif "NO" in tf:        tf_md = T["vla_tf_no_"]
                else:                   tf_md = T["vla_tf_other"](tf)
                cat = r.get("Method Category","—")
                md_title = f"**{title}**"
                if link and link not in ("NA","N/A",""): md_title = f"[{md_title}]({link})"
                L.append(f"| {i} | {md_title} | {cat} | {tf_md} | {speed} | {gap} |")
            L.append("")

    # 7.2 BudgetLoop proposal
    L.append(f'<a name="{ANCHOR_BL[lang]}"></a>'); L.append("")
    L.append(T["bl_title"]); L.append("")
    L.append(T["bl_intro"]); L.append("")
    L.append("→ **[`proposals/BUDGETLOOP_VLA.md`](proposals/BUDGETLOOP_VLA.md)**"); L.append("")
    L.append(T["bl_oneline"]); L.append("")
    L.append(T["bl_3m_title"]); L.append("")
    L.append(f"| {T['bl_3m_h_mode']} | {T['bl_3m_h_scenario']} | {T['bl_3m_h_reused']} | {T['bl_3m_h_refreshed']} | {T['bl_3m_h_loop']} |")
    L.append("|---|---|---|---|---|")
    L.append(f"| **Reflex** | {T['bl_3m_reflex_s']} | {T['bl_3m_reflex_reused']} | {T['bl_3m_reflex_refr']} | K=1 |")
    L.append(f"| **Refresh** | {T['bl_3m_refresh_s']} | {T['bl_3m_refresh_reused']} | {T['bl_3m_refresh_refr']} | K=1 |")
    L.append(f"| **Deliberate** | {T['bl_3m_delib_s']} | {T['bl_3m_delib_reused']} | {T['bl_3m_delib_refr']} | {T['bl_3m_delib_loop']} |")
    L.append("")
    L.append(T["bl_bank_title"]); L.append("")
    L.append("$$")
    L.append("b_t = \\mathrm{clip}\\bigl(b_{t-1} + B - c_t,\\ \\ b_{\\min},\\ \\ b_{\\max}\\bigr)")
    L.append("$$")
    L.append("")
    L.append(T["bl_bank_claim"]); L.append("")
    L.append(T["bl_gates_title"]); L.append("")

    # 8. Robot Type Legend
    L.append("---"); L.append("")
    L.append(T["legend_title"]); L.append("")
    L.append(f"| {T['legend_h_icon']} | {T['legend_h_cn']} | {T['legend_h_desc']} |")
    L.append("|------|-----------|-------------|")
    for k, (icon, desc) in legend_map.items():
        L.append(f"| {icon} | {k} | {desc} |")
    L.append("")

    # 9. Year sections
    for year in years_present:
        is_trend = (year == "2026")
        L.append("---"); L.append("")
        L.append(f'<a name="year-{year}"></a>'); L.append("")
        if is_trend:
            L.append(T["year_trend_title"].format(y=year)); L.append("")
            for ln in T["year_trend_note"].splitlines(): L.append(f"> {ln}")
            L.append("")
        else:
            L.append(T["year_title"].format(y=year)); L.append("")

        for venue in sorted(data[year].keys()):
            venue_rows = data[year][venue]
            anchor_id = venue.lower().replace(" ", "-").replace("(","").replace(")","")
            L.append(f'<a name="{anchor_id}-{year}"></a>'); L.append("")
            vc = {"ICRA": "0065BD", "IROS": "009E4D", "RSS": "E57200", "CoRL": "C00000"}.get(venue.split()[0], "555555")
            L.append(f"### ![{venue}](https://img.shields.io/badge/{venue.replace(' ','_')}-{year}-{vc}?style=flat-square)  {venue} {year}")
            L.append("")
            cnt_ln = T["venue_count_trend"](len(venue_rows)) if is_trend else T["venue_count_plain"](len(venue_rows))
            L.append(f"> {cnt_ln}")
            ph_in_venue = sum(1 for r in venue_rows if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in r.get("Notes",""))
            if ph_in_venue:
                L.append(f"> {T['venue_ph_warn'](ph_in_venue)}")
            L.append("")
            if is_trend:
                L.append(f"| {T['trend_h_num']} | {T['trend_h_topic']} | {T['trend_h_rt']} | {T['trend_h_kw']} | {T['trend_h_desc']} |")
                L.append("|---|-------|-------------|-----------|-------------|")
                for i, r in enumerate(venue_rows, 1):
                    note = r.get("Notes", "")
                    trend_kw = desc_kw = ""
                    if "Trend:" in note:
                        for p in note.split("|"):
                            p = p.strip()
                            if p.startswith("Trend:"):  trend_kw = p[6:].strip()[:80]
                            elif p.startswith("Desc:"): desc_kw  = p[5:].strip()[:80]
                    rt = r["Robot Type"] if r["Robot Type"] not in ("NA","N/A") else "—"
                    title = r["Title"].replace("|","\\|")
                    L.append(f"| {i} | **{title}** | {rt} | {trend_kw} | {desc_kw} |")
            else:
                L.append(f"| {T['paper_h_num']} | {T['paper_h_title']} | {T['paper_h_auth']} | {T['paper_h_rt']} | {T['paper_h_paper']} | {T['paper_h_code']} |")
                L.append("|---|-------|---------|------------|-------|------|")
                for i, r in enumerate(venue_rows, 1):
                    title   = r["Title"].replace("|","\\|")
                    authors = r["Authors"]
                    notes   = r.get("Notes", "")
                    is_ph   = "DATA_QUALITY=PLACEHOLDER_AUTHORS" in notes
                    authors = T["paper_ph_auth"] if is_ph else shorten_authors(authors)
                    authors = authors.replace("|","\\|")
                    rt      = r["Robot Type"] if r["Robot Type"] not in ("NA","N/A","") else "⚙️ 其他/通用"
                    paper   = paper_link_md(r["Paper Link"], title)
                    code    = code_link_md(r["Code Link"])
                    bdg     = dq_badge(notes)
                    L.append(f"| {i} | {bdg}**{title}** | {authors} | {rt} | {paper} | {code} |")
            L.append("")

    # 10. Trends & Statistics
    L.append("---"); L.append("")
    L.append(T["trends_title"]); L.append("")
    L.append(T["trends_rt_dist"]); L.append("")
    L.append(f"| {T['trends_rt_type']} | {T['trends_rt_count']} | {T['trends_rt_share']} |")
    L.append("|------------|-------|-------|")
    paper_rows_only = [r for r in rows if r["Year"] in ("2024","2025")]
    tc2 = Counter(r["Robot Type"] for r in paper_rows_only if r["Robot Type"] not in ("NA","N/A",""))
    total_typed = sum(tc2.values())
    for t, c in tc2.most_common(10):
        pct = f"{100*c/total_typed:.0f}%"
        L.append(f"| {t} | {c} | {pct} |")
    L.append("")
    L.append(T["trends_per_venue"]); L.append("")
    L.append(f"| {T['trends_pv_year']} | CoRL | ICRA | IROS | RSS |")
    L.append("|------|------|------|------|-----|")
    for y in ["2024","2025"]:
        corl = len(data[y].get("CoRL",[]))
        icra = len(data[y].get("ICRA",[])) + len(data[y].get("ICRA (SRL Workshop)",[]))
        iros = len(data[y].get("IROS",[]))
        rss  = len(data[y].get("RSS",[]))
        L.append(f"| {y} | {corl or '—'} | {icra or '—'} | {iros or '—'} | {rss or '—'} |")
    L.append("")
    L.append(T["trends_2026kw"]); L.append("")
    L.append(" ".join(f"`{kw}`" for kw in trend_keywords))
    L.append("")

    # 11. Contributing
    L.append("---"); L.append("")
    L.append(T["contrib_title"]); L.append("")
    for ln in T["contrib_intro"].splitlines(): L.append(ln)
    L.append("")
    for i in range(1, 7):
        L.append(f"{i}. {T[f'contrib_step_{i}']}")
    L.append("")
    L.append(T["contrib_dq_note"]); L.append("")

    # 12. License + footer
    L.append("---"); L.append("")
    L.append(T["license_title"]); L.append("")
    L.append(T["license_body"]); L.append("")
    L.append("---"); L.append("")
    L.append('<p align="center">')
    L.append(f'  <i>{T["footer_line1"]}</i>')
    L.append(f'  <i>{T["footer_line2"]}</i>')
    L.append(f'  <i>{T["footer_line3"]}</i>')
    L.append('</p>')
    L.append("")

    return "\n".join(L)

# ── Write both files ────────────────────────────────────────────────────────
readme_en = build("en")
readme_zh = build("zh-CN")

with open(OUT_EN, "w", encoding="utf-8") as f: f.write(readme_en)
with open(OUT_ZH, "w", encoding="utf-8") as f: f.write(readme_zh)

print(f"README.md (EN)     : {len(readme_en):,} chars, {readme_en.count(chr(10))+1} lines")
print(f"README.zh-CN.md    : {len(readme_zh):,} chars, {readme_zh.count(chr(10))+1} lines")
print(f"Main CSV rows      : {total}   |   VLA track rows: {len(vla_rows)}")
print(f"Placeholder flagged: {dq_placeholder}   |   Review items: {dq_review}")
print("Done. Both bilingual readmes are in sync.")
