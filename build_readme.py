"""Generate README.md from the CSV data."""
import csv, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
CSV  = os.path.join(BASE, "robotics_papers_2024_2026_analysis.csv")
OUT  = os.path.join(BASE, "README.md")

rows = list(csv.DictReader(open(CSV, encoding="utf-8-sig")))

# Group: year → venue → [rows]
data = defaultdict(lambda: defaultdict(list))
for r in rows:
    data[r["Year"]][r["Venue"]].append(r)

# Stats
total = len(rows)
code_found = sum(1 for r in rows if r["Code Link"] not in ("NA", "N/A", ""))
years_present = sorted(data.keys())

# Robot type legend (unique types, excluding N/A)
all_types = sorted({r["Robot Type"] for r in rows if r["Robot Type"] not in ("NA","N/A","")})

# --------------------------------------------------------------------------
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

# --------------------------------------------------------------------------
lines = []

# Header
lines.append("# 🤖 Robotics Top Conference Papers — 2024-2026")
lines.append("")
lines.append("A curated collection of robotics papers from the four premier conferences:")
lines.append("**ICRA**, **IROS**, **RSS**, and **CoRL** — spanning 2024, 2025, and 2026 trends.")
lines.append("")

# Badges
lines.append(
    " ".join([
        badge("ICRA", "2024--2025", "blue"),
        badge("IROS", "2024--2025", "green"),
        badge("RSS",  "2024", "orange"),
        badge("CoRL", "2024", "red"),
        badge("Papers", str(total), "lightgrey"),
        badge("Code_Links", str(code_found), "brightgreen"),
        badge("License", "MIT", "yellow"),
    ])
)
lines.append("")

# Attribution / Acknowledgement
lines.append("---")
lines.append("")
lines.append("## 🙏 Acknowledgement")
lines.append("")
lines.append("> This project is inspired by and references the excellent work:")
lines.append("> **[Embodied-AI-Paper-TopConf](https://github.com/Songwxuan/Embodied-AI-Paper-TopConf)** by [@Songwxuan](https://github.com/Songwxuan).")
lines.append("> Their methodology for curating and organizing top-conference robotics / embodied AI papers provided")
lines.append("> the structural template for this repository. Many thanks! 🎉")
lines.append("")

# TOC
lines.append("---")
lines.append("")
lines.append("## 📋 Table of Contents")
lines.append("")
lines.append("- [📊 Overview](#-overview)")
lines.append("- [🏷️ Robot Type Legend](#️-robot-type-legend)")
for y in years_present:
    anchor = f"year-{y}"
    lines.append(f"- [📅 {y}](#{anchor})")
    for v in sorted(data[y].keys()):
        sub = v.lower().replace(" ", "-").replace("(", "").replace(")", "")
        lines.append(f"  - [{v}](#{sub}-{y})")
lines.append("- [📈 Trends \& Statistics](#-trends--statistics)")
lines.append("- [🤝 Contributing](#-contributing)")
lines.append("")

# Overview
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
lines.append(f"| Papers with code links | {code_found} |")
lines.append("")

# Robot Type Legend
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
        lines.append(f"> ⚠️ **Note**: 2026 entries are **predicted trend topics**, not confirmed accepted papers.")
        lines.append("> They represent anticipated research directions based on current momentum.")
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
        lines.append("")

        if is_trend:
            # Trend table: Topic, Robot Type, Trend Keywords, Description
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
            # Paper table
            lines.append("| # | Title | Authors | Robot Type | Paper | Code |")
            lines.append("|---|-------|---------|------------|-------|------|")
            for i, r in enumerate(venue_rows, 1):
                title   = r["Title"].replace("|","\\|")
                authors = r["Authors"].replace("|","\\|")
                # Shorten long author lists
                auth_parts = authors.split(";")
                if len(auth_parts) > 3:
                    authors = "; ".join(a.strip() for a in auth_parts[:3]) + f" *et al.* (+{len(auth_parts)-3})"
                rt      = r["Robot Type"] if r["Robot Type"] not in ("NA","N/A","") else "⚙️ Other"
                paper   = paper_link_md(r["Paper Link"], title)
                code    = code_link_md(r["Code Link"])
                lines.append(f"| {i} | **{title}** | {authors} | {rt} | {paper} | {code} |")

        lines.append("")

# Trends & Statistics
lines.append("---")
lines.append("")
lines.append("## 📈 Trends & Statistics")
lines.append("")

from collections import Counter
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
    "Search and Rescue", "Micro/Nano Robotics",
]
lines.append(" ".join(f"`{kw}`" for kw in trend_keywords))
lines.append("")

# Contributing
lines.append("---")
lines.append("")
lines.append("## 🤝 Contributing")
lines.append("")
lines.append("Contributions are welcome! If you find missing papers, wrong classifications,")
lines.append("or want to add code links:")
lines.append("")
lines.append("1. Fork this repository")
lines.append("2. Edit `robotics_papers_2024_2026_analysis.csv`")
lines.append("3. Run `python build_readme.py` to regenerate the README")
lines.append("4. Submit a Pull Request")
lines.append("")

# Footer
lines.append("---")
lines.append("")
lines.append("## 📜 License")
lines.append("")
lines.append("This project is licensed under the [MIT License](LICENSE).")
lines.append("")
lines.append("---")
lines.append("")
lines.append('<p align="center">')
lines.append('  <i>Made with ❤️ for the robotics research community</i><br>')
lines.append('  <i>Data sourced from ICRA, IROS, RSS, CoRL proceedings (2024-2026)</i><br>')
lines.append('  <i>Inspired by <a href="https://github.com/Songwxuan/Embodied-AI-Paper-TopConf">Embodied-AI-Paper-TopConf</a></i>')
lines.append('</p>')
lines.append("")

readme = "\n".join(lines)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(readme)

print(f"README written: {OUT}")
print(f"Length: {len(readme):,} chars, {readme.count(chr(10))+1} lines")
