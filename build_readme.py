"""Generate README.md from the main CSV + research tracks.

Extended 2026-08-06: adds
  - Data quality banner + audit link
  - Research Tracks section (VLA inference efficiency)
  - ⚠️ DATA_QUALITY row markers on placeholder-author entries
"""
import csv, os, textwrap
from collections import defaultdict, Counter

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_MAIN = os.path.join(BASE, "robotics_papers_2024_2026_analysis.csv")
CSV_VLA  = os.path.join(BASE, "research_tracks", "vla_inference_efficiency_2024_2026.csv")
OUT      = os.path.join(BASE, "README.md")

# ── Load main CSV ──────────────────────────────────────────────────────────
rows = list(csv.DictReader(open(CSV_MAIN, encoding="utf-8-sig")))

# ── Load VLA research track CSV ────────────────────────────────────────────
vla_rows = []
if os.path.exists(CSV_VLA):
    vla_rows = list(csv.DictReader(open(CSV_VLA, encoding="utf-8-sig")))

# Group main rows: year → venue → [rows]
data = defaultdict(lambda: defaultdict(list))
for r in rows:
    data[r["Year"]][r["Venue"]].append(r)

# Stats
total = len(rows)
code_found = sum(1 for r in rows if r["Code Link"] not in ("NA", "N/A", ""))
years_present = sorted(data.keys())

# Data quality stats
dq_placeholder = sum(1 for r in rows if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in r.get("Notes",""))
dq_review      = sum(1 for r in rows if r.get("Notes","").startswith("DATA_QUALITY=REVIEW"))
dq_total       = dq_placeholder + dq_review

# ── Helpers ─────────────────────────────────────────────────────────────────
def badge(label, msg, color):
    label_ = label.replace("-", "--").replace(" ", "_")
    msg_   = msg.replace("-", "--").replace(" ", "_")
    return f"![{label}](https://img.shields.io/badge/{label_}-{msg_}-{color})"

def paper_link_md(link, title):
    if link and link not in ("NA","N/A",""):
        return f"[📄 Paper]({link})"
    return "📄 N/A"

def code_link_md(link):
    if link and link not in ("NA","N/A",""):
        return f"[💻 Code]({link})"
    return "—"

def dq_badge(notes):
    if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in notes:
        return " ⚠️ "
    if "DATA_QUALITY=REVIEW" in notes:
        return " 🟡 "
    return ""

def robot_emoji(rt):
    mapping = {
        "UAV/无人机": "🚁",
        "四足机器人": "🐾",
        "人形/双足": "🤖",
        "轮型机器人": "🛞",
        "机械臂/灵巧手": "🦾",
        "自动驾驶车辆": "🚗",
        "水下机器人": "🌊",
        "手术/医疗机器人": "🏥",
        "软体机器人": "🪸",
        "多机器人/集群": "🐝",
    }
    for k, v in mapping.items():
        if k in rt:
            return v + " " + rt
    return rt

def shorten_authors(authors):
    parts = [a.strip() for a in authors.split(";")]
    if len(parts) > 3:
        return "; ".join(parts[:3]) + f" *et al.* (+{len(parts)-3})"
    return authors

# ── Build README ────────────────────────────────────────────────────────────
lines = []

# Header
lines.append("# 🤖 Robotics Top Conference Papers — 2024-2026")
lines.append("")
lines.append("A curated collection of robotics papers from the four premier conferences:")
lines.append("**ICRA**, **IROS**, **RSS**, and **CoRL** — spanning 2024, 2025, and 2026 trends.")
lines.append("")
# Badges
venue_badges = [
    badge("ICRA", "2024--2025", "blue"),
    badge("IROS", "2024--2025", "green"),
    badge("RSS",  "2024", "orange"),
    badge("CoRL", "2024", "red"),
    badge("Papers", str(total), "lightgrey"),
    badge("Code_Links", str(code_found), "brightgreen"),
]
if dq_placeholder:
    venue_badges.append(badge("Placeholder_Papers", str(dq_placeholder), "critical"))
if dq_review:
    venue_badges.append(badge("Review_Flagged", str(dq_review), "yellow"))
venue_badges.append(badge("License", "MIT", "yellow"))
lines.append(" ".join(venue_badges))
lines.append("")

# ⚠️ Data quality banner ──────────────────────────────────────────────────────
if dq_total > 0:
    lines.append("> ⚠️ **Data Quality Notice**")
    lines.append(f"> This dataset carries **{dq_total} flagged entries**: **{dq_placeholder} with placeholder authors** (John Doe / Zhang San patterns — injected before 2025 venues were indexed) and **{dq_review} flagged for review**. All are marked ⚠️/🟡 in paper tables and carry an `AUDIT_REF` in the CSV `Notes` column. **Full audit**: [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md).")
    lines.append("")

# Acknowledgement
lines.append("---")
lines.append("")
lines.append("## 🙏 Acknowledgement")
lines.append("")
lines.append("> This project is inspired by and references the excellent work:")
lines.append("> **[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)** by [@Songwxuan](https://github.com/Songwxuan).")
lines.append("> Their methodology for curating and organizing top-conference robotics / embodied AI papers provided")
lines.append("> the structural template for this repository. Many thanks! 🎉")
lines.append("")

# ── TOC ─────────────────────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## 📋 Table of Contents")
lines.append("")
lines.append("- [📊 Overview](#-overview)")
lines.append("- [⚠️ Data Quality Status](#️-data-quality-status)")
lines.append("- [🔬 Research Tracks](#-research-tracks)")
lines.append("  - [VLA Inference Efficiency (2024–2026)](#vla-inference-efficiency-20242026)")
lines.append("  - [BudgetLoop-VLA Proposal](#budgetloop-vla-proposal)")
lines.append("- [🏷️ Robot Type Legend](#️-robot-type-legend)")
for y in years_present:
    anchor = f"year-{y}"
    lines.append(f"- [📅 {y}](#{anchor})")
    for v in sorted(data[y].keys()):
        sub = v.lower().replace(" ", "-").replace("(", "").replace(")", "")
        lines.append(f"  - [{v}](#{sub}-{y})")
lines.append("- [📈 Trends & Statistics](#-trends--statistics)")
lines.append("- [🤝 Contributing](#-contributing)")
lines.append("")

# ── Overview ────────────────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## 📊 Overview")
lines.append("")
lines.append("| Metric | Count |")
lines.append("|--------|-------|")
lines.append(f"| Total Papers / Trend Entries | **{total}** |")
for y in years_present:
    cnt = sum(len(v) for v in data[y].values())
    lines.append(f"| {y} entries | {cnt} |")
lines.append(f"| Venues covered | ICRA, IROS, RSS, CoRL |")
lines.append(f"| Research tracks | 1 (VLA inference efficiency, {len(vla_rows)} papers) |")
lines.append(f"| Open proposals | 1 (BudgetLoop-VLA) |")
lines.append(f"| Papers with code links | {code_found} |")
if dq_total:
    lines.append(f"| ⚠️ Data-quality flagged | {dq_total} ({dq_placeholder} placeholder authors, {dq_review} review) |")
lines.append("")

# ── Data Quality Section ────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## ⚠️ Data Quality Status")
lines.append("")
lines.append("| Severity | Tag | Count | Resolution |")
lines.append("|---|---|---|---|")
if dq_placeholder:
    lines.append(f"| 🔴 HIGH | `DATA_QUALITY=PLACEHOLDER_AUTHORS` | **{dq_placeholder}** | Marked in CSV `Notes`; carrying `AUDIT_REF`; to be cross-replaced once 2025 proceedings publish. |")
if dq_review:
    lines.append(f"| 🟡 MEDIUM | `DATA_QUALITY=REVIEW` | **{dq_review}** | Type-classification or authorship-truncation review; not suppressed. |")
lines.append(f"| ✅ CLEAN | (unflagged) | **{total-dq_total}** | Treated as ground truth for stats / tables. |")
lines.append("")
lines.append("Full itemized list with rationale, cross-references to SRL Workshop real-author counterparts, and remediation plan:")
lines.append("")
lines.append("→ **[`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md)**")
lines.append("")
lines.append("Affected rows in paper tables carry a ⚠️ prefix. Do not cite the 🔴 placeholder-author entries in academic writing before verification.")
lines.append("")

# ── Research Tracks Section ─────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append('<a name="research-tracks"></a>')
lines.append("")
lines.append("## 🔬 Research Tracks")
lines.append("")
lines.append("Dedicated deep-dives on fast-moving topics **outside** the ICRA/IROS/RSS/CoRL four-venue main CSV — including arXiv preprints, non-robotics venues (NeurIPS/ICML), and pure Transformer architecture work that informs robotics methods.")
lines.append("")

# === VLA Inference Efficiency track ===
lines.append('<a name="vla-inference-efficiency-20242026"></a>')
lines.append("")
lines.append("### 🚀 VLA Inference Efficiency — Training-Free Acceleration (2024–2026)")
lines.append("")
lines.append(f"Curated **{len(vla_rows)} papers** spanning 6 method categories. Source file:")
lines.append("")
lines.append("→ **[`research_tracks/vla_inference_efficiency_2024_2026.csv`](research_tracks/vla_inference_efficiency_2024_2026.csv)**")
lines.append("")

if vla_rows:
    # Category distribution
    cat_counter = Counter(r["Method Category"] for r in vla_rows if r.get("Method Category"))
    tf_counter  = Counter(r.get("Training-Free?","UNKNOWN") for r in vla_rows)
    tf_yes = tf_counter.get("YES (no training)",0)+tf_counter.get("YES",0)+tf_counter.get("YES — fully frozen",0)
    tf_partial = tf_counter.get("PARTIAL",0)
    tf_no = tf_counter.get("NO",0)+tf_counter.get("NO (light router trained end-to-end)",0)+tf_counter.get("NO — TBPTT trains recurrent action head",0)+tf_counter.get("NO (architecture trained from scratch with loop)",0)
    tf_analysis = sum(v for k,v in tf_counter.items() if k.startswith("N/A")) + tf_counter.get("N/A (analysis paper)",0)

    lines.append("| Dimension | Breakdown |")
    lines.append("|---|---|")
    lines.append(f"| Training-free compatible | {tf_yes} directly usable + {tf_partial} partial = **{tf_yes+tf_partial} training-free baseline pool** |")
    lines.append(f"| Trained (strict upper bounds only) | {tf_no} (used for ceiling ablations not strict comparison) |")
    lines.append(f"| Analysis / theory papers | {tf_analysis} |")
    lines.append(f"| Method categories | " + " · ".join(f"**{c}** ×{n}" for c,n in cat_counter.most_common(7)) + " |")
    lines.append("")

    # Top-competitor mini-table (the 6 most relevant baselines)
    top_ids = {"VLA-IE-001","VLA-IE-002","VLA-IE-003","VLA-IE-004","VLA-IE-005","VLA-IE-011"}
    top_rows = [r for r in vla_rows if r.get("Track ID") in top_ids]
    if top_rows:
        lines.append("**Key baselines referenced by the BudgetLoop proposal:**")
        lines.append("")
        lines.append("| # | Work | Category | Training-Free? | Reported speedup | Gap BudgetLoop fills |")
        lines.append("|---|---|---|---|---|---|")
        for i, r in enumerate(sorted(top_rows, key=lambda x: x["Track ID"]), 1):
            gap = (r.get("Gaps BudgetLoop Exploits") or "see CSV")[:70]
            link = r.get("Paper Link") or ""
            title = r.get("Title","").split(":")[0].strip()
            speed = r.get("Reported Speedup") or "—"
            tf = r.get("Training-Free?","—")
            if "YES" in tf: tf = "✅ YES"
            elif "NO" in tf: tf = "❌ NO"
            else: tf = "🟡 " + tf
            cat = r.get("Method Category","—")
            md_title = f"**{title}**"
            if link and link not in ("NA","N/A",""): md_title = f"[{md_title}]({link})"
            lines.append(f"| {i} | {md_title} | {cat} | {tf} | {speed} | {gap} |")
        lines.append("")

# === BudgetLoop-VLA proposal ===
lines.append('<a name="budgetloop-vla-proposal"></a>')
lines.append("")
lines.append("### 🧭 BudgetLoop-VLA — Locked Research Direction")
lines.append("")
lines.append("Full proposal with 3 modes, Cache-to-Think bank, P0–P3 gates, and claim map:")
lines.append("")
lines.append("→ **[`proposals/BUDGETLOOP_VLA.md`](proposals/BUDGETLOOP_VLA.md)**")
lines.append("")
lines.append("**One-line framing.** Under a fixed per-step average compute budget on a **single frozen 1B-parameter reasoning VLA**, deposit surplus compute from easy control steps into a sliding-window compute bank; re-deposit it into genuinely difficult steps (contact / target-switch / failure-recovery) by enabling a training-free K=2 damped loop + grounded CoT selective refresh. This is a **compute allocator**, not just an accelerator.")
lines.append("")
lines.append("**Three modes:**")
lines.append("")
lines.append("| Mode | Scenario | Reused | Refreshed | Loop depth |")
lines.append("|---|---|---|---|---|")
lines.append("| **Reflex** | Free-space motion, stable scene, actions consistent | goal/subtask/plan, static visual KV, ActionCache | Gripper sanity only | K=1 |")
lines.append("| **Refresh** | Occlusion, pre-grasp micro-adjust, grounding change | goal/subtask/plan + static background | move / gripper / objects / grounded-CoT + task-relevant visual tokens | K=1 |")
lines.append("| **Deliberate** | Contact, target switch, action inconsistency, failure recovery | goal only | Full vision + full CoT | K∈{2,3} damped mid-stack, token-selective |")
lines.append("")
lines.append("**Core bank:**")
lines.append("")
lines.append("$$")
lines.append("b_t = \\mathrm{clip}\\bigl(b_{t-1} + B - c_t,\\ \\ b_{\\min},\\ \\ b_{\\max}\\bigr)")
lines.append("$$")
lines.append("")
lines.append("with B = per-step budget, c_t = actual compute consumed. **Claims: (1) same avg latency → higher task success than cache-only baselines; (2) same success → both mean AND p95 latency lower.**")
lines.append("")
lines.append("**Go / No-Go gates before each stage:** Profiling → strong cache-only baseline → frozen loop → BudgetLoop integrated. See proposal for thresholds.")
lines.append("")

# ── Robot Type Legend ────────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## 🏷️ Robot Type Legend")
lines.append("")
legend_map = {
    "UAV/无人机": ("🚁", "Unmanned Aerial Vehicle / Drone"),
    "四足机器人": ("🐾", "Quadruped / Legged Robot"),
    "人形/双足": ("🤖", "Humanoid / Biped Robot"),
    "轮型机器人": ("🛞", "Wheeled / Mobile Robot"),
    "机械臂/灵巧手": ("🦾", "Robotic Arm / Dexterous Hand"),
    "自动驾驶车辆": ("🚗", "Autonomous Vehicle"),
    "水下机器人": ("🌊", "Underwater Robot"),
    "手术/医疗机器人": ("🏥", "Surgical / Medical Robot"),
    "软体机器人": ("🪸", "Soft Robot"),
    "多机器人/集群": ("🐝", "Swarm / Multi-Robot System"),
    "其他/通用": ("⚙️", "General / Other"),
}
lines.append("| Icon | Type (CN) | Description |")
lines.append("|------|-----------|-------------|")
for k, (icon, desc) in legend_map.items():
    lines.append(f"| {icon} | {k} | {desc} |")
lines.append("")

# ── Year sections ────────────────────────────────────────────────────────────
for year in years_present:
    is_trend = (year == "2026")
    lines.append("---")
    lines.append("")
    lines.append(f'<a name="year-{year}"></a>')
    lines.append("")
    if is_trend:
        lines.append(f"## 📅 {year} — Emerging Trends (Predicted)")
        lines.append("")
        lines.append("> ⚠️ **Note**: 2026 entries are **predicted trend topics**, not confirmed accepted papers.")
        lines.append("> They represent anticipated research directions based on current momentum.")
        lines.append("> Research-track extensions (e.g. VLA Inference Efficiency) live in the [🔬 Research Tracks](#-research-tracks) section above.")
    else:
        lines.append(f"## 📅 {year}")
    lines.append("")

    for venue in sorted(data[year].keys()):
        venue_rows = data[year][venue]
        anchor_id = venue.lower().replace(" ", "-").replace("(","").replace(")","")
        lines.append(f'<a name="{anchor_id}-{year}"></a>')
        lines.append("")
        venue_badge_color = {
            "ICRA": "0065BD", "IROS": "009E4D",
            "RSS": "E57200", "CoRL": "C00000",
        }.get(venue.split()[0], "555555")
        lines.append(f"### ![{venue}](https://img.shields.io/badge/{venue.replace(' ','_')}-{year}-{venue_badge_color}?style=flat-square)  {venue} {year}")
        lines.append("")
        lines.append(f"> {len(venue_rows)} {'trend topics' if is_trend else 'papers'}")
        ph_in_venue = sum(1 for r in venue_rows if "DATA_QUALITY=PLACEHOLDER_AUTHORS" in r.get("Notes",""))
        if ph_in_venue:
            lines.append(f"> ⚠️ **{ph_in_venue} entries carry placeholder authors — see [`data_quality/AUDIT_2024_2026.md`](data_quality/AUDIT_2024_2026.md).**")
        lines.append("")
        if is_trend:
            lines.append("| # | Topic | Robot Focus | Key Trend | Description |")
            lines.append("|---|-------|-------------|-----------|-------------|")
            for i, r in enumerate(venue_rows, 1):
                note = r.get("Notes", "")
                trend_kw = ""
                desc_kw  = ""
                if "Trend:" in note:
                    parts = note.split("|")
                    for p in parts:
                        p = p.strip()
                        if p.startswith("Trend:"):
                            trend_kw = p[6:].strip()[:80]
                        elif p.startswith("Desc:"):
                            desc_kw  = p[5:].strip()[:80]
                rt = r["Robot Type"] if r["Robot Type"] not in ("NA","N/A") else "—"
                title = r["Title"].replace("|","\\|")
                lines.append(f"| {i} | **{title}** | {rt} | {trend_kw} | {desc_kw} |")
        else:
            lines.append("| # | Title | Authors | Robot Type | Paper | Code |")
            lines.append("|---|-------|---------|------------|-------|------|")
            for i, r in enumerate(venue_rows, 1):
                title   = r["Title"].replace("|","\\|")
                authors = r["Authors"]
                notes   = r.get("Notes", "")
                is_ph   = "DATA_QUALITY=PLACEHOLDER_AUTHORS" in notes
                if is_ph:
                    authors = "_⚠️ Placeholder — see audit_"
                else:
                    authors = shorten_authors(authors)
                authors = authors.replace("|","\\|")
                rt      = r["Robot Type"] if r["Robot Type"] not in ("NA","N/A","") else "⚙️ Other"
                paper   = paper_link_md(r["Paper Link"], title)
                code    = code_link_md(r["Code Link"])
                bdg     = dq_badge(notes)
                lines.append(f"| {i} | {bdg}**{title}** | {authors} | {rt} | {paper} | {code} |")
        lines.append("")

# ── Trends & Statistics ─────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## 📈 Trends & Statistics")
lines.append("")
type_counter = Counter(r["Robot Type"] for r in rows if r["Robot Type"] not in ("NA","N/A",""))
lines.append("### Robot Type Distribution (2024-2025 papers)")
lines.append("")
lines.append("| Robot Type | Count | Share |")
lines.append("|------------|-------|-------|")
paper_rows_only = [r for r in rows if r["Year"] in ("2024","2025")]
tc2 = Counter(r["Robot Type"] for r in paper_rows_only if r["Robot Type"] not in ("NA","N/A",""))
total_typed = sum(tc2.values())
for t, c in tc2.most_common(10):
    pct = f"{100*c/total_typed:.0f}%"
    lines.append(f"| {t} | {c} | {pct} |")
lines.append("")
lines.append("### Papers per Venue")
lines.append("")
lines.append("| Year | CoRL | ICRA | IROS | RSS |")
lines.append("|------|------|------|------|-----|")
for y in ["2024","2025"]:
    corl = len(data[y].get("CoRL",[]))
    icra = len(data[y].get("ICRA",[])) + len(data[y].get("ICRA (SRL Workshop)",[]))
    iros = len(data[y].get("IROS",[]))
    rss  = len(data[y].get("RSS",[]))
    lines.append(f"| {y} | {corl or '—'} | {icra or '—'} | {iros or '—'} | {rss or '—'} |")
lines.append("")
lines.append("### 2026 Predicted Trend Keywords")
lines.append("")
trend_keywords = [
    "Human-Robot Interaction", "Autonomous Navigation", "Machine Learning in Robotics",
    "Healthcare Robotics", "Sustainable Automation", "Multi-Robot Systems",
    "Robotic Vision", "Field Robotics", "Soft Robotics", "Bio-inspired Robotics",
    "Aerial Robotics", "Legged & Bio-inspired Locomotion", "Manipulation & Grasping",
    "Search and Rescue", "Micro/Nano Robotics", "VLA Inference Efficiency",
    "BudgetLoop-VLA", "Cache-to-Think",
]
lines.append(" ".join(f"`{kw}`" for kw in trend_keywords))
lines.append("")

# ── Contributing ────────────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## 🤝 Contributing")
lines.append("")
lines.append("Contributions are welcome! If you find missing papers, wrong classifications,")
lines.append("or want to add code links:")
lines.append("")
lines.append("1. Fork this repository")
lines.append("2. Edit `robotics_papers_2024_2026_analysis.csv` (main venues) **or** extend CSVs inside `research_tracks/` for special topics")
lines.append("3. **Propose new research tracks or directions:** add a file under `proposals/`")
lines.append("4. **Flag data quality issues:** cross-check against the audit at `data_quality/AUDIT_2024_2026.md` and add new `AUDIT_REF` markers in CSV Notes")
lines.append("5. Run `python build_readme.py` to regenerate the README")
lines.append("6. Submit a Pull Request")
lines.append("")
lines.append("Data quality (placeholder authors, unverified venues) takes highest priority before any new 2025/2026 venue entries are accepted.")
lines.append("")

# ── License ──────────────────────────────────────────────────────────────────
lines.append("---")
lines.append("")
lines.append("## 📜 License")
lines.append("")
lines.append("This project is licensed under the [MIT License](LICENSE).")
lines.append("")
lines.append("---")
lines.append("")
lines.append('<p align="center">')
lines.append('  <i>Made with ❤️ for the robotics research community</i>\n')
lines.append('  <i>Data sourced from ICRA, IROS, RSS, CoRL proceedings (2024–2026) plus arXiv research-track preprints.</i>\n')
lines.append('  <i>Inspired by <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a></i>')
lines.append('</p>')
lines.append("")

readme = "\n".join(lines)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(readme)
print(f"README written: {OUT}")
print(f"Length: {len(readme):,} chars, {readme.count(chr(10))+1} lines")
print(f"Main CSV rows: {total}  |  VLA track rows: {len(vla_rows)}")
print(f"Placeholder authors flagged: {dq_placeholder}  |  Review items: {dq_review}")
