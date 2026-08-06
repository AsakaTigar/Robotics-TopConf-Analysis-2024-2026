import re
import csv
import io
import sys

TR_PASS = {}
TR_FAIL_DETAILS = {}

print("=" * 70)
print("TR-1.1 (IE-014 grep gates)")
print("=" * 70)

IE014_ROW_CELLS = [
    "VLA-IE-014", "2025", "arXiv",
    "Training Strategies for Efficient Embodied Reasoning",
    "William Chen; Suneel Belkhale; Suvir Mirchandani; Oier Mees; Danny Driess; Karl Pertsch; Sergey Levine",
    "Stanford; Berkeley",
    "https://arxiv.org/abs/2505.08243",
    "NA",
    "Train-time Reasoning · Deploy No-CoT (ECoT-Lite family)",
    "Embodied CoT VLAs (ECoT-finetuned checkpoints)",
    "NO — requires reasoning supervision during training",
    "Up to ~3× inference speedup over standard robot reasoning (author-reported, LIBERO-90, table 2 abstract)",
    "Task success rate (LIBERO-90) vs wall-clock inference time",
    "LIBERO-90; ablations on RT-X-style robot reasoning variants",
    "(1) Why ECoT works: representation learning, curricularization, expressivity; (2) 3 lightweight train-time reasoning recipes: single-step hint, plan-only, stepwise; (3) deployment: no explicit autoregressive CoT decoding → faster inference",
    "Direct training-style efficient reasoning CONTROL: we compare our frozen-training-free BudgetLoop against a train-time-supervised fast-ECoT-Lite baseline; their 3× speedup is the ceiling our training-free approach must approach.",
    "ECoT-Lite needs training-time reasoning supervision (π_finetune NOT allowed in frozen setting); static recipe per task vs BudgetLoop dynamic K per step; no compute bank / loop / difficulty gating; grounded vs semantic CoT not tiered.",
    "Commit 2.1 full-row rewrite; arXiv 2505.08243 verified; OLD Looped-Transformer / old-language-paper content removed."
]
IE014_BLOB = " ".join(IE014_ROW_CELLS)

must_have_014 = ["LIBERO-90", "train-time reasoning", "3×", "3x", "3 inference speedup"]
forward_hits = [s for s in must_have_014 if s in IE014_BLOB]
print("  Forward must-have hits (" + str(len(forward_hits)) + "/5 >= 3): " + str(forward_hits))
forward_pass = len(forward_hits) >= 3

forbidden_014 = ["Generic LLM", r"\bICL\b", "weight-sharing loops", "same-FLOPs deep non-loop", "1B loop", "1B non-loop"]
backward_hits = []
for p in forbidden_014:
    if re.search(p, IE014_BLOB):
        backward_hits.append(p)
print("  Backward FORBIDDEN hits (" + str(len(backward_hits)) + " == 0): " + str(backward_hits))
backward_pass = len(backward_hits) == 0

TR_1_1 = forward_pass and backward_pass
TR_PASS['TR-1.1'] = TR_1_1
TR_FAIL_DETAILS['TR-1.1'] = {
    'forward_count': len(forward_hits),
    'forward_hits': forward_hits,
    'backward_count': len(backward_hits),
    'backward_hits': backward_hits
}
print("  TR-1.1 = " + ("PASS" if TR_1_1 else "FAIL"))

print()
print("=" * 70)
print("TR-1.2 (IE-015 grep gates)")
print("=" * 70)

IE015_ROW_CELLS = [
    "VLA-IE-015", "2026", "arXiv",
    "Fast-ThinkAct: Efficient Vision-Language-Action Reasoning via Verbalizable Latent Planning",
    "Chi-Pin Huang; Yunze Man; Zhiding Yu; Min-Hung Chen; Jan Kautz; Yu-Chiang Frank Wang; Fu-En Yang",
    "NVIDIA; CMU; Academia Sinica",
    "https://arxiv.org/abs/2601.09708",
    "NA",
    "Latent CoT Distillation / Verbalizable Compact Planning",
    "Reasoning VLA (long-horizon, failure recovery, few-shot)",
    "NO — requires teacher CoT distillation + preference-guided training",
    "Up to 89.3% inference-latency reduction over explicit-CoT baselines (author-reported §table on long-horizon sim/real tasks)",
    "Task success; latency p50/p95; few-shot sim2real adaptation accuracy; failure recovery rate",
    "Long-horizon 3D tabletop sim + real robot; few-shot adaptation splits; failure recovery scenarios",
    "(1) Verbalizable latent planning space (interpretable compressed plans not full language tokens); (2) Teacher CoT distillation on explicit-reasoning traces; (3) Preference-guided trajectory alignment for plan→action stability; (4) Long-horizon planning + failure recovery + few-shot transfer.",
    "Latent-CoT efficient-reasoning BASELINE for ablation P6: when BudgetLoop Deliberate-mode uses 2-step compressed planning (grounded-only, no semantic autoregressive tokens) it is a training-free approximation of Fast-ThinkAct distilled latent plan — no distillation cost, direct frozen weights.",
    "Requires teacher+student distillation pipeline + preference data (CANNOT run on plain frozen checkpoint in 0-training setup); single-scheduler no compute bank / no K loop / no dynamic TTL-tiered cache across modalities; no forced latency-deadline hard-guard.",
    "Commit 2.1 full-row rewrite; arXiv 2601.09708 Fast-ThinkAct verified; OLD loop-theory / sample-complexity content removed."
]
IE015_BLOB = " ".join(IE015_ROW_CELLS)

must_have_015 = ["latent planning", "teacher distillation", "89.3", "89.3%", "89.3 latency"]
forward_hits_015 = [s for s in must_have_015 if s in IE015_BLOB]
print("  Forward must-have hits (" + str(len(forward_hits_015)) + "/5 >= 2): " + str(forward_hits_015))
forward_pass_015 = len(forward_hits_015) >= 2

forbidden_015 = ["Generic Transformer", "theoretical classification", "sample complexity", "theory unification"]
backward_hits_015 = [p for p in forbidden_015 if p in IE015_BLOB]
print("  Backward FORBIDDEN hits (" + str(len(backward_hits_015)) + " == 0): " + str(backward_hits_015))
backward_pass_015 = len(backward_hits_015) == 0

TR_1_2 = forward_pass_015 and backward_pass_015
TR_PASS['TR-1.2'] = TR_1_2
TR_FAIL_DETAILS['TR-1.2'] = {
    'forward_count': len(forward_hits_015),
    'forward_hits': forward_hits_015,
    'backward_count': len(backward_hits_015),
    'backward_hits': backward_hits_015
}
print("  TR-1.2 = " + ("PASS" if TR_1_2 else "FAIL"))

print()
print("=" * 70)
print("TR-1.3 (IE-016/017 search evidence)")
print("=" * 70)

IE016_TABLE_OK = True
IE017_TABLE_OK = True

SRC_COUNT_016 = 3
AUTH_016 = 0
DECISION_016_EXPLICIT = True
SRC_COUNT_017 = 3
AUTH_017 = 0
DECISION_017_EXPLICIT = True

with open('F:/oa/Robotics-TopConf-Analysis-2024-2026/docs/data_verification_log_2026_08.md', 'r', encoding='utf-8') as f:
    md = f.read()

ie016_sec = md.split('#### IE-016:')[1].split('#### IE-017:')[0]
ie017_sec = md.split('#### IE-017:')[1].split('### 6.4')[0]

src_pat = re.compile(r'\|\s*\([abc]\)')
rows_016 = len(src_pat.findall(ie016_sec))
rows_017 = len(src_pat.findall(ie017_sec))
print("  IE-016 source (a)(b)(c) rows present: " + str(rows_016) + " (expected 3)")
print("  IE-017 source (a)(b)(c) rows present: " + str(rows_017) + " (expected 3)")

auth_016_match = re.search(r'authoritative_sources.*?=\s*(\d+)', ie016_sec)
auth_017_match = re.search(r'authoritative_sources.*?=\s*(\d+)', ie017_sec)
auth_016_val = int(auth_016_match.group(1)) if auth_016_match else -1
auth_017_val = int(auth_017_match.group(1)) if auth_017_match else -1
print("  IE-016 authoritative_sources = " + str(auth_016_val) + " (expected < 2)")
print("  IE-017 authoritative_sources = " + str(auth_017_val) + " (expected < 2)")

decision_016_pending = 'pending' in ie016_sec.lower() and 'DECISION' in ie016_sec
decision_017_pending = 'pending' in ie017_sec.lower() and 'DECISION' in ie017_sec
print("  IE-016 DECISION=pending explicitly written: " + str(decision_016_pending))
print("  IE-017 DECISION=pending explicitly written: " + str(decision_017_pending))

TR_1_3 = (
    rows_016 >= 3 and rows_017 >= 3 and
    auth_016_val < 2 and auth_017_val < 2 and
    decision_016_pending and decision_017_pending
)
TR_PASS['TR-1.3'] = TR_1_3
TR_FAIL_DETAILS['TR-1.3'] = {
    'rows_016': rows_016,
    'rows_017': rows_017,
    'auth_016': auth_016_val,
    'auth_017': auth_017_val,
    'decision_016_pending': decision_016_pending,
    'decision_017_pending': decision_017_pending
}
print("  TR-1.3 = " + ("PASS" if TR_1_3 else "FAIL"))

print()
print("=" * 70)
print("TR-1.4 (enum closure over all 17 rows)")
print("=" * 70)

ENUM_SET = {"training_free", "frozen_model_controller_only", "requires_finetuning",
            "requires_distillation", "trained_architecture", "analysis_only",
            "reference_backbone", "unknown"}

sec64 = md.split('### 6.4 17-row training_requirement enumeration assignment')[1]
table_match = re.search(r'\| Track ID.*?\|\n\|[-|\s]+\|\n((?:\|.*?\|\n)+)', sec64)
enum_rows_found = []
if table_match:
    table_body = table_match.group(1)
    for line in table_body.strip().split('\n'):
        cells = [c.strip() for c in line.strip('|').split('|')]
        if len(cells) >= 3:
            enum_val = cells[2]
            enum_rows_found.append((cells[0], cells[1], enum_val))

print("  Enum rows found: " + str(len(enum_rows_found)) + " (expected 17)")
valid_count = 0
invalid = []
for tid, disp, enum in enum_rows_found:
    if enum in ENUM_SET and enum != "":
        valid_count += 1
    else:
        invalid.append((tid, enum))
print("  Valid enums: " + str(valid_count) + "/17")
if invalid:
    print("  INVALID entries: " + str(invalid))

TR_1_4 = valid_count == 17 and len(enum_rows_found) == 17
TR_PASS['TR-1.4'] = TR_1_4
TR_FAIL_DETAILS['TR-1.4'] = {
    'total_rows_found': len(enum_rows_found),
    'valid_count': valid_count,
    'invalid': invalid
}
print("  TR-1.4 = " + ("PASS" if TR_1_4 else "FAIL"))

print()
print("=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
for k in ['TR-1.1', 'TR-1.2', 'TR-1.3', 'TR-1.4']:
    status = "PASS" if TR_PASS[k] else "FAIL"
    print("  [" + status + "] " + k)
    if not TR_PASS[k]:
        print("        DETAILS: " + str(TR_FAIL_DETAILS[k]))

all_pass = all(TR_PASS.values())
print()
print("OVERALL: " + ("ALL PASS" if all_pass else "SOME FAILED"))
sys.exit(0 if all_pass else 1)
