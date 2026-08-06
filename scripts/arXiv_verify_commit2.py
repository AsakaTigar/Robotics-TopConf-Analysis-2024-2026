"""Query arXiv API for the 11 IDs flagged in the auditor's commit-2 list.

Outputs CSV-formatted rows: arxiv_id | canonical_title | authors | first_300_chars_of_abstract
Usage:  python scripts/arXiv_verify_commit2.py
"""
import csv, io, sys, urllib.request, urllib.parse, xml.etree.ElementTree as ET

IDS = [
    "2506.07639",   # 1 Fast ECoT
    "2407.08693",   # 2 Real ECoT
    "2501.12148",   # 3 Wrong old ECoT link (comms paper!)
    "2505.08243",   # 4 VLA-IE-014 audit: ECoT-Lite
    "2601.09708",   # 5 VLA-IE-015 audit: Fast-ThinkAct
    "2606.03784",   # 6 ERVLA
    "2607.06370",   # 7 ActionCache
    "2502.02175",   # 8 VLA-Cache
    "2605.29438",   # 9 ElegantVLA
    "2602.07845",   # A RD-VLA
    "2506.10100",   # B EfficientVLA
    # ---- second batch for remaining check ----
    "2605.23872",   # C VLA-IE-011 Training-Free Looped Xfmr
    "2604.21254",   # D VLA-IE-010 Hyperloop
    "2605.16343",   # E VLA-IE-012 LoopQ
    "2507.10524",   # F VLA-IE-009 Mixture-of-Recursions
]

ATOM = "{http://www.w3.org/2005/Atom}"
url = "http://export.arxiv.org/api/query?id_list=" + ",".join(IDS) + f"&max_results={len(IDS)}"

print("Fetching arXiv metadata …", file=sys.stderr)
with urllib.request.urlopen(url, timeout=45) as resp:
    raw = resp.read().decode("utf-8", errors="replace")

root = ET.fromstring(raw)
rows = []
for e in root.findall(f"{ATOM}entry"):
    raw_id = e.findtext(f"{ATOM}id") or ""
    arxiv_id = raw_id.split("/abs/")[-1].split("v")[0]
    title = " ".join((e.findtext(f"{ATOM}title") or "").split())
    summary = " ".join((e.findtext(f"{ATOM}summary") or "").split())
    authors = "; ".join(a.findtext(f"{ATOM}name") or "" for a in e.findall(f"{ATOM}author"))
    rows.append((arxiv_id, title, authors, summary[:320]))

rows.sort(key=lambda r: r[0])

w = csv.writer(sys.stdout, lineterminator="\n")
w.writerow(["arxiv_id", "canonical_title", "authors", "abstract_head"])
w.writerows(rows)

print(f"\nRows returned: {len(rows)} / requested {len(IDS)}", file=sys.stderr)
