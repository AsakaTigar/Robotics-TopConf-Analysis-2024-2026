# Commit 2.1 Hotfix — Product Requirement Document

## Overview
- **Summary**: 在 Commit 2/7 (`0eab18f`) 已完成的 canonical-title 修正之上，执行一次插入式 hotfix commit：解决 7 个 auditor 发现的"表面门全绿、实际语义仍错位"的残留问题，然后才能进入原定 Commit 3/7（schema + verification_status 枚举）。
- **Purpose**: 防止错误的 baseline 语义（VLA-IE-014 整行仍然是旧的 Looped Transformer ICL 论文、VLA-IE-015 整行仍然是 loop-theory 综述）被写进 schema 固化进数据集；同时修掉 Training-Free 脆匹配、重复计数、临时文件被入库、Notes 重复标记等工程漏洞。
- **Target Users**:
  1. 数据集维护者（Agent / Auditor）—— 需要可信的 enumeration-only baselines。
  2. BudgetLoop-VLA 论文写作方（后续要拿 verified baseline 画 12 矩阵）—— 不能拿 ICL 论文当 robot reasoning 对照。

## Goals
- **G1 VLA-IE-014 全行语义纠正**：Title 改为 `Training Strategies for Efficient Embodied Reasoning` 之后，其余 11 个字段也完全对齐 arXiv 2505.08243（robot policy / VLA 方向 / LIBERO-90 / train-time reasoning supervision / 约 3× 推理加速，training-free=NO），不再残留任何 Generic LLM / ICL / weight-sharing loops / 1B-loop-vs-1B-non-loop 等原错误论文的内容。
- **G2 VLA-IE-015 全行语义纠正**：Title 改为 `Fast-ThinkAct: Efficient VLA Reasoning via Verbalizable Latent Planning` 之后，其余 11 个字段完全对齐 arXiv 2601.09708（teacher distillation / preference-guided / 报告 89.3% latency reduction / long-horizon planning / training-free=NO），不再残留 Generic Transformer / theoretical classification / sample complexity / theory unification 等原错误 loop-theory 综述论文内容。
- **G3 VLA-IE-016 / 017 证据隔离**：在 arXiv / 会议官网 / 项目页 找不到可核验的权威来源时，物理降级为 `verification_status=pending`，**永不入 verified=78 计数、永不入 README baselines 对比表**；禁止根据标题自行补作者 / venue / speedup / 指标。
- **G4 Training-Free 枚举规范落地**：新增 8 值枚举字段 `training_requirement ∈ { training_free, frozen_model_controller_only, requires_finetuning, requires_distillation, trained_architecture, analysis_only, reference_backbone, unknown }`；保留旧列 `Training-Free?` 仅作为 display text；README 计数和表格 ✅ 着色**只从枚举字段读**，解决 "Top 统计 = 2 / 表格 = 6 个 YES" 矛盾，同时修复 `tf_analysis` 里 `N/A (analysis paper)` 加两遍的重复计数漏洞。
- **G5 Notes 幂等与唯一 CANONICAL_TITLE_VERIFIED 标签**：每行 Notes 中 CANONICAL_TITLE_VERIFIED 出现次数 ≤ 1；删除旧自总结标题残留；canonical title 本体**不再复制进 Notes**；详细 old→new 证据**只存在 `docs/data_verification_log_2026_08.md`**；`apply_commit2_corrections.py` 连续跑两遍，`csv_hash` 必须前后一致（幂等）。
- **G6 临时文件清理 + ignore**：删除并提交 `.arXiv_tmp_commit2.csv`；`.gitignore` 追加 `.arXiv_tmp*`、`*.tmp.csv`、`__pycache__/`、`*.pyc` 四种模式；`git ls-files .arXiv_tmp_commit2.csv` 返回空。
- **G7 新增硬验收门全部通过**：新增的 7 条 gate 全部对应具体可跑命令 + 预期返回值，不是关键词 grep 表面式。

## Non-Goals (Out of Scope)
- **NOT** 实施原定 Commit 3/7（schema + verification_status 枚举大重构 + CI validate.yml）—— 等 2.1 通过后另起。
- **NOT** 更改 datasets/ 主 CSV 120 行的分区计数（verified 仍 =78 / pending=22 / pred=20，计数不变）。
- **NOT** 横向新收录任何一篇机器人论文（与审计报告 §7 "停止横向加论文"一致）。
- **NOT** 重新生成 BudgetLoop-VLA proposal（那是 Commit 6/7 的范围）。
- **NOT** 改 README 视觉样式或双语翻译。

## Background & Context
- 上一轮 commit `0eab18f` 声称 7/7 GREEN，但 auditor 核对线上仓库后发现：
  1. 7 条 gate 只检查了 bad string 消失和 row count，没有逐字段语义比对——导致 VLA-IE-014 / 015 只换了 title，整行其余 11 字段还是旧错误论文。
  2. Training-Free 统计依赖自然语言字符串脆匹配，漏了 YES(inference only) 等 6 种写法，README 顶部写 "2 training-free baselines"，但表格 6 条都标 ✅ YES。
  3. 临时文件 `.arXiv_tmp_commit2.csv` 已 delete，但 delete 没有推送，线上仍在仓库中。
  4. apply_commit2_corrections.py 的重复检查只看完整 tag，旧 tag+不同标题尾巴仍会重复追加，幂等性不成立。
- 审计报告 §AUDIT_P0 ③ 已点名 "build_readme.py 4 漏洞（脆字符串匹配 / 过滤+枚举缺失 / N/A 重复计数）"——本 hotfix 先拿 Training-Free 做一次"小枚举落地"，把最明显的矛盾修好，再在 Commit 3 扩到全 schema verification_status 枚举。

## Functional Requirements
- **FR-1 (IE-014 rewrite)**：在 `research_tracks/vla_inference_efficiency_2024_2026.csv` 中，Track ID = VLA-IE-014 整行 17 列（Year / Venue / Title / Authors / Affiliation / Paper Link / Code Link / Method Category / VLA Target / Training-Free? / Reported Speedup / Primary Metric / Evaluated On / Key Mechanism / Relevance BudgetLoop / Gaps / Notes），依据 arXiv 2505.08243 abstract+intro 的作者原文全部重写；training_requirement = requires_finetuning。
- **FR-2 (IE-015 rewrite)**：Track ID = VLA-IE-015 整行 17 列依据 arXiv 2601.09708 abstract 原文重写；training_requirement = requires_distillation。
- **FR-3 (IE-016/017 isolate)**：
  1. 用 arXiv API + title 搜索（exact quote）+ 会议官网 / GitHub 项目页，检索 IE-016 / 017 两标题；
  2. **任一条命中**（arXiv abs 页 / conference proceeding DOI / 作者 GitHub 项目页有 paper link 或 arXiv id）→ 保留在 verified 并填充 authors / link / venue / year；
  3. **0 命中** → ① verification_status = pending（写进 Notes 追加字段并同步到 datasets/pending_verification.csv，partition_commit1.py 重新分区）；② verified baseline 计数不包含；③ README baselines 表不渲染；④ author / venue / speedup / metric 四列全部清空，不允许猜测。
- **FR-4 (Training-Free enum + dedupe)**：
  1. 在 `vla_inference_efficiency_2024_2026.csv` 后追加新列 `training_requirement`（8 值闭合枚举，允许 `unknown` 当 fallback，不允许空）；
  2. 逐行人工分派，旧列 `Training-Free?` 原有 display 文本保留不动；
  3. `build_readme.py` 顶部"Top training-free baseline 计数"只从 `training_requirement == training_free OR training_requirement == frozen_model_controller_only` 统计；
  4. 表格 ✅/❌ 着色只从枚举画，不再看 `Training-Free?` 字符串；
  5. 修复 `tf_analysis` 函数，`analysis_only` 只统计 1 次，不再把同一行在 N/A (general) 和 N/A (analysis paper) 各加一遍。
- **FR-5 (Notes dedupe & idempotence)**：
  1. apply_commit2_corrections.py 运行前先把每行 Notes 中所有 `CANONICAL_TITLE_VERIFIED: arXiv:<X>` 按正则全量提取、去重、只保留一个；
  2. 删除 Notes 中的"旧自总结标题残留"字符串（如 14/015 旧 bad title、old style `OLD_TITLE=` 等），`docs/data_verification_log_2026_08.md` 是唯一证据仓；
  3. 脚本末尾增加 hash self-check：跑前 `hash(csv_bytes)` → 跑后 `hash(csv_bytes)`，不一致则 `returncode=9` 并打印 diff。
- **FR-6 (Temp file + gitignore)**：`git rm --cached .arXiv_tmp_commit2.csv && rm .arXiv_tmp_commit2.csv`；`.gitignore` 追加 4 种模式。
- **FR-7 (Exit gates 代码化)**：新增脚本 `scripts/exit_gates_commit2_1.py`，七条 gate 每条都有 `subprocess.run` 具体命令 + 返回值校验，非 0 直接 exit，供后续 agent / CI 复用。

## Non-Functional Requirements
- **NFR-1 (Idempotence)**：`apply_commit2_corrections.py` 连续 2 次调用后，`sha256sum vla_inference_efficiency_2024_2026.csv` 完全相同（programmatic）。
- **NFR-2 (Partition count invariance)**：`partition_commit1.py` 跑完后 verified=78 pending=22 pred=20 sum=120 不变（程序 assert）。
- **NFR-3 (Verified gate 7 全绿)**：`scripts/exit_gates_commit2_1.py` 返回 exit_code=0（7 条内部 gate 全部 pass）。
- **NFR-4 (No regression on bilingual README)**：`build_readme.py` 成功生成 README.md/README.zh-CN.md，char count 波动范围 ± 2%（programmatic + human）。
- **NFR-5 (Audit trail single source of truth)**：任意 VLA 行的 Notes 最大长度 ≤ 300 字符，old→new 证据不再内联 CSV，一律跳转 `docs/data_verification_log_2026_08.md`（programmatic 长度断言）。

## Constraints
- **Technical**：纯 Python3 + stdlib 解决；不引入 pandas / click 等新依赖；`build_readme.py` 保留现有 TRANSLATIONS 架构和 BASE 自识别。
- **Business**：严格单 commit（hotfix 只允许 1 个 commit，不能拆多个），commit message 必须以 "commit 2.1/7 hotfix:" 开头。
- **Dependencies**：只允许读 arXiv Atom API（`export.arxiv.org` 走 `urllib` stdlib，允许 offline fallback 用 commit2 已存的 canonical data）。

## Assumptions
- **A1**：VLA-IE-016 / 017 大概率搜不到（否则 auditor 不会点名要降级为 pending）——实施方先搜，搜不到就走 pending 分支；如果搜到了，在决策表 doc 里附证据链。
- **A2**：在 research_tracks CSV 加新列 `training_requirement` 不会影响 build_readme.py 的 VLA baselines 表（build_readme.py 当前只按列名读字段，字段数扩展安全）—— 如果 build_readme.py 实际是按 column index，实施方要在 FR-4 同步修复成按 column name 读。
- **A3**：用户同意 "verified=78 计数不变" 的语义等价于 "VLA-IE-016/017 本来就不在主 78 行（它们是 business track 内部条目，和 datasets 分区不是一张表）"，FR-3 的 pending 隔离不改变 datasets/ 四份分区文件字节数——如果它们确实通过 partition_commit1.py 参与分区了，实施方在 report 里写明偏移值。

## Acceptance Criteria

### AC-1: VLA-IE-014 整行语义对齐 ECoT-Lite
- **Given**：research_tracks VLA CSV 中 `Track ID == VLA-IE-014`
- **When**：逐字段比对 against arXiv 2505.08243 abstract + Table 1 报告 speedup
- **Then**：该行不包含任何 "Generic LLM / ICL / weight-sharing loops / same-FLOPs deep non-loop / 1B loop / 1B non-loop" 字符串；同时包含 `LIBERO-90`、`training supervision` 或 `train-time reasoning`、`~3x` 或 `3× inference speedup`、`VLA Target != Generic LLM` 四项；
- **Verification**：`programmatic`（`exit_gates_commit2_1.py --gate=IE014`，断言 + 关键词反向 grep + 正向关键词 count）。
- **Notes**：允许 1 项正向关键词命中失败（abstract 转述可能换词），但反向 4 项 bad string 必须 0 命中。

### AC-2: VLA-IE-015 整行语义对齐 Fast-ThinkAct
- **Given**：`Track ID == VLA-IE-015`
- **When**：逐字段比对 against arXiv 2601.09708 abstract
- **Then**：不包含 "Generic Transformer / theoretical classification / sample complexity / theory unification"；同时包含 `latent planning` 或 `teacher distillation`、`89.3%` 或 `latency reduction`、`training_requirement == requires_distillation` 三项；
- **Verification**：`programmatic`（`exit_gates_commit2_1.py --gate=IE015`）。

### AC-3: IE-016/017 未核验时进入 pending
- **Given**：arXiv / 会议官网 / GitHub 三件套检索结果 ≤ 1 命中（不足构成"权威证据"）
- **When**：`partition_commit1.py` 重跑
- **Then**：两条在 pending_verification.csv 出现（或在 business-only CSV 中被标记 verification_status=pending，视其归属）；`scripts/build_readme.py` 的 README baselines 表**不渲染**这两条；
- **Verification**：`programmatic`（`exit_gates_commit2_1.py --gate=PENDING016017` + `Select-String -Path README.md,README.zh-CN.md -Pattern "VLA-IE-016|VLA-IE-017" | Measure-Object` 返回 0）。

### AC-4: Training-Free 枚举与表格着色一致
- **Given**：VLA 17 行已分派 `training_requirement`
- **When**：跑 build_readme.py 生成双语 README
- **Then**：README 顶部 "N training-free baselines" 的数字 = 枚举计数（training_free+frozen_model_controller_only）= baseline 表格中 ✅ YES 的着色数量 ± 0；`tf_analysis` 不再重复计数（同一个 paper id 最终在 aggregate dict 中只会出现 1 次）；
- **Verification**：`programmatic`（`exit_gates_commit2_1.py --gate=TF_ENUM`）。

### AC-5: Notes 幂等 & CANONICAL_TITLE_VERIFIED ≤ 1
- **Given**：VLA CSV + 修正脚本
- **When**：
  1. 统计第一次运行前 Notes 中每行 `CANONICAL_TITLE_VERIFIED` 出现次数；
  2. 运行 `apply_commit2_corrections.py`；
  3. 再运行一次（第二次）；
  4. `git diff -- research_tracks/vla_inference_efficiency_2024_2026.csv`。
- **Then**：第二次 diff 为空；所有行的 CANONICAL_TITLE_VERIFIED 次数 ≤ 1；
- **Verification**：`programmatic`（`exit_gates_commit2_1.py --gate=NOTES_IDEMPOTENT`）。

### AC-6: 临时文件清理 + ignore
- **Given**：线上仍存在被追踪的 `.arXiv_tmp_commit2.csv`
- **When**：`git ls-files .arXiv_tmp_commit2.csv`
- **Then**：返回空；`.gitignore` 中同时含 `.arXiv_tmp*`、`*.tmp.csv`、`__pycache__/`、`*.pyc` 四条模式；
- **Verification**：`programmatic`（`exit_gates_commit2_1.py --gate=GIT_CLEANUP`）。

### AC-7: 新增 7 条 exit gates 全部 GREEN + commit message 规范
- **Given**：所有 subtask 跑完
- **When**：`scripts/exit_gates_commit2_1.py`（无参数，跑全部 7 条）
- **Then**：exit_code = 0，stdout 形如 `GATE1=PASS GATE2=PASS ... GATE7=PASS`；git commit message 以 "commit 2.1/7 hotfix:" 开头；
- **Verification**：`programmatic` + `human-judgment`（commit message wording）。

## Open Questions
- [ ] **OQ-A3-verify**：VLA-IE-016/017 两行业务条目是否通过 partition_commit1.py 参与 datasets/ 四份分区？（如果 A3 假设失败，实施方须在 exit gates 里输出字节数变化并解释，**不得**为了保 78/22/20 数字而把两条无证据条目强行留在 verified）。
- [ ] **OQ-build-readme-col-index**：build_readme.py 的 VLA baselines 段是按列名还是列 index 取字段？影响 FR-4 新列插入的安全边界。
- [ ] **OQ-IE-016-017-authoritative**：是否有 auditor 已确认的权威来源链接？（默认按 FR-3 走 0 命中→pending 分支，如果之后补到证据，在 commit 3/7 再升回 verified）。
