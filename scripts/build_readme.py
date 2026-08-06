"""Generate bilingual README from the main CSV + research tracks.

Usage:
  # from repo root (recommended)
  python scripts/build_readme.py

Outputs (always written to repository root):
  - README.md         (English, default GitHub landing)
  - README.zh-CN.md   (Simplified Chinese mirror)

Both files carry a top-of-page language-switcher badge that points at
the other file, matching standard bilingual GitHub repository UX.
"""
import csv, os, sys
from collections import defaultdict, Counter

# When invoked as scripts/build_readme.py, BASE should be the repo root
# (one level up from this file), so data paths and output paths stay stable
# regardless of cwd.
_HERE     = os.path.dirname(os.path.abspath(__file__))
BASE      = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE

# ---- Commit-1 partitioned CSVs ------------------------------------------------
# verified_papers.csv          -> SOLE SOURCE of public paper counts, overview,
#                                 venue tables, trend charts.
# pending_verification.csv     -> 19 placeholder + 3 review rows; NOT in stats.
# predicted_trends.csv         -> 2026-only trend topics; rendered in its own
#                                 demarcated section; NEVER counted in "Total
#                                 papers" or venue badges.
# robotics_papers_...csv       -> master backward-compat source for editors.
# vla_inference_efficiency.csv -> standalone research track (unchanged).
# ------------------------------------------------------------------------------
CSV_VER  = os.path.join(BASE, "datasets", "verified_papers.csv")
CSV_PEND = os.path.join(BASE, "datasets", "pending_verification.csv")
CSV_PRED = os.path.join(BASE, "datasets", "predicted_trends.csv")
CSV_MAIN = os.path.join(BASE, "datasets", "robotics_papers_2024_2026_analysis.csv")
CSV_VLA  = os.path.join(BASE, "research_tracks", "vla_inference_efficiency_2024_2026.csv")
OUT_EN   = os.path.join(BASE, "README.md")
OUT_ZH   = os.path.join(BASE, "README.zh-CN.md")

def _read_csv(p):
    with open(p, "r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

# ── Translation dictionary (UI strings only; CSV content is never translated) ─
TRANSLATIONS = {
    "en": {
        "header_title": "# 🤖 Robotics Top Conference Papers — 2024-2026",
        "header_desc": "A curated collection of robotics papers from the four premier conferences:\n**ICRA**, **IROS**, **RSS**, and **CoRL** — spanning 2024, 2025, and 2026 trends.",
        "lang_en": "English",
        "lang_zh": "Simplified Chinese",
        "badge_placeholder": "Placeholder_Papers",
        "badge_review": "Review_Flagged",
        "dq_banner_title": "⚠️ **Data Quality Notice**",
        "dq_banner_body": lambda dq_total,dq_placeholder,dq_review:
            f"This dataset carries **{dq_total} flagged entries**: **{dq_placeholder} with placeholder authors** (John Doe / Zhang San patterns — injected before 2025 venues were officially indexed) and **{dq_review} flagged for manual review**. All are marked ⚠️/🟡 in the paper tables and carry an `AUDIT_REF` ID in the CSV `Notes` column. **Full audit record**: [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md).",
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
        "dq_high_res": "Marked in CSV `Notes` with `AUDIT_REF` ID; cross-replace with real authors once 2025 proceedings are published.",
        "dq_med_res":  "Type-classification or authorship-truncation review pending; NOT visually suppressed in tables.",
        "dq_clean_res": "Treated as ground truth for statistics and tables.",
        "dq_full_title": "Full itemized list with rationale, cross-mappings to SRL Workshop real-author counterparts, and a three-stage remediation plan:",
        "dq_warn_cite": "Affected rows in paper tables carry a ⚠️ prefix. Do NOT cite the 🔴 placeholder-author entries in academic writing before verification.",
        "rt_title": "## 🔬 Research Tracks",
        "rt_intro": "Deep dives on fast-moving topics **outside** the ICRA/IROS/RSS/CoRL four-venue main CSV — including arXiv preprints, non-robotics venues (NeurIPS/ICML), and pure Transformer architecture work that directly shapes robotics methods.",
        "vla_title": "### 🚀 VLA Inference Efficiency — Training-Free Acceleration (2024–2026)",
        "vla_intro": lambda n: f"Curated **{n} papers** spanning 6 method categories. Source file:",
        "vla_dim": "Dimension",
        "vla_bd":  "Breakdown",
        "vla_tf_compat": lambda yes,partial: f"Training-free compatible",
        "vla_tf_compat_val": lambda yes,partial: f"{yes} directly usable + {partial} partially compatible = **{yes+partial} training-free baselines**",
        "vla_tf_no": "Requires training (strict upper bound only)",
        "vla_tf_no_val": lambda no: f"{no} (used for ceiling ablations, not strict comparison)",
        "vla_analysis": "Analysis / theory papers",
        "vla_categories": "Method categories",
        "vla_top_intro": "**Key baselines directly referenced by the BudgetLoop proposal:**",
        "vla_top_h_work": "Work",
        "vla_top_h_cat":  "Category",
        "vla_top_h_tf":   "Training-Free?",
        "vla_top_h_sp":   "Reported speedup",
        "vla_top_h_gap":  "Gap BudgetLoop fills",
        "vla_tf_yes": "✅ YES",
        "vla_tf_no_": "❌ NO",
        "vla_tf_other": lambda v: f"🟡 {v}",
        "bl_title": "### 🧭 BudgetLoop-VLA — Locked Research Direction",
        "bl_intro": "Full proposal: three reasoning modes, Cache-to-Think compute bank, P0–P3 Go/No-Go gates, and a claim map.",
        "bl_oneline": """**One-line framing.** On a **single frozen 1B-parameter reasoning VLA** with a fixed per-step average compute budget, deposit surplus compute from easy control steps into a sliding-window compute bank; spend it on genuinely hard steps (contact, target switch, failure recovery) by enabling a training-free K=2 damped loop plus grounded-CoT selective refresh. This is a **compute allocator**, not just an accelerator.""",
        "bl_3m_title": "**Three reasoning modes:**",
        "bl_3m_h_mode":      "Mode",
        "bl_3m_h_scenario":  "Scenario",
        "bl_3m_h_reused":    "Reused / held fixed",
        "bl_3m_h_refreshed": "Recomputed / refreshed",
        "bl_3m_h_loop":      "Loop depth",
        "bl_3m_reflex_s":      "Free-space motion, stable scene, consistent actions",
        "bl_3m_reflex_reused": "Goal / subtask / plan KV, static visual tokens, ActionCache history",
        "bl_3m_reflex_refr":   "Gripper sanity-check only",
        "bl_3m_refresh_s":     "Occlusion, pre-grasp micro-adjust, grounding drift",
        "bl_3m_refresh_reused":"Goal / subtask / plan + static background tokens",
        "bl_3m_refresh_refr":  "move / gripper / objects / grounded-CoT + task-relevant visual tokens",
        "bl_3m_delib_s":       "Contact, target switch, action inconsistency, failure recovery",
        "bl_3m_delib_reused":  "Goal only (everything else flushed)",
        "bl_3m_delib_refr":    "Full vision encoder + full CoT",
        "bl_3m_delib_loop":    "K ∈ {2,3} — damped mid-stack, token-selective",
        "bl_bank_title": "**Compute bank (Cache-to-Think):**",
        "bl_bank_claim": """where B = per-step compute budget, c_t = actual compute consumed. **Core claims: (1) Same average latency → higher task success than cache-only baselines; (2) Same success rate → BOTH mean and p95 latency are lower.**""",
        "bl_gates_title": "**Go / No-Go gates before each stage:** Profiling → strong cache-only baseline → frozen loop verification → BudgetLoop integrated. Hard thresholds are documented in the proposal.",
        "legend_title": "## 🏷️ Robot Type Legend",
        "legend_h_icon": "Icon",
        "legend_h_cn":   "Type (CN)",
        "legend_h_desc": "Description",
        "year_trend_title": "## 📅 {y} — Emerging Trends (Predicted)",
        "year_trend_note": "📌 **Note**: 2026 entries are **predicted trend topics**, not confirmed accepted papers. They represent research directions anticipated from current momentum. Research-track extensions (e.g., VLA Inference Efficiency) live in the [🔬 Research Tracks](#-research-tracks) section above.",
        "year_title": "## 📅 {y}",
        "venue_count_plain": lambda n: f"{n} papers",
        "venue_count_trend": lambda n: f"{n} trend topics",
        "venue_ph_warn": lambda n: f"⚠️ **{n} entries carry placeholder authors — see [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md).**",
        "trend_h_num":   "#",
        "trend_h_topic": "Topic",
        "trend_h_rt":    "Robot focus",
        "trend_h_kw":    "Key trend",
        "trend_h_desc":  "Short description",
        "paper_h_num":   "#",
        "paper_h_title": "Title",
        "paper_h_auth":  "Authors",
        "paper_h_rt":    "Robot Type",
        "paper_h_paper": "Paper",
        "paper_h_code":  "Code",
        "paper_ph_auth": "_⚠️ Placeholder — see audit_",
        "trends_title":  "## 📈 Trends & Statistics",
        "trends_rt_dist": "### Robot Type Distribution (2024–2025 real papers)",
        "trends_rt_type": "Robot Type",
        "trends_rt_count": "Count",
        "trends_rt_share": "Share",
        "trends_per_venue": "### Papers per Venue",
        "trends_pv_year": "Year",
        "trends_2026kw":   "### 2026 Predicted Trend Keywords",
        "contrib_title":   "## 🤝 Contributing",
        "contrib_intro": "Contributions are welcome! If you find missing papers, wrong classifications, or would like to add code links:",
        "contrib_step_1": "Fork this repository",
        "contrib_step_2": "Edit `datasets/robotics_papers_2024_2026_analysis.csv` (main four venues) **or** extend a CSV under `research_tracks/` for special topics",
        "contrib_step_3": "**Propose new research tracks or directions:** add a Markdown file under `proposals/`",
        "contrib_step_4": "**Cross-check new entries:** verify paper metadata against the official venue page or arXiv abstract and keep titles / author lists / venues consistent with the already-indexed rows",
        "contrib_step_5": "Run `python scripts/build_readme.py` from the repository root to regenerate both READMEs",
        "contrib_step_6": "Open a Pull Request",
        "contrib_dq_note": "Data quality (placeholder authors, unverified venues) is the highest priority before any new 2025/2026 venue entries are accepted.",
        "license_title": "## 📜 License",
        "license_body": "This project is released under the [MIT License](LICENSE).",
        "footer_line1": "Made with ❤️ for the robotics research community",
        "footer_line2": "Data sources: ICRA / IROS / RSS / CoRL proceedings 2024–2026 + arXiv research-track preprints",
        "footer_line3": 'Inspired by <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a>',
    },
    "zh-CN": {
        "header_title": "# 🤖 机器人顶会论文精选 — 2024–2026",
        "header_desc": "精选四大机器人顶会（**ICRA**、**IROS**、**RSS**、**CoRL**）论文与趋势，覆盖 2024–2026 三年。",
        "lang_en": "English",
        "lang_zh": "简体中文",
        "badge_placeholder": "占位作者条",
        "badge_review": "待复核条",
        "dq_banner_title": "⚠️ **数据质量说明**",
        "dq_banner_body": lambda dq_total,dq_placeholder,dq_review:
            f"本数据集共标记 **{dq_total} 条异常条目**：**{dq_placeholder} 条含占位作者**（John Doe / 张三 等占位模式——为 2025 年会议正式索引前所注入），以及 **{dq_review} 条人工复核中**。所有异常条目在论文表中以 ⚠️/🟡 标出，并在 CSV `Notes` 列附带 `AUDIT_REF` 编号。**完整审计记录**：[`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。",
        "ack_title": "## 🙏 致谢",
        "ack_body": """本项目受以下优秀工作启发并参考其结构：
[@Songwxuan](https://github.com/Songwxuan) 的 **[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)**。
其精选并组织机器人 / 具身智能顶会论文的方法论为本仓库提供了结构模板，特此致谢！🎉""",
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
        "toc_contrib":  "[🤝 如何贡献](#-如何贡献)",
        "overview_title": "## 📊 概览",
        "ov_metric": "指标",
        "ov_count": "数量",
        "ov_total": "论文 / 趋势条目总数",
        "ov_year_entries": "{y} 年条目",
        "ov_venues": "覆盖会议",
        "ov_tracks": "研究专题",
        "ov_tracks_val": lambda n: f"1 个（VLA 推理效率，共 {n} 篇）",
        "ov_proposals": "开放提案",
        "ov_proposals_val": "1 个（BudgetLoop-VLA）",
        "ov_code": "含代码链接的论文",
        "ov_dq_flagged": lambda dq_total,dq_placeholder,dq_review: f"⚠️ 数据质量异常标记",
        "ov_dq_flagged_val": lambda dq_total,dq_placeholder,dq_review: f"{dq_total} 条（占位作者 {dq_placeholder} 条 / 复核中 {dq_review} 条）",
        "dq_title": "## ⚠️ 数据质量状态",
        "dq_severity": "严重度",
        "dq_tag": "标签",
        "dq_count": "条数",
        "dq_res": "处理方案",
        "dq_high_res": "已在 CSV `Notes` 标记并附 `AUDIT_REF` 编号；2025 年会议论文集正式发布后交叉替换真实作者。",
        "dq_med_res":  "类型分类 / 作者截断待复核；表格中不做视觉抑制。",
        "dq_clean_res": "视作统计与表格的可靠数据。",
        "dq_full_title": "逐条清单（含判断理由、与 ICRA SRL Workshop 真实作者的交叉映射、三阶段修复计划）：",
        "dq_warn_cite": "表中受影响行以 ⚠️ 前缀标出；🔴 占位作者条在核实前，**请勿用于学术写作引用**。",
        "rt_title": "## 🔬 研究专题",
        "rt_intro": "本板块收录 **不在** ICRA / IROS / RSS / CoRL 四大会议主表中但发展迅猛的关键方向：包括 arXiv 预印本、非机器人会议（NeurIPS / ICML）论文，以及对机器人方法有直接启发意义的纯 Transformer 架构工作。",
        "vla_title": "### 🚀 VLA 推理效率 — 免训练加速专题（2024–2026）",
        "vla_intro": lambda n: f"共收录 **{n} 篇论文**，覆盖 6 大类方法。源文件：",
        "vla_dim": "维度",
        "vla_bd":  "划分",
        "vla_tf_compat": lambda yes,partial: f"可直接免训练使用",
        "vla_tf_compat_val": lambda yes,partial: f"{yes} 篇直接可用 + {partial} 篇部分兼容 = 共 **{yes+partial} 条免训练 baseline**",
        "vla_tf_no": "需要训练（仅作严格上界参考）",
        "vla_tf_no_val": lambda no: f"{no} 篇（仅用于 ceiling 消融，不作严格对比）",
        "vla_analysis": "分析 / 理论类论文",
        "vla_categories": "方法类别",
        "vla_top_intro": "**BudgetLoop 提案直接引用的 6 条关键 baseline：**",
        "vla_top_h_work": "工作",
        "vla_top_h_cat":  "类别",
        "vla_top_h_tf":   "免训练?",
        "vla_top_h_sp":   "报告加速比",
        "vla_top_h_gap":  "BudgetLoop 填补的缺口",
        "vla_tf_yes": "✅ 是",
        "vla_tf_no_": "❌ 否",
        "vla_tf_other": lambda v: f"🟡 {v}",
        "bl_title": "### 🧭 BudgetLoop-VLA — 已锁定方向提案",
        "bl_intro": "完整提案包含：3 种推理模式、Cache-to-Think 计算银行、P0–P3 Go/No-Go 门控、以及 claim 地图。",
        "bl_oneline": """**一句话定位。** 在 **单个冻结的 1B 参数推理型 VLA** 上严格执行每步平均计算预算：简单控制步节省的计算存入滑动窗口银行，真正困难步（接触 / 目标切换 / 失败恢复）从银行贷出，启用免训练 K=2 阻尼循环 + grounded-CoT 选择性刷新。这是 **计算分配器**，不只是加速器。""",
        "bl_3m_title": "**三种推理模式：**",
        "bl_3m_h_mode":      "模式",
        "bl_3m_h_scenario":  "适用场景",
        "bl_3m_h_reused":    "保留 / 复用",
        "bl_3m_h_refreshed": "重算 / 刷新",
        "bl_3m_h_loop":      "循环深度",
        "bl_3m_reflex_s":      "自由空间移动、场景稳定、动作连贯",
        "bl_3m_reflex_reused": "Goal / Subtask / Plan KV、静态背景视觉 token、ActionCache 历史",
        "bl_3m_reflex_refr":   "仅夹爪状态 sanity check",
        "bl_3m_refresh_s":     "局部遮挡、抓取前微调、grounding 变化",
        "bl_3m_refresh_reused":"Goal / Subtask / Plan + 静态背景 token",
        "bl_3m_refresh_refr":  "move / gripper / objects / grounded-CoT + 任务相关视觉 token",
        "bl_3m_delib_s":       "接触阶段、目标切换、动作不一致、失败恢复",
        "bl_3m_delib_reused":  "仅保留 Goal（其余全部清空）",
        "bl_3m_delib_refr":    "完整视觉编码器 + 完整 CoT",
        "bl_3m_delib_loop":    "K ∈ {2,3} 中栈阻尼循环 + token 选择性递归",
        "bl_bank_title": "**核心：Cache-to-Think 计算银行**",
        "bl_bank_claim": """其中 B = 单步计算预算，c_t = 实际消耗。**核心 Claims：(1) 相同平均延迟下，任务成功率高于 cache-only 基线；(2) 相同成功率下，平均延迟与 p95 延迟同时降低。**""",
        "bl_gates_title": "**各阶段 Go / No-Go 门控：** Profiling → 强 cache-only 基线 → 冻结循环验证 → BudgetLoop 集成。阈值详见提案正文。",
        "legend_title": "## 🏷️ 机器人类型图例",
        "legend_h_icon": "图标",
        "legend_h_cn":   "中文类型",
        "legend_h_desc": "英文说明",
        "year_trend_title": "## 📅 {y} 年 — 新兴趋势（预测）",
        "year_trend_note": "📌 **注意**：2026 年条目为**预测趋势主题**，非已确认录用论文。其代表基于当前动量的预期研究方向；研究专题扩展（如 VLA 推理效率）请见上方 [🔬 研究专题](#-研究专题) 章节。",
        "year_title": "## 📅 {y} 年",
        "venue_count_plain": lambda n: f"共 {n} 篇论文",
        "venue_count_trend": lambda n: f"共 {n} 条趋势主题",
        "venue_ph_warn": lambda n: f"⚠️ **其中 {n} 条含占位作者 — 详见 [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)。**",
        "trend_h_num":   "#",
        "trend_h_topic": "主题",
        "trend_h_rt":    "机器人方向",
        "trend_h_kw":    "关键趋势",
        "trend_h_desc":  "简述",
        "paper_h_num":   "#",
        "paper_h_title": "论文题目",
        "paper_h_auth":  "作者",
        "paper_h_rt":    "机器人类型",
        "paper_h_paper": "论文",
        "paper_h_code":  "代码",
        "paper_ph_auth": "_⚠️ 占位作者 — 见审计_",
        "trends_title":  "## 📈 趋势与统计",
        "trends_rt_dist": "### 机器人类型分布（2024–2025 真实论文）",
        "trends_rt_type": "机器人类型",
        "trends_rt_count": "条数",
        "trends_rt_share": "占比",
        "trends_per_venue": "### 各会议论文数量",
        "trends_pv_year": "年份",
        "trends_2026kw":   "### 2026 预测趋势关键词",
        "contrib_title":   "## 🤝 如何贡献",
        "contrib_intro": "欢迎贡献！若发现遗漏论文、分类错误、或希望补充代码链接，请按以下流程：",
        "contrib_step_1": "Fork 本仓库",
        "contrib_step_2": "编辑主表 `datasets/robotics_papers_2024_2026_analysis.csv`（四大会议）**或**在 `research_tracks/` 下扩展专题 CSV",
        "contrib_step_3": "**提出新研究专题 / 方向：** 在 `proposals/` 目录下新增 Markdown 提案",
        "contrib_step_4": "**交叉核验新条目：** 对照会议官网或 arXiv 摘要核对元数据，确保标题、作者列表、会议与已收录条目保持一致",
        "contrib_step_5": "在仓库根目录执行 `python scripts/build_readme.py` 重新生成双语文档",
        "contrib_step_6": "提交 Pull Request",
        "contrib_dq_note": "在接收任何新的 2025 / 2026 会议条目前，数据质量（占位作者、未核实会议）为最高优先级。",
        "license_title": "## 📜 许可证",
        "license_body": "本项目以 [MIT License](LICENSE) 发布。",
        "footer_line1": "Made with ❤️ 献给机器人研究社区",
        "footer_line2": "数据来源：ICRA / IROS / RSS / CoRL 2024–2026 论文集 + arXiv 研究专题预印本",
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

VLA_TF_ENUM_YES = {"training_free", "frozen_model_controller_only"}

# ── Load data once (global; only verified + predicted are rendered) ─────────
rows_verified = _read_csv(CSV_VER)
rows_pending  = _read_csv(CSV_PEND)
rows_pred     = _read_csv(CSV_PRED)
rows_all      = _read_csv(CSV_MAIN)     # for pend/pred counters; NOT for stats
rows          = rows_verified           # **default: use verified only.**
vla_rows      = _read_csv(CSV_VLA) if os.path.exists(CSV_VLA) else []

# Verified venue buckets (2024 / 2025 real entries only)
data = defaultdict(lambda: defaultdict(list))
for r in rows_verified:
    data[r["Year"]][r["Venue"]].append(r)

# Predicted 2026 trend buckets -> kept strictly separate.
pred_data = defaultdict(lambda: defaultdict(list))
for r in rows_pred:
    pred_data[r["Year"]][r["Venue"]].append(r)

# Counts — PUBLIC counters read from rows_verified (n=78), never rows_all.
total         = len(rows_verified)
pending_total = len(rows_pending)
pred_total    = len(rows_pred)
code_found    = sum(1 for r in rows_verified if r["Code Link"] not in ("NA", "N/A", ""))

# Years: union of verified real years + 2026 trend section, still in desc order.
_real_years = sorted(data.keys(), reverse=True)
years_present = _real_years[:]
if "2026" not in years_present and rows_pred:
    years_present = ["2026"] + years_present  # 2026 first (reverse order)

# Internal DQ counters (diagnostic only; no longer rendered publicly).
dq_placeholder = sum(1 for r in rows_all if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in r.get("Notes",""))
dq_review      = sum(1 for r in rows_all if r.get("Notes","").startswith("DATA_QUALITY=REVIEW") or "DATA_QUALITY=REVIEW|" in r.get("Notes",""))
dq_total       = dq_placeholder + dq_review

# ── Natural, language-aware Gap short-form descriptions for the 6 key baselines
#    (replaces raw [:70] CSV slice that was cutting words in half on GitHub tables)
BASELINE_GAP_SHORT = {
    "en": {
        "VLA-IE-001": "Saves compute but discards it — BudgetLoop banks + reallocates; no grounded vs semantic TTL tiering",
        "VLA-IE-002": "Saves vision FLOPs but has no cross-step budget, no compute bank, no loop",
        "VLA-IE-003": "Fixed pruning/select/cache recipe — no difficulty-driven dynamic reallocation across steps",
        "VLA-IE-004": "Action-head only — no joint vision + CoT coordination; no unified budget controller",
        "VLA-IE-005": "Per-module scheduler with no compute bank b_t, no hard latency ceiling, no loop",
        "VLA-IE-011": "Blueprint for the K-loop — yet no VLA adaptation, no caching, no difficulty gating",
    },
    "zh-CN": {
        "VLA-IE-001": "省了计算就扔掉 — BudgetLoop 存进银行再分配；也无语义/grounded 两层 TTL",
        "VLA-IE-002": "省了视觉 FLOPs，但无跨步预算、无计算银行、无循环",
        "VLA-IE-003": "固定剪枝/选 token / 缓存配方；没有按难度跨步动态再分配",
        "VLA-IE-004": "只管动作头；视觉+CoT 不联动；无统一预算控制器",
        "VLA-IE-005": "有模块级调度但无 b_t 计算银行、无硬延迟上限、无循环",
        "VLA-IE-011": "K 循环蓝图；但未接入 VLA，不联合缓存，无难度门控",
    },
}

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
        badge("Verified", f"{total}", "brightgreen"),
        badge("Pending",  f"{pending_total}", "yellow"),
        badge("Predicted", f"{pred_total}", "informational"),
        badge("Code_Links", str(code_found), "blueviolet"),
        badge("License", "MIT", "yellow"),
    ]
    L.append(" ".join(venue_badges))
    L.append("")

    # 2. Acknowledgement
    L.append("---"); L.append("")
    L.append(T["ack_title"]); L.append("")
    for ln in T["ack_body"].splitlines(): L.append(ln)
    L.append("")

    # 4. TOC
    L.append("---"); L.append("")
    L.append(T["toc_title"]); L.append("")
    L.append(f"- {T['toc_overview']}")
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
    L.append("")

    # 6. Research Tracks
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
        enum_counter = Counter((r.get("training_requirement") or "unknown").strip() or "unknown" for r in vla_rows)
        def _e(c, keys): return sum(c.get(k,0) for k in keys)
        tf_yes     = _e(enum_counter, sorted(VLA_TF_ENUM_YES))
        tf_partial = 0
        tf_no      = _e(enum_counter, ["requires_finetuning", "requires_distillation", "trained_architecture"])
        tf_analysis = _e(enum_counter, ["analysis_only", "reference_backbone"])

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
                tid = r.get("Track ID","")
                gap = BASELINE_GAP_SHORT.get(lang, {}).get(tid)
                if not gap:
                    gap_raw = r.get("Gaps BudgetLoop Exploits") or "see CSV"
                    gap = gap_raw if len(gap_raw) <= 75 else (gap_raw[:72].rstrip() + "…")
                link = r.get("Paper Link") or ""
                title = r.get("Title","").split(":")[0].strip()
                speed = r.get("Reported Speedup") or "—"
                tfe = (r.get("training_requirement") or "unknown").strip() or "unknown"
                tf_display = r.get("Training-Free?", "—") or "—"
                if tfe in VLA_TF_ENUM_YES:
                    tf_md = T["vla_tf_yes"]
                elif tfe in {"requires_finetuning","requires_distillation","trained_architecture"}:
                    tf_md = T["vla_tf_no_"]
                else:
                    tf_md = T["vla_tf_other"](tf_display)
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
            # Commit-1 hard boundary: trend section reads strictly from
            # predicted_trends.csv, NEVER from rows_verified / rows_all.
            year_bucket = pred_data.get(year, {})
        else:
            L.append(T["year_title"].format(y=year)); L.append("")
            year_bucket = data.get(year, {})

        for venue in sorted(year_bucket.keys()):
            venue_rows = year_bucket[venue]
            anchor_id = venue.lower().replace(" ", "-").replace("(","").replace(")","")
            L.append(f'<a name="{anchor_id}-{year}"></a>'); L.append("")
            vc = {"ICRA": "0065BD", "IROS": "009E4D", "RSS": "E57200", "CoRL": "C00000"}.get(venue.split()[0], "555555")
            L.append(f"### ![{venue}](https://img.shields.io/badge/{venue.replace(' ','_')}-{year}-{vc}?style=flat-square)  {venue} {year}")
            L.append("")
            cnt_ln = T["venue_count_trend"](len(venue_rows)) if is_trend else T["venue_count_plain"](len(venue_rows))
            L.append(f"> {cnt_ln}")
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
                    authors = shorten_authors(authors).replace("|","\\|")
                    rt      = r["Robot Type"] if r["Robot Type"] not in ("NA","N/A","") else "⚙️ 其他/通用"
                    paper   = paper_link_md(r["Paper Link"], title)
                    code    = code_link_md(r["Code Link"])
                    L.append(f"| {i} | **{title}** | {authors} | {rt} | {paper} | {code} |")
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
