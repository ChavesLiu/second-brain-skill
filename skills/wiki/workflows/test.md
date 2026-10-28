# Test 工作流

手动验证知识库的核心工作流（首次语言选择、再次调用、init、ingest、query、lint、wipe）和六语边界。此流程用于指导 LLM 实际执行和观察结果，不得编造“自动通过”。

> 路径约定：本文档中的 `raw/`、`wiki/` 均指当前知识库的绝对路径，由 SKILL.md 路由时确定（`KB_RAW`、`KB_WIKI`）。测试前需先通过知识库选择或 `/wiki init` 确定目标知识库；首次调用测试可在隔离环境或临时 settings/registries 上执行。

## 语言分工

- `UI_LANG`：测试过程提示、确认问题、测试报告使用该语言。
- `KB_LANG`：测试中写入 wiki 页面、index、overview、log 的内容使用该语言。
- test 不改变语言设置，除非测试项明确验证 `/wiki language <code>` 或首次 `needs_language` 分支。
- 内部脚本 JSON、命令输出需要用 `UI_LANG` 转述，不直接当最终报告。
- 下方中文模板只表示结构；实际报告按 `UI_LANG` 自然生成。

## 测试总则

- 每个测试项都要记录“实际观察到的结果”；没有执行或没有观察到，不得标为通过。
- 如果某项需要人工选择或 LLM 手动判断，标注为“需手动确认/已人工确认”，不要伪装成自动化结果。
- 六语 LLM 行为边界（zh/en/ja/es/fr/ko）主要验证提示、映射和输出约束，不能声称由脚本自动完全验证。

## Test 0: 首次/再次调用与语言设置

### 0a. 首次调用 needs_language

在缺少 `settings.json` 顶层 `interaction_language` 的隔离状态下调用 `/wiki help` 或等价 router 命令，验证：

- [ ] 路由返回 `status: "needs_language"`。
- [ ] 结果包含 `supported_languages`。
- [ ] 结果包含 `original_args` 数组，保留原始 argv，不是拼接字符串。
- [ ] UI 只问一次语言问题。
- [ ] 直接选项只有 `zh`、`en`、`ja`、`es` 四个。
- [ ] 题干清楚说明 Other/自定义输入可填 `fr`（Français）或 `ko`（한국어）。
- [ ] 用户选择后通过 `router.py language <code>` 原子保存顶层 `interaction_language`，不是 LLM 直接 Write `settings.json`。
- [ ] 保存后使用 `original_args` 逐参数安全引用并重新执行。

### 0b. 再次调用

在已有 `settings.json` 顶层 `interaction_language` 后再次调用 `/wiki help`、自然语言查询或 `/wiki init`，验证：

- [ ] 不再触发首次语言选择。
- [ ] 帮助、交互和报告使用已保存的 `UI_LANG`。
- [ ] 普通提问使用其他语言时，不改变 `interaction_language`。

### 0c. 自然语言切换映射

分别用自然语言表达切换：英文、日文、法文、韩文，验证：

- [ ] 明确切换语言意图才路由到 `language`。
- [ ] args 是合法单个 code（如 `en`、`ja`、`fr`、`ko`），不能把整句原文作为 args。
- [ ] `/wiki language <code>` 成功后返回/报告字段使用 `interaction_language`，不是 `language`。
- [ ] 不支持 code 用当前 `UI_LANG` 报错并列出 `zh/en/ja/es/fr/ko`。

## Test 1: Init 工作流测试

执行 `/wiki init`，验证：

- [ ] 路由结果 `subcommand=init` 时 `kb = null`，执行流程没有解引用 `kb`。
- [ ] `init_lang = ui_lang`。
- [ ] 只询问路径和名称两个问题，不再询问第三个 wiki 内容语言问题。
- [ ] 创建 `raw/assets`、`wiki/sources`、`wiki/entities`、`wiki/concepts`、`wiki/analyses`。
- [ ] 创建 `wiki/index.md`、`wiki/log.md`、`wiki/overview.md`、`wiki/conventions.md`。
- [ ] 上述模板中的人类可读文本按 `INIT_LANG` 生成，非中文库不是中文字面模板。
- [ ] `registries.json` 新条目的 `language` 等于 `INIT_LANG`。
- [ ] 最终报告按 `UI_LANG` 输出。

## Test 2: 架构完整性检查

验证目录结构和核心文件是否存在：

```text
检查项:
- [ ] raw/ 目录存在
- [ ] raw/assets/ 目录存在
- [ ] wiki/ 目录存在
- [ ] wiki/sources/ 目录存在
- [ ] wiki/entities/ 目录存在
- [ ] wiki/concepts/ 目录存在
- [ ] wiki/analyses/ 目录存在
- [ ] wiki/index.md 存在且包含正确的分类标题
- [ ] wiki/log.md 存在且包含初始记录
- [ ] wiki/overview.md 存在且包含 frontmatter
- [ ] <skill-dir>/SCHEMA.md 存在且包含 schema 定义
- [ ] <skill-dir>/SKILL.md 存在
- [ ] <skill-dir>/workflows/init.md 存在
- [ ] <skill-dir>/workflows/ingest.md 存在
- [ ] <skill-dir>/workflows/query.md 存在
- [ ] <skill-dir>/workflows/lint.md 存在
- [ ] <skill-dir>/workflows/wipe.md 存在
- [ ] <skill-dir>/scripts/lint.py 存在
- [ ] <skill-dir>/scripts/router.py 存在
```

使用 Glob 和 Read 工具逐项验证，报告结果。

## Test 3: Ingest 工作流测试

1. 检查 `raw/` 下是否有测试素材 `raw/test-sample.md`。
2. 如果不存在，经用户确认后创建一个测试素材；内容语言可与 `KB_LANG` 不同，用于验证统一输出语言：

   ```markdown
   # Vannevar Bush 与 Memex 的构想

   1945年，Vannevar Bush 在《As We May Think》文章中提出了 Memex 的概念。
   这份素材包含实体：Vannevar Bush；概念：Memex、关联记忆、知识管理。
   ```

3. 执行 ingest 流程（调用 `/wiki ingest test-sample.md` 的逻辑）。
4. 验证：
   - [ ] `wiki/sources/test-sample.md` 已创建。
   - [ ] 文件包含正确 frontmatter。
   - [ ] `title`、`aliases`、正文、tags 按 `KB_LANG`。
   - [ ] 文件名为英文 slug。
   - [ ] `wiki/index.md` 已更新，新增条目按 `KB_LANG`。
   - [ ] `wiki/log.md` 已更新，新增记录按 `KB_LANG`。
   - [ ] `wiki/overview.md` 的统计已更新。
   - [ ] 完成报告按 `UI_LANG`。

## Test 4: Query 工作流测试

1. 执行查询：“Memex 是什么？”（或按 `UI_LANG` 的等价问题）。
2. 验证：
   - [ ] 回答引用了 wiki 中的相关页面。
   - [ ] 回答包含 `[[` 格式的页面引用。
   - [ ] 回答基于知识库内容而非 LLM 自身知识。
   - [ ] 默认回答语言为 `UI_LANG`。
   - [ ] 当用户单次明确要求另一种回答语言时，本次回答使用该语言，但 `settings.json` 的 `interaction_language` 不改变。
   - [ ] 若发生页面回写，写入内容仍按 `KB_LANG`。

## Test 5: Lint 工作流测试

1. 执行 lint 检查。
2. 验证：
   - [ ] 运行确定性脚本并读取 JSON。
   - [ ] 生成了结构化报告。
   - [ ] 报告包含统计数据。
   - [ ] 报告按优先级分类。
   - [ ] 内部 JSON 被 `UI_LANG` 转述，没有作为最终报告原样倾倒。
   - [ ] 语言不一致只报告或请求确认，不自动翻译旧页面。
   - [ ] 检测到测试产生的任何问题（如缺失的交叉引用）。

## Test 6: Wipe 工作流测试

选择低风险目标（优先测试样例页面或临时知识库），验证：

- [ ] 交互选择、确认和风险提示使用 `UI_LANG`。
- [ ] 删除前列出影响范围并等待确认。
- [ ] 删除移动到 `wiki/.trash/`，不删除 `raw/`。
- [ ] index、overview、log 的更新按 `KB_LANG`。
- [ ] 删除后运行 lint 检查。
- [ ] `/wiki wipe trash` 能列出回收站。
- [ ] `/wiki wipe restore` 能恢复并重新更新索引/关联。
- [ ] `/wiki wipe empty-trash` 明确提示不可逆并等待确认。

## Test 7: 六语 LLM 手动边界

分别以 `zh/en/ja/es/fr/ko` 作为 `UI_LANG` 或 `KB_LANG` 组合进行抽样验证。该项需要人工观察，不得编造自动通过。

- [ ] UI：帮助、确认问题、错误、报告按 `UI_LANG` 自然输出。
- [ ] KB：页面正文、title、aliases、tags、index、overview、conventions、log 按 `KB_LANG` 自然输出。
- [ ] 文件名：所有语言下仍为英文 slug。
- [ ] 自然语言切换：明确切换意图映射到合法 code；普通提问不改设置。
- [ ] Other 输入：`fr`、`ko` 可在首次语言选择中被接受；其他非法输入被拒绝。
- [ ] 非中文模板：不会把中文模板逐字写入 ja/es/fr/ko 知识库。

## Test 8: 清理

测试完成后询问用户是否保留测试数据，交互使用 `UI_LANG`：

- 保留：测试素材留在 wiki 中作为示例。
- 清理：删除测试产生的所有文件，恢复 index.md、overview.md 和 log.md；写入内容按 `KB_LANG`。

## 结果汇总

用 `UI_LANG` 输出报告。只把实际执行并观察到的项目标为通过；未执行项目标为未执行或需手动确认。

```text
========================================
  Wiki 测试报告
========================================
  首次/再次调用:   通过/失败/未执行 (N/M)
  Init 工作流:     通过/失败/未执行 (N/M)
  架构完整性:      通过/失败/未执行 (N/M)
  Ingest 工作流:   通过/失败/未执行 (N/M)
  Query 工作流:    通过/失败/未执行 (N/M)
  Lint 工作流:     通过/失败/未执行 (N/M)
  Wipe 工作流:     通过/失败/未执行 (N/M)
  六语手动边界:    通过/失败/需手动确认 (N/M)
========================================
  总计: N/M 通过；X 未执行；Y 需手动确认
========================================
```
