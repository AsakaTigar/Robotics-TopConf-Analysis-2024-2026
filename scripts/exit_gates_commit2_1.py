import subprocess
import sys
import os
import re
import csv
import io
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(_HERE) if os.path.basename(_HERE) == "scripts" else _HERE

VLA_CSV = os.path.join(BASE, "research_tracks", "vla_inference_efficiency_2024_2026.csv")
VERIFY_LOG = os.path.join(BASE, "docs", "data_verification_log_2026_08.md")


def _run_ps(cmd: str) -> tuple[int, str, str]:
    full = ["powershell", "-Command", cmd]
    p = subprocess.run(full, capture_output=True, text=True, cwd=BASE)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def _run_py(script: str) -> tuple[int, str, str]:
    p = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, cwd=BASE,
    )
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def _find_row(track_id: str) -> dict:
    with open(VLA_CSV, "r", encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r.get("Track ID") == track_id:
                return r
    return {}


def gate1_ie014_semantic() -> tuple[bool, list[str]]:
    detail: list[str] = []

    cmd_a = (
        "$p='research_tracks/vla_inference_efficiency_2024_2026.csv';"
        "(Select-String -Path $p -Pattern "
        "'Generic LLM|\\bICL\\b|weight-sharing loops|same-FLOPs deep non-loop|1B loop|1B non-loop').Count"
    )
    rc_a, out_a, err_a = _run_ps(cmd_a)
    try:
        count_reverse = int(out_a) if out_a else 0
    except ValueError:
        count_reverse = -1
    detail.append(f"GATE1 CmdA reverse count={count_reverse} (expect=0)")
    if err_a:
        detail.append(f"  CmdA stderr: {err_a[:120]}")

    row = _find_row("VLA-IE-014")
    fwd = []
    dataset_cell = (
        (row.get("Evaluated On / Dataset") or "")
        + " " + (row.get("Reported Speedup") or "")
        + " " + (row.get("Primary Metric") or "")
    )
    f1 = "LIBERO-90" in dataset_cell
    fwd.append(f1)

    method_cell = (
        (row.get("Method Category") or "")
        + " " + (row.get("Training-Free?") or "")
        + " " + (row.get("Key Mechanism") or "")
        + " " + (row.get("Notes") or "")
    )
    f2 = bool(re.search(r"train-time|training supervision", method_cell, re.IGNORECASE))
    fwd.append(f2)

    speedup = row.get("Reported Speedup") or ""
    f3 = bool(re.search(r"3x|3×|3 inference speedup", speedup, re.IGNORECASE))
    fwd.append(f3)

    vla_target = row.get("VLA Target") or ""
    f4 = "Generic LLM" not in vla_target
    fwd.append(f4)

    fwd_pass = sum(1 for x in fwd if x)
    detail.append(
        f"GATE1 CmdB forward assertions: LIBERO-90={f1} train-time_supervision={f2} "
        f"3x-speedup={f3} not-Generic-LLM={f4} → {fwd_pass}/4"
    )
    if fwd_pass >= 3 and fwd_pass < 4:
        detail.append("  3/4 forward OK (caveat)")

    reverse_ok = count_reverse == 0
    forward_ok = fwd_pass >= 3
    passed = reverse_ok and forward_ok
    if not passed:
        detail.append(f"  FAIL: reverse_ok={reverse_ok} forward_ok={forward_ok}")
    return passed, detail


def gate2_ie015_semantic() -> tuple[bool, list[str]]:
    detail: list[str] = []
    cmd_a = (
        "(Select-String -Path research_tracks/vla_inference_efficiency_2024_2026.csv "
        "-Pattern "
        "'Generic Transformer|theoretical classification|sample complexity|theory unification|"
        "Unifies recurrent weight-sharing|Background reference for loop section').Count"
    )
    rc_a, out_a, err_a = _run_ps(cmd_a)
    try:
        count_reverse = int(out_a) if out_a else 0
    except ValueError:
        count_reverse = -1
    detail.append(f"GATE2 CmdA reverse count={count_reverse} (expect=0)")
    if err_a:
        detail.append(f"  CmdA stderr: {err_a[:120]}")

    row = _find_row("VLA-IE-015")
    mc_km_rel_notes = (
        (row.get("Method Category") or "")
        + " " + (row.get("Key Mechanism") or "")
        + " " + (row.get("Relevance to BudgetLoop-VLA") or "")
        + " " + (row.get("Notes") or "")
    )
    g1 = bool(re.search(r"latent planning|teacher distillation", mc_km_rel_notes, re.IGNORECASE))

    speedup = row.get("Reported Speedup") or ""
    g2 = bool(re.search(r"89\.3.*(latency|reduction|%)", speedup)) or ("89.3" in speedup)

    training_req = row.get("training_requirement") or ""
    g3 = training_req == "requires_distillation"

    tf_raw = row.get("Training-Free?") or ""
    tf_head = tf_raw.strip()[:3].lower()
    g4 = tf_head != "yes"

    detail.append(
        f"GATE2 CmdB forward: latent_plan_or_distill={g1} 89.3-speedup={g2} "
        f"training_req=requires_distillation?={g3} Training-Free?-not-start-with-YES={g4}"
    )
    detail.append(
        f"  (training_requirement raw='{training_req}' Training-Free? raw='{tf_raw}' head3='{tf_head}')"
    )

    reverse_ok = count_reverse == 0
    forward_ok = g1 and g2 and g3 and g4
    passed = reverse_ok and forward_ok
    if not passed:
        detail.append(f"  FAIL: reverse_ok={reverse_ok} all4forward={forward_ok}")
    return passed, detail


def gate3_pending016017() -> tuple[bool, list[str]]:
    detail: list[str] = []
    cmd_a = (
        "(Select-String -Path README.md,README.zh-CN.md "
        "-Pattern 'VLA-IE-016|VLA-IE-017').Count"
    )
    rc_a, out_a, err_a = _run_ps(cmd_a)
    try:
        count_readme = int(out_a) if out_a else 0
    except ValueError:
        count_readme = -1
    detail.append(f"GATE3 CmdA README mentions 016/017 count={count_readme} (expect=0)")

    row16 = _find_row("VLA-IE-016")
    row17 = _find_row("VLA-IE-017")
    notes16 = row16.get("Notes") or ""
    notes17 = row17.get("Notes") or ""
    authors16 = (row16.get("Authors") or "").strip()
    authors17 = (row17.get("Authors") or "").strip()

    p16 = "VERIFICATION_STATUS=PENDING" in notes16
    p17 = "VERIFICATION_STATUS=PENDING" in notes17
    aw16 = authors16 == ""
    aw17 = authors17 == ""

    detail.append(
        f"GATE3 CmdB CSV: 016pending={p16} 017pending={p17} "
        f"016authors_wiped={aw16}('{authors16[:30]}') "
        f"017authors_wiped={aw17}('{authors17[:30]}')"
    )

    passed = (count_readme == 0) and p16 and p17 and aw16 and aw17
    if not passed:
        detail.append(f"  FAIL readme_mentions={count_readme} pending_ok={p16 and p17} authors_wiped={aw16 and aw17}")
    return passed, detail


def gate4_tf_enum() -> tuple[bool, list[str]]:
    detail: list[str] = []
    snippet = (
        "import re,pathlib;"
        "rd=pathlib.Path('README.md').read_text(encoding='utf-8');"
        "tm=re.findall(r'\\*\\*(\\d+)\\s+(?:training-free|免训练)\\s+baselines',rd);"
        "top=int(tm[0])if tm else -1;"
        "yes=rd.count('✅ YES')+rd.count('✅ 是');"
        "print('TOP=',top);print('YES=',yes);"
        "raise SystemExit(0 if top==yes and yes>=1 else 1)"
    )
    rc, out, err = _run_py(snippet)
    detail.append(f"GATE4 README top-check rc={rc} stdout='{out}'")
    if err:
        detail.append(f"  stderr: {err[:160]}")

    build_py_path = os.path.join(BASE, "scripts", "build_readme.py")
    try:
        with open(build_py_path, "r", encoding="utf-8") as f:
            txt = f.read()
    except OSError as e:
        txt = ""
        detail.append(f"  cannot read build_readme.py: {e}")

    brittle_counter = txt.count('Counter(r.get("Training-Free?"')
    startswith_na = txt.count('startswith("N/A")')
    detail.append(
        f"GATE4 build_readme brittle strings: Counter grep count={brittle_counter} "
        f"startswith('N/A') count={startswith_na}"
    )

    passed = (rc == 0) and (brittle_counter == 0) and (startswith_na == 0)
    if not passed:
        detail.append(
            f"  FAIL topcheck_rc0={rc==0} counter0={brittle_counter==0} "
            f"startswith0={startswith_na==0}"
        )
    return passed, detail


def gate5_notes_idempotent() -> tuple[bool, list[str]]:
    detail: list[str] = []
    script_path = os.path.join(BASE, "scripts", "apply_commit2_corrections.py")
    p = subprocess.run(
        [sys.executable, script_path, "--self-test-idempotent"],
        capture_output=True, text=True, cwd=BASE,
    )
    detail.append(f"GATE5 idempotent-check rc={p.returncode}")
    if p.stdout:
        lines = p.stdout.strip().splitlines()
        for ln in lines[-4:]:
            detail.append("  " + ln[:160])
    if p.stderr:
        detail.append(f"  stderr tail: {p.stderr.strip()[-160:]}")

    snippet2 = (
        "import csv,re,sys;"
        "rows=list(csv.DictReader(open('research_tracks/vla_inference_efficiency_2024_2026.csv',encoding='utf-8-sig')));"
        "c=[len(re.findall(r'CANONICAL_TITLE_VERIFIED',r.get('Notes')or ''))for r in rows];"
        "print('MAX=',max(c) if c else 0);"
        "print('VIOL=',sum(1 for x in c if x>1));"
        "sys.exit(0 if (max(c)if c else 0)<=1 and sum(1 for x in c if x>1)==0 else 9)"
    )
    rc2, out2, err2 = _run_py(snippet2)
    detail.append(f"GATE5 CTV≤1 check rc={rc2} stdout='{out2}'")
    if err2:
        detail.append(f"  CTV stderr: {err2[:160]}")

    passed = (p.returncode == 0) and (rc2 == 0)
    if not passed:
        detail.append(f"  FAIL idempotent_rc0={p.returncode==0} ctv_rc0={rc2==0}")
    return passed, detail


def gate6_git_cleanup() -> tuple[bool, list[str]]:
    detail: list[str] = []
    p1 = subprocess.run(
        ["git", "ls-files", ".arXiv_tmp_commit2.csv"],
        capture_output=True, text=True, cwd=BASE,
    )
    stdout1 = (p1.stdout or "").strip()
    detail.append(f"GATE6 git ls-files .arXiv_tmp_commit2.csv → '{stdout1}' (expect empty)")

    gi_path = os.path.join(BASE, ".gitignore")
    try:
        with open(gi_path, "r", encoding="utf-8") as f:
            gi_txt = f.read()
    except OSError as e:
        gi_txt = ""
        detail.append(f"  cannot read .gitignore: {e}")

    patterns = [".arXiv_tmp*", "*.tmp.csv", "__pycache__/", "*.pyc"]
    pat_ok = {}
    for pat in patterns:
        # treat *.tmp.csv and *.pyc as glob-matches (any line contains the pattern with escaping)
        # simple contains-match for each
        count = 0
        for line in gi_txt.splitlines():
            line_strip = line.strip()
            if not line_strip or line_strip.startswith("#"):
                continue
            if pat == "*.tmp.csv":
                if re.search(r"\*\.tmp\.csv", line_strip) or line_strip.endswith(".tmp.csv"):
                    count += 1
            elif pat == "*.pyc":
                if re.search(r"\*\.pyc", line_strip) or line_strip.endswith(".pyc"):
                    count += 1
            elif pat == ".arXiv_tmp*":
                if re.search(r"\.arXiv_tmp\*", line_strip) or ".arXiv_tmp" in line_strip:
                    count += 1
            elif pat == "__pycache__/":
                if line_strip.startswith("__pycache__") or "__pycache__" in line_strip:
                    count += 1
        pat_ok[pat] = count >= 1
        detail.append(f"  pattern '{pat}' present_count={count}")

    ls_ok = stdout1 == ""
    all_pat = all(pat_ok.values())
    passed = ls_ok and all_pat
    if not passed:
        detail.append(f"  FAIL ls_empty={ls_ok} all4patterns={all_pat} ({pat_ok})")
    return passed, detail


def gate7_count_invariance() -> tuple[bool, list[str]]:
    detail: list[str] = []
    cmd_counts = (
        "$v=(Import-Csv datasets/verified_papers.csv).Count;"
        "$p=(Import-Csv datasets/pending_verification.csv).Count;"
        "$pr=(Import-Csv datasets/predicted_trends.csv).Count;"
        "$s=$v+$p+$pr;"
        "Write-Host \"VERIFIED=$v PENDING=$p PREDICTED=$pr SUM=$s\""
    )
    rc, out, err = _run_ps(cmd_counts)
    detail.append(f"GATE7 partition counts rc={rc} stdout='{out}'")
    if err:
        detail.append(f"  stderr: {err[:160]}")

    exp_v, exp_p, exp_pr, exp_sum = 78, 22, 20, 120
    counts_ok = False
    m = re.search(r"VERIFIED=(\d+) PENDING=(\d+) PREDICTED=(\d+) SUM=(\d+)", out)
    if m:
        v, p, pr, s = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
        counts_ok = (v == exp_v) and (p == exp_p) and (pr == exp_pr) and (s == exp_sum)
        detail.append(
            f"  parsed: v={v}(expect {exp_v}) p={p}(expect {exp_p}) "
            f"pr={pr}(expect {exp_pr}) s={s}(expect {exp_sum}) → {'OK' if counts_ok else 'MISMATCH'}"
        )
    else:
        detail.append("  FAIL: could not parse partition counts output")

    build_script = os.path.join(BASE, "scripts", "build_readme.py")
    p2 = subprocess.run(
        [sys.executable, build_script],
        capture_output=True, text=True, cwd=BASE,
    )
    detail.append(f"GATE7 build_readme.py rc={p2.returncode}")
    if p2.stdout:
        last = p2.stdout.strip().splitlines()[-1:]
        if last:
            detail.append(f"  build stdout tail: {last[0][:120]}")
    if p2.stderr:
        detail.append(f"  build stderr: {p2.stderr.strip()[-160:]}")

    build_ok = p2.returncode == 0
    passed = counts_ok and build_ok
    if not passed:
        detail.append(f"  FAIL counts_ok={counts_ok} build_ok={build_ok}")
    return passed, detail


GATE_MAP = {
    "IE014": ("GATE1", "IE014 semantic", gate1_ie014_semantic),
    "IE015": ("GATE2", "IE015 semantic", gate2_ie015_semantic),
    "PENDING016017": ("GATE3", "016/017 pending isolation", gate3_pending016017),
    "TF_ENUM": ("GATE4", "TF enum TOP==TABLE dedupe", gate4_tf_enum),
    "NOTES_IDEMPOTENT": ("GATE5", "Notes idempotent CTV≤1", gate5_notes_idempotent),
    "GIT_CLEANUP": ("GATE6", "git cleanup ignore", gate6_git_cleanup),
    "COUNT_INVARIANCE": ("GATE7", "partitions + build success", gate7_count_invariance),
}

GATE_ORDER = ["IE014", "IE015", "PENDING016017", "TF_ENUM", "NOTES_IDEMPOTENT", "GIT_CLEANUP", "COUNT_INVARIANCE"]


def _parse_args() -> list[str]:
    if len(sys.argv) >= 2 and sys.argv[1].startswith("--gate="):
        v = sys.argv[1].split("=", 1)[1].strip().upper()
        if v == "ALL":
            return list(GATE_ORDER)
        if v in GATE_MAP:
            return [v]
        print(f"UNKNOWN gate {v}, use one of {list(GATE_MAP.keys())} or ALL", file=sys.stderr)
        sys.exit(2)
    return list(GATE_ORDER)


def main() -> int:
    run_order = _parse_args()
    full_out_buf = io.StringIO()

    def emit(s: str = ""):
        print(s)
        full_out_buf.write(s + "\n")

    results: dict[str, tuple[bool, list[str]]] = {}
    for key in GATE_ORDER:
        if key not in run_order:
            continue
        tag, label, fn = GATE_MAP[key]
        ok, det = fn()
        results[key] = (ok, det)
        emit(f"{tag}=[{'PASS' if ok else 'FAIL'}]")

    emit()
    emit("================= COMMIT 2.1 EXIT-GATES SUMMARY =================")
    all_pass = True
    pass_count = 0
    for key in GATE_ORDER:
        if key not in results:
            continue
        tag, label, _ = GATE_MAP[key]
        ok, det = results[key]
        if ok:
            pass_count += 1
        else:
            all_pass = False
        first_line = det[0] if det else "(no detail)"
        collapsed = first_line[:160]
        emit(f"{tag} ({label:29s}): {'PASS' if ok else 'FAIL'} — {collapsed}")

    fail_count = len(results) - pass_count
    if all_pass and fail_count == 0:
        emit(f"OVERALL: {pass_count}/{len(results)} GREEN")
    else:
        emit(f"OVERALL: FAIL count {fail_count} ({pass_count}/{len(results)} GREEN)")
    emit()

    full_stdout_text = full_out_buf.getvalue()

    if all_pass and len(results) == 7:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        append_sec = (
            f"\n## Commit 2.1 Hotfix Gates Stdout ({ts})\n"
            f"<pre>\n{full_stdout_text}</pre>\n"
        )
        try:
            with open(VERIFY_LOG, "a", encoding="utf-8") as f:
                f.write(append_sec)
            emit(f"[log-append] Appended exit_gates stdout to {VERIFY_LOG} (tail section)")
        except OSError as e:
            emit(f"[log-append] FAIL: could not write verification log: {e}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
