# Commit 2.1 Hotfix - 实施计划 (Decomposed & Prioritized Task List)

## [/] Task 1: 证据抽取 & 审计决策表落地
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 用 arXiv Atom API + 标题精确搜索（exact-quote Semantic Scholar fallback）对 **VLA-IE-014 2505.08243** 和 **VLA-IE-015 2601.09708** 重新抽完整 abstract / authors / reported-metrics / datasets，形成每条独立的 per-column 决策表（不是只改标题，是 17 列一字段一字段填）。
  - 同时验证 VLA-IE-016 / 017 的可核验性：用 arXiv API search_query=ti:"<TITLE>"、Google Scholar（用 Semantic Scholar API 兜底）搜索两个标题；命中 ≤1 条 → 标记 `pending`。
  - 对 VLA 17 行中 `Training-Free?` 现有 display_text 做全量枚举扫描（逐行打印 3 列：Track ID, Display text, Proposed `training_requirement` 枚举值），形成 17-row manual assignment CSV。
  - **Deliverable**: 追加写入 `docs/data_verification_log_2026_08.md` 一个新 §"Commit 2.1 Hotfix Supplement"：包含 IE-014 17-col decision、IE-015 17-col decision、IE-016/017 search evidence table、17 行 training_requirement 分派表。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4
- **Test Requirements**:
  - `programmatic` TR-1.1：IE-014 decision table 必须同时出现 `LIBERO-90`、`train-time reasoning`、`~3x speedup` 三条证据引用；反向 bad-string "Generic LLM/ICL/weight-sharing/1B loop" 0 命中。
  - `programmatic` TR-1.2：IE-015 decision table 出现 `latent planning | teacher distillation | 89.3%` 三条；反向 bad-string "Generic Transformer / theoretical classification / sample complexity" 0 命中。
  - `programmatic` TR-1.3：IE-016/017 每条必须至少有 3 条 search source（arXiv ti-search / Semantic Scholar / GitHub 项目页搜索）的证据；0 命中分支在表格中写明 `authoritative_sources=0`。
  - `programmatic` TR-1.4：17 行 training_requirement 分派表 17 个值都在 8 枚举闭包内，不允许空字符串。
- **Notes**: Semantic Scholar 搜索用 `https://api.semanticscholar.org/graph/v1/paper/search?query=<URLencoded exact title>&limit=5&fields=externalIds,year,title,authors,venue`；失败就走 offline 分支（IE-016/017 默认 pending），不 block。

## [ ] Task 2: IE-014 + IE-015 全行 17 列语义重写 + IE-016/017 pending 标记
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `scripts/apply_commit2_corrections.py` 中新增两个 block：`PATCH_IE014_FULL_17COL = {...}` / `PATCH_IE015_FULL_17COL = {...}`，把 Task 1 decision 里 17 列字典（含新增的 training_requirement 列声明）逐字段覆盖。
  - 对 IE-016 / 017：若 search evidence < 2，在 Notes 列追加 `VERIFICATION_STATUS=PENDING; authoritative_sources=<N>; Commit 2.1`，并同步追加 `verification_status=pending` 辅助标识（写进 Notes 的同时，在 training_requirement 辅助派生列统一写）。
  - 扩展现有 `apply_commit2_corrections.py` FORBIDDEN_PHRASES 列表，加入 IE-014/015 专属 bad-phrase（7 项合计）。
  - 在脚本末尾追加：CSV 跑前 hash；脚本跑后 hash；不一致则 `sys.exit(9) + 打印差异行`，保证幂等。
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1：运行 `apply_commit2_corrections.py` 一次后，VLA-IE-014 Primary Metric 不再是 "In-context task accuracy" 必须更改为 "Success rate (LIBERO-90) vs inference time"。
  - `programmatic` TR-2.2：VLA-IE-015 Reported Speedup 必须包含 "89.3% latency reduction"（作者原文 exact）。
  - `programmatic` TR-2.3：VLA-IE-015 `Training-Free?` display text 不再以 "YES" 开头。
  - `programmatic` TR-2.4：IE-016/017 Notes 字段包含 "VERIFICATION_STATUS=PENDING" 或对应 `verification_status=pending` 标识其中之一（允许用 schema 暂存）。
- **Notes**: 保留原有 `CANONICAL_TITLE_VERIFIED: arXiv:XXXX.XXXXX @ 2026-08-06` 的短 tag，但删除 canonical title 本体重复复制进 Notes 的旧内容（FORBIDDEN_PHRASES 中加 `"canonical title = "` 和 `"Revisiting Embodied …"` 这种长 canonical 文本片段如果发现出现在 Notes 就清掉）。

## [ ] Task 3: Training-Free 枚举列 + build_readme.py 统计 & 着色修复 + analysis 去重
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 在 `vla_inference_efficiency_2024_2026.csv` 末尾追加新列 `training_requirement`；脚本化填充（Task 1 的 17 行决策表，不手改 CSV）。
  - 改 `scripts/build_readme.py` 两处：
    1. 顶部 "Top training-free baselines" 统计：从 `training_requirement ∈ { training_free, frozen_model_controller_only }` 计数，完全废弃原自然语言匹配。
    2. VLA baselines 表格 `✅ YES / ❌ NO` 着色：`training_requirement in YES_SET → ✅ YES`，其它 → ❌ NO 或 N/A（analysis / reference）。
  - 修复 `tf_analysis` 重复计数：原逻辑在 aggregate dict 中对 `N/A (analysis paper)` 同时落入 `N/A bucket` 和 `analysis bucket` 加两遍，改成只允许第一次入桶，或改成 `collections.Counter` aggregate after per-row classification once。
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1：生成的 README.md 顶部 "N training-free baselines" 数字 = 表格中 `✅ YES` 出现次数（差值 0）。
  - `programmatic` TR-3.2：`git diff build_readme.py` 中 `tf_analysis` 函数 diff hunk 必须显示 "dedupe per paper id once" 或等价去重结构。
  - `programmatic` TR-3.3：README.md/zh-CN.md 渲染完后 training_requirement=analysis_only 的同一行在 Overview + 分析段落合计只出现 1 次（不再双重计数）。
  - `human-judgement` TR-3.4：双 README 表格第一列前 6 行 Fast ECoT / VLA-Cache / EfficientVLA / ActionCache / ElegantVLA / Training-Free Looped Xfmr ✅ 着色与枚举分派一致（对照 Task-1 17-row assignment table 肉眼检查）。
- **Notes**: 所有字段读取 `r.get("training_requirement", "unknown")`，对空字符串自动 fallback = unknown，禁止因列缺失导致 IndexError。

## [ ] Task 4: Notes 规范化（唯一 CANONICAL_TITLE_VERIFIED tag + 残留清洗 + 幂等）
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - 写一个 `normalize_notes(notes: str) -> str` 函数（放在 `apply_commit2_corrections.py` 顶部 utility 段）：
    1. 正则 `re.findall(r"CANONICAL_TITLE_VERIFIED:\s*arXiv:([0-9.]+)", notes)` 提取全部 ids，去重后按升序拼回一条短 tag（不含 OLD_TITLE= 尾段）。
    2. 把 FORBIDDEN_PHRASES 中所有残留都去掉（canonical title 本体复制、旧自总结标题、OLD_TITLE= 段、重复分隔符）。
    3. 所有 tag 统一用 ` | ` 分隔，首尾无 ` | ` 残留。
  - 在 apply_commit2_corrections.py 每次 patch 前/后都调用 normalize_notes，确保输出 Notes 干净。
  - 在脚本末尾增加：第一次运行后 git commit（不需要推送），再运行第二次，检查 `git diff --stat` 对 VLA CSV 的 bytes change = 0；否则 throw。
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-4.1：全 17 行 Notes 中 CANONICAL_TITLE_VERIFIED 正则出现次数 hist 最大值 = 1（0 行 ≥2）。
  - `programmatic` TR-4.2：第二次运行 `apply_commit2_corrections.py` 后的 `git diff --name-only` = 空列表。
  - `programmatic` TR-4.3：最长 Notes 行字符数 ≤ 300（NFR-5）。

## [ ] Task 5: 临时文件清理 + .gitignore 追加 4 种模式
- **Priority**: medium
- **Depends On**: None
- **Description**:
  - `git rm --cached .arXiv_tmp_commit2.csv; Remove-Item .arXiv_tmp_commit2.csv`
  - 追加 `.gitignore` 4 条：`.arXiv_tmp*`、`*.tmp.csv`、`__pycache__/`、`*.pyc`（放在文件末尾，追加 section 标题 `# commit 2.1 generated temp artifacts`）。
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1：`git ls-files .arXiv_tmp_commit2.csv` 标准输出为空。
  - `programmatic` TR-5.2：4 条模式均在 `.gitignore` 中出现。

## [ ] Task 6: Exit gates 脚本化 + 全量跑一遍 7 gates + 推送
- **Priority**: high
- **Depends On**: Task 2,3,4,5
- **Description**:
  - 新建 `scripts/exit_gates_commit2_1.py`，7 gates 每条实现为一个函数并返回 `(pass:bool, detail:str)`：
    1. `gate_ie014()` — 反向 grep 4 bad-strings + 正向 4 断言（LIBERO-90/train-time/3×/VLA Target 非 Generic LLM）。
    2. `gate_ie015()` — 反向 grep 4 bad-strings + 正向 3 断言（latent planning、89.3% latency reduction、training_requirement=requires_distillation）。
    3. `gate_pending_016_017()` — 若 IE-016/017 无权威链接：Notes 含 PENDING tag + README 两条 grep=0；若搜到权威来源则改为权威来源存在断言。
    4. `gate_tf_enum()` — README 顶部数字 = 表格 ✅ 数量；同时 tf_analysis 没重复（analysis_only 唯一）。
    5. `gate_notes_idempotent()` — CANONICAL_TITLE_VERIFIED per-row ≤ 1；第二次 apply 后 diff 为空。
    6. `gate_git_cleanup()` — git ls-files `.arXiv_tmp_commit2.csv` = empty + 4 ignore patterns present。
    7. `gate_count_invariance()` — verified=78 pending=22 pred=20 sum=120 + build_readme.py 成功（无异常）。
  - 所有 gate 跑完，打印 `GATE1=PASS ... GATE7=PASS` 或失败原因。
  - 单 commit 推送，msg 开头：`commit 2.1/7 hotfix: IE014 IE015 full semantic rows; training_requirement enum; notes dedupe; tmpfile cleanup; 7/7 gates`。
- **Acceptance Criteria Addressed**: AC-7, NFR-1, NFR-2, NFR-3
- **Test Requirements**:
  - `programmatic` TR-6.1：`python scripts/exit_gates_commit2_1.py` exit_code = 0。
  - `programmatic` TR-6.2：打印的每条 gate detail 中含每条 sub-check 的实际返回值（例如 "IE014 bad Generic LLM: 0 hits ✓"），**不允许只打印 PASS/FAIL**。
  - `human-judgement` TR-6.3：最终 commit message 含 "commit 2.1/7 hotfix" 前缀、列出 4 类变更、注明 "7/7 gates GREEN"。

**NOTE for agents**：
- Task 6 必须在 2,3,4,5 全部 pass 后才执行；**推送前**必须在本机把 7 gates 全部 GREEN 一次，并把 stdout/stderr 追加写入 `docs/data_verification_log_2026_08.md` §"Commit 2.1 Hotfix Gates Stdout"。
- 严禁多 commit，必须 squash 成一条。
