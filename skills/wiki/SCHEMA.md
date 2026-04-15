# Second Brain Schema

本文件定义 wiki 页面的规范和约定。所有 workflow 执行时必须遵守。

## 语言设置

每个知识库在 `/wiki init` 时设置语言，存储在 `registries.json` 中（`KB_LANG`）：
- **zh**: 用中文撰写所有 wiki 内容（专有名词保留英文原文，如 "Memex"、"Vannevar Bush"）
- **en**: Write all wiki content in English (keep proper nouns in their original language)

规则：
- 新 ingest 的素材按 `KB_LANG` 语言撰写 wiki 页面
- 已有页面不会自动翻译，可执行 `/wiki lint` 检测语言不一致的页面并批量翻译
- frontmatter 中的 title 字段跟随当前语言（但 tags 始终使用中文，确保一致性）
- 文件名始终使用小写英文+连字符，不受语言设置影响

## Frontmatter 规范

每个 wiki 页面必须包含 YAML frontmatter：

```yaml
---
title: Page Title
aliases: [中文别名]              # Obsidian 图谱显示用，language=zh 时填中文，language=en 时填英文
type: source | entity | concept | analysis | overview | conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]
sources: [source_filename1, source_filename2]  # 引用的原始素材
---
```

## 文件命名

- 全部使用小写英文 + 连字符: `reinforcement-learning.md`, `openai.md`
- 素材摘要页与原始文件同名: `raw/paper-x.pdf` → `wiki/sources/paper-x.md`
- 避免过长文件名，保持在 50 字符以内

## 交叉引用

- 使用 Obsidian 双链语法: `[[page-name]]` 或 `[[page-name|显示文本]]`
- 每个页面底部设 `## Related` 区块，列出所有相关链接
- 新建页面时检查是否应添加到已有页面的 Related 区块

## 内容规范

- 按 `KB_LANG` 设置撰写 wiki 内容（zh=中文，en=English）。专有名词保留原文
- 优先陈述事实，标注信息来源
- 当新素材与已有内容矛盾时，明确标注 `> ⚠️ 矛盾：...` 并说明两边的说法
- 保持页面聚焦，一个页面一个主题

## 索引格式

`wiki/index.md` 按类别组织：

```markdown
## Sources
- [素材标题](sources/filename.md) — 一句话摘要 (YYYY-MM-DD)

## Entities
- [实体名](entities/filename.md) — 一句话描述 [N 个素材引用]

## Concepts
- [概念名](concepts/filename.md) — 一句话描述

## Analyses
- [分析标题](analyses/filename.md) — 一句话摘要 (YYYY-MM-DD)
```

## 日志格式

`wiki/log.md` 按时间倒序：

```markdown
## [YYYY-MM-DD] <operation> | <title>
- 具体操作描述
- 影响的页面列表
```

operation 取值: `ingest`, `query`, `lint`, `update`, `init`, `wipe`

## 矛盾处理

当新素材与已有 wiki 内容矛盾时：

1. **不删除旧信息** — 保留两方观点
2. **标注矛盾** — 在相关段落使用 `> ⚠️ 矛盾：...` callout
3. **注明来源** — 分别标注两方信息的出处素材
4. **更新时间** — 标注各自信息的日期，便于判断时效性
5. **留给用户判断** — 如果矛盾涉及核心论点，在讨论中提醒用户
