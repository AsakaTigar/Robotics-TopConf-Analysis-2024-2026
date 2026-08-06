# Commit 2.1 Hotfix - 验收清单（每条须由独立验证子 Agent 黑盒执行，不允许实施子 Agent 自证）

## 7 条新增 Exit Gates（与 scripts/exit_gates_commit2_1.py 中 gate_*() 一一对应，每条必须有测试命令 + 实际返回值粘贴）

- [ ] **Checkpoint GATE-1: VLA-IE-014 全行语义无残留**
  - 测试命令 1 (反向 bad-string)：
    ```powershell
    cd F:\oa\Robotics-TopConf-Analysis-2024-2026; (Select-String -Path research_tracks/vla_inference_efficiency_2024_2026.csv -Pattern 'Generic LLM|\bICL\b|weight-sharing loops|same-FLOPs deep non-loop|1B loop|1B non-loop').Count
    ```
  - 预期返回：`0`（不允许 >0）。
  - 测试命令 2 (正向关键内容)：从 VLA CSV 读 Track ID=VLA-IE-014 这 1 行，`Primary Metric`, `Evaluated On / Dataset`, `VLA Target`, `Training-Free?`, `Reported Speedup` 5 列的 **完整字段值** 粘贴到 report，逐条对照 arXiv 2505.08243 abstract 人工判断合理性（human-judgment：**4/5 列合理即 PASS**）。

- [ ] **Checkpoint GATE-2: VLA-IE-015 全行语义无残留**
  - 测试命令 1 (反向 bad-string)：
    ```powershell
    (Select-String -Path research_tracks/vla_inference_efficiency_2024_2026.csv -Pattern 'Generic Transformer|theoretical classification|sample complexity|theory unification').Count
    ```
  - 预期返回：`0`
  - 测试命令 2 (正向 3 断言)：从 VLA CSV 读 Track=VLA-IE-015，
    - `Reported Speedup` 字段必须包含正则 `89\.3.*latency|latency.*89\.3`；
    - `Training-Free?` 字段不得以 "YES" 字母开头（大小写不敏感）；
    - `training_requirement` 列值必须等于 `requires_distillation`。
    - 三项全部满足即 PASS。

- [ ] **Checkpoint GATE-3: VLA-IE-016 / 017 证据不足时 pending 隔离**
  - 前置步骤：先打印 IE-016/017 两标题在 arXiv/semantic scholar 搜索返回的命中数（≥2 才视为"已验证"，否则 pending）。
  - 测试命令 A（pending 分支，若命中数 <2）：
    ```powershell
    (Select-String -Path README.md,README.zh-CN.md -Pattern 'VLA-IE-016|VLA-IE-017').Count ;# 必须 = 0（不进 baseline 表）
    ```
    同时，CSV 中对应行 Notes 或辅助列含 `VERIFICATION_STATUS=PENDING` / `verification_status=pending`。
  - 测试命令 B（已验证分支，若命中数 ≥2）：打印权威来源，并检查 CSV 中 author/link/venue 三列均非空。

- [ ] **Checkpoint GATE-4: Training-Free 枚举一致性（README 顶部 N = 表格 ✅ 数量）**
  - 测试命令：
    ```powershell
    python -c "
    import re, pathlib
    readme = pathlib.Path('README.md').read_text(encoding='utf-8')
    top_num = re.findall(r'(\d+)\s+(?:directly usable )?(?:training-free|Training-Free) baselines', readme)
    table_yes = readme.count('✅ YES') + readme.count('✅ 是')
    print('TOP_COUNT=', top_num[:3])
    print('TABLE_YES=', table_yes)
    "
    ```
  - 预期：`TOP_COUNT[0] == TABLE_YES`（字符串相等，int 相等），且 `TABLE_YES ≥ 1`。
  - 附加去重检查：`build_readme.py` 的 `tf_analysis` aggregate dict 中 paper id 重复次数 `Counter(ids).most_common()[0][1] == 1`。

- [ ] **Checkpoint GATE-5: Notes 幂等 + CANONICAL_TITLE_VERIFIED ≤ 1（每行）**
  - 测试命令 1（重复 tag 统计）：
    ```powershell
    python -c "
    import csv, re, pathlib
    rows = list(csv.DictReader(open('research_tracks/vla_inference_efficiency_2024_2026.csv', encoding='utf-8-sig')))
    cnt = [len(re.findall(r'CANONICAL_TITLE_VERIFIED', r.get('Notes','') or '')) for r in rows]
    print('max_ctv_per_row=', max(cnt)); print('rows_violating=', sum(1 for c in cnt if c>1))
    "
    ```
  - 预期 `max_ctv_per_row ≤ 1 AND rows_violating = 0`。
  - 测试命令 2（幂等性）：
    ```powershell
    $before = git hash-object research_tracks/vla_inference_efficiency_2024_2026.csv
    python scripts/apply_commit2_corrections.py
    python scripts/apply_commit2_corrections.py   ;# 第二次
    $after  = git hash-object research_tracks/vla_inference_efficiency_2024_2026.csv
    Write-Host "before=$before after=$after equal=$($before -eq $after)"
    ```
  - 预期：`before == after`（True）。

- [ ] **Checkpoint GATE-6: 临时文件 .arXiv_tmp_commit2.csv 不再被追踪 + ignore 四条模式**
  - 测试命令：
    ```powershell
    git ls-files .arXiv_tmp_commit2.csv | Measure-Object | Select-Object -ExpandProperty Count ;# 必须=0
    Get-Content .gitignore -Raw | Select-String -Pattern '\.arXiv_tmp\*' ; # 1 命中
    Get-Content .gitignore -Raw | Select-String -Pattern '\*\.tmp\.csv'  ; # 1 命中
    Get-Content .gitignore -Raw | Select-String -Pattern '__pycache__/'  ; # 1 命中
    Get-Content .gitignore -Raw | Select-String -Pattern '\*\.pyc'       ; # 1 命中
    ```

- [ ] **Checkpoint GATE-7: 分区计数不变 + README 正常生成 + exit_gates 脚本总返回 0**
  - 分区计数断言：
    ```powershell
    (Import-Csv datasets/verified_papers.csv | Measure-Object).Count      ;# 78
    (Import-Csv datasets/pending_verification.csv | Measure-Object).Count ;# 22
    (Import-Csv datasets/predicted_trends.csv | Measure-Object).Count     ;# 20
    ```
  - README build 断言：`python scripts/build_readme.py` exit_code=0，README.md 32000-36000 chars（在合理范围，不爆掉）。
  - 总 exit gates：`python scripts/exit_gates_commit2_1.py` exit_code = 0 且 stdout 每行末尾打印的 gate 明细 7/7 PASS。

## 黑盒一致性（交叉验证，独立于实施子 Agent 执行）
- [ ] **CP-1**：单独再跑 3 次 `apply_commit2_corrections.py`（共 3 次）后 `git diff --name-only` = 空，证明幂等性不依赖"第一次后立即第二次"的顺序。
- [ ] **CP-2**：从 7 gates 结果中，任取 GATE-1 和 GATE-2 的反向 bad-string grep 结果，用 PowerShell 原始 `Select-String -Pattern` 和 `grep -c` 两种方式再比对一次，数字一致（Windows 下用 `findstr` 等价替代）。
- [ ] **CP-3**：README.md 与 README.zh-CN.md 中 training-free 段落数字一致（双语一致断言）。
