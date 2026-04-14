# Test 工作流

自动化测试知识库的三个核心工作流（ingest、query、lint），验证架构完整性。

> 📌 **路径约定**: 本文档中的 `raw/`、`wiki/` 均指当前知识库的绝对路径，由 SKILL.md 路由时确定（`KB_RAW`、`KB_WIKI`）。测试前需先通过知识库选择或 `/wiki init` 确定目标知识库。

## 测试流程

### Test 1: 架构完整性检查

验证目录结构和核心文件是否存在：

```
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
- [ ] <skill-dir>/workflows/ingest.md 存在
- [ ] <skill-dir>/workflows/query.md 存在
- [ ] <skill-dir>/workflows/lint.md 存在
- [ ] <skill-dir>/workflows/wipe.md 存在
- [ ] <skill-dir>/scripts/lint.py 存在
```

使用 Glob 和 Read 工具逐项验证，报告结果。

### Test 2: Ingest 工作流测试

1. 检查 `raw/` 下是否有测试素材 `raw/test-sample.md`
2. 如果不存在，创建一个测试素材：
   ```markdown
   # Vannevar Bush 与 Memex 的构想

   1945年，Vannevar Bush 在《As We May Think》文章中提出了 Memex 的概念...
   （包含实体：Vannevar Bush、Memex；概念：关联记忆、知识管理）
   ```
3. 执行 ingest 流程（调用 /wiki ingest test-sample.md 的逻辑）
4. 验证：
   - [ ] `wiki/sources/test-sample.md` 已创建
   - [ ] 文件包含正确的 frontmatter
   - [ ] `wiki/index.md` 已更新，包含新条目
   - [ ] `wiki/log.md` 已更新，包含 ingest 记录
   - [ ] `wiki/overview.md` 的 source_count 已更新

### Test 3: Query 工作流测试

1. 执行查询："Memex 是什么？"
2. 验证：
   - [ ] 回答引用了 wiki 中的相关页面
   - [ ] 回答包含 `[[` 格式的页面引用
   - [ ] 回答基于知识库内容而非 LLM 自身知识

### Test 4: Lint 工作流测试

1. 执行 lint 检查
2. 验证：
   - [ ] 生成了结构化报告
   - [ ] 报告包含统计数据
   - [ ] 报告按优先级分类
   - [ ] 检测到测试产生的任何问题（如缺失的交叉引用）

### Test 5: 清理

测试完成后询问用户是否保留测试数据：
- 保留：测试素材留在 wiki 中作为示例
- 清理：删除测试产生的所有文件，恢复 index.md 和 log.md

## 结果汇总

```
========================================
  Wiki 自动化测试报告
========================================
  架构完整性:    ✅/❌ (N/M 通过)
  Ingest 工作流: ✅/❌ (N/M 通过)
  Query 工作流:  ✅/❌ (N/M 通过)
  Lint 工作流:   ✅/❌ (N/M 通过)
========================================
  总计: N/M 通过
========================================
```
