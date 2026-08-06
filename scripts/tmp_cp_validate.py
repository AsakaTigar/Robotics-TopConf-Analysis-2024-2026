import subprocess
import sys
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def run(cmd, shell=False, cwd=None):
    if cwd is None:
        cwd = BASE
    if shell:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, shell=True)
    else:
        p = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    return p.returncode, p.stdout, p.stderr

def main():
    cp_results = {}

    # ============ CP-1 ============
    print("=" * 60)
    print("CP-1: 3x apply_commit2_corrections.py, then git diff name-only empty")
    print("=" * 60)
    # Pre: stage current state so git diff compares index vs worktree (not HEAD vs worktree)
    rc_st, out_st, err_st = run(["git", "add", "research_tracks/vla_inference_efficiency_2024_2026.csv"])
    print(f"  [pre] git add vla_csv rc={rc_st}")
    script_path = os.path.join(BASE, "scripts", "apply_commit2_corrections.py")
    for i in range(3):
        rc, out, err = run([sys.executable, script_path])
        print(f"  run-{i+1}: rc={rc}")
        if out.strip():
            print(f"    stdout: {out.strip()[-200:]}")
        if rc != 0 and err.strip():
            print(f"    stderr: {err.strip()[-200:]}")

    # git diff --name-only (staged vs worktree, default)
    rc, out, err = run(["git", "diff", "--name-only", "--", "research_tracks/vla_inference_efficiency_2024_2026.csv"])
    out_strip = out.strip()
    print(f"  git diff --name-only stdout='{out_strip}' (expect empty)")
    if err.strip():
        print(f"  git diff stderr='{err.strip()}'")
    cp1_pass = (out_strip == "")
    cp_results["CP-1"] = (cp1_pass, f"3-runs no diff? diff_stdout='{out_strip[:80]}'")
    print(f"CP-1: {'PASS' if cp1_pass else 'FAIL'}")
    print()

    # ============ CP-2 ============
    print("=" * 60)
    print("CP-2: GATE1 reverse bad grep — Select-String vs findstr")
    print("=" * 60)

    pattern_gate1 = 'Generic LLM|\\bICL\\b|weight-sharing loops|same-FLOPs deep non-loop|1B loop|1B non-loop'
    ps_cmd = (
        "$p='research_tracks/vla_inference_efficiency_2024_2026.csv';"
        f"(Select-String -Path $p -Pattern '{pattern_gate1}').Count"
    )
    rc_a, out_a, err_a = run(["powershell", "-Command", ps_cmd])
    try:
        count_a = int(out_a.strip()) if out_a.strip() else -1
    except ValueError:
        count_a = -999
    print(f"  (a) PowerShell Select-String count = {count_a}")

    # findstr /R /C:...  CSV file, then find /C /V ""
    csv_rel = os.path.join("research_tracks", "vla_inference_efficiency_2024_2026.csv")
    findstr_cmd = (
        f'findstr /R /C:"Generic LLM" /C:"weight-sharing loops" '
        f'/C:"same-FLOPs deep non-loop" /C:"1B loop" /C:"1B non-loop" "{csv_rel}" | find /C /V ""'
    )
    # findstr \bICL\b case-insensitive — use /C:"ICL"
    # Windows findstr regex \b is not word-boundary; skip ICL word boundary for CP-2; main check is in GATE1
    rc_b, out_b, err_b = run(findstr_cmd, shell=True)
    try:
        count_b = int(out_b.strip()) if out_b.strip() else -1
    except ValueError:
        count_b = -999
    print(f"  (b) findstr + find count = {count_b}")

    cp2_pass = (count_a == 0) and (count_b == 0)
    cp_results["CP-2"] = (cp2_pass, f"Select-String={count_a} findstr={count_b} (expect both 0)")
    print(f"CP-2: {'PASS' if cp2_pass else 'FAIL'}")
    print()

    # ============ CP-3 ============
    print("=" * 60)
    print("CP-3: bilingual training-free top number EN == ZH")
    print("=" * 60)

    en_path = os.path.join(BASE, "README.md")
    zh_path = os.path.join(BASE, "README.zh-CN.md")
    en_txt = open(en_path, "r", encoding="utf-8").read()
    zh_txt = open(zh_path, "r", encoding="utf-8").read()

    # EN: match "**N training-free baselines" anywhere
    en_pat = re.compile(r'\*\*(\d+)\s+training-free\s+baselines')
    en_m = en_pat.search(en_txt)
    X = int(en_m.group(1)) if en_m else -1
    print(f"  (a) EN README training-free top_num X = {X}")
    # also gate4-style pattern for sanity
    en_m2 = re.findall(r'\*\*(\d+)\s+(?:training-free|免训练)\s+baselines', en_txt)
    print(f"  (a-alt) gate4 mixed pattern hits: {en_m2}")

    # ZH: "**N 条免训练 baseline**" (from line 74: 共 **6 条免训练 baseline**)
    zh_pats = [
        re.compile(r'\*\*(\d+)\s*条免训练\s*baselines?\s*\*\*'),
        re.compile(r'\*\*(\d+)\s+(?:training-free|免训练)\s+baselines'),
        re.compile(r'共\s*\*\*(\d+)\s*条免训练'),
    ]
    Y = -1
    for i, pat in enumerate(zh_pats):
        m = pat.search(zh_txt)
        if m:
            Y = int(m.group(1))
            print(f"  (b) ZH README matched via pat[{i}] → Y = {Y}")
            break
    if Y == -1:
        # brute: search all **N** in the VLA section then pick largest reasonable 1..20
        brute = re.findall(r'\*\*(\d{1,2})\*\*', zh_txt[10000:20000])
        print(f"  (b) brute candidate numbers in mid section: {brute}")
        for v in brute:
            vi = int(v)
            if 1 <= vi <= 20:
                Y = vi
                print(f"  (b) fallback pick Y = {Y}")
                break

    cp3_pass = (X != -1) and (Y != -1) and (X == Y)
    cp_results["CP-3"] = (cp3_pass, f"EN top={X} ZH top={Y} (expect equal)")
    print(f"CP-3: {'PASS' if cp3_pass else 'FAIL'}")
    print()

    # ============ Summary ============
    print("=" * 60)
    print("CROSS-VALIDATION CP SUMMARY")
    print("=" * 60)
    all_cp_pass = True
    for name, (ok, detail) in cp_results.items():
        print(f"  {name}: {'PASS' if ok else 'FAIL'} — {detail}")
        if not ok:
            all_cp_pass = False
    print(f"OVERALL CP: {'ALL PASS' if all_cp_pass else 'FAIL DETECTED'}")
    sys.exit(0 if all_cp_pass else 1)

if __name__ == "__main__":
    main()
