# Second Brain Schema

本文件定义 wiki 页面的规范和约定。所有 workflow 执行时必须遵守。

## 语言设置

每个知识库在 `/wiki init` 时写入内容语言，存储在 `registries.json` 中（`KB_LANG`）。支持六种语言：

- **zh**: 用中文撰写所有 wiki 内容；专有名词保留原文，如 “Memex”、“Vannevar Bush”。
- **en**: Write all wiki content in English; keep proper nouns in their original language.
- **ja**: Wiki の本文を日本語で書く。固有名詞は原語を保持する。
- **es**: Escribir todo el contenido de la wiki en español; conservar los nombres propios en su idioma original.
- **fr**: Rédiger tout le contenu du wiki en français ; conserver les noms propres dans leur langue d’origine.
- **ko**: 모든 wiki 콘텐츠를 한국어로 작성하며, 고유명사는 원문을 유지한다.

规则：

- 新 ingest 的素材按 `KB_LANG` 语言撰写 wiki 页面；素材原文语言不改变目标输出语言。
- `/wiki query` 的用户可单次明确指定回答语言；这只影响本次对话回答，不改变 `KB_LANG`，页面回写仍按 `KB_LANG`。
- 已有页面不会因普通提问、语言切换或 lint 自动翻译；lint 只报告语言不一致并在用户确认后处理。
- `title`、`aliases`、页面正文、index 摘要、overview、conventions、log 等面向人阅读的内容跟随 `KB_LANG`。
- `tags` 跟随 `KB_LANG`，同一知识库内保持一致；旧标签不自动迁移或翻译。
- 文件名始终使用小写英文 slug + 连字符，不受 `KB_LANG` 影响。

## Frontmatter 规范

每个 wiki 页面必须包含 YAML frontmatter：

```yaml
---
title: Page Title                 # 跟随 KB_LANG 的页面标题
aliases: [alias1, alias2]         # 跟随 KB_LANG 的别名；可保留必要原文名
type: source | entity | concept | analysis | overview | conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [tag1, tag2]                # 跟随 KB_LANG；同一库内保持旧标签风格，不迁移
sources: [source_filename1, source_filename2]  # 引用的原始素材；source/overview/conventions 可省略
---
```

## 文件命名

- 全部使用小写英文 slug + 连字符: `reinforcement-learning.md`, `openai.md`。
- 非英文标题需转写或意译为稳定英文 slug: `知识管理` → `knowledge-management.md`。
- 素材摘要页与原始文件基名对应并 slug 化: `raw/Paper X.pdf` → `wiki/sources/paper-x.md`。
- 避免过长文件名，保持在 50 字符以内。

## 交叉引用

- 使用 Obsidian 双链语法: `[[page-name]]` 或 `[[page-name|显示文本]]`。
- 每个页面底部设 `## Related` 区块，列出所有相关链接。
- 新建页面时检查是否应添加到已有页面的 Related 区块。
- 链接目标使用英文 slug 文件名；显示文本可按 `KB_LANG` 使用本地化标题。

## 内容规范

- 按 `KB_LANG` 设置撰写 wiki 内容。专有名词保留原文。
- 优先陈述事实，标注信息来源。
- 当新素材与已有内容矛盾时，明确标注 `> ⚠️ 矛盾：...` 并说明两边的说法；非中文 `KB_LANG` 时使用同等含义的自然表达，不必逐字使用中文。
- 保持页面聚焦，一个页面一个主题。

## 索引格式

`wiki/index.md` 按类别组织；以下模板只表示结构，条目标题和摘要按 `KB_LANG` 输出：

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

`wiki/log.md` 按时间倒序，日志正文按 `KB_LANG` 输出：

```markdown
## [YYYY-MM-DD] <operation> | <title>
- 具体操作描述
- 影响的页面列表
```

operation 取值: `ingest`, `query`, `lint`, `update`, `init`, `wipe`。

## 矛盾处理

当新素材与已有 wiki 内容矛盾时：

1. **不删除旧信息** — 保留两方观点。
2. **标注矛盾** — 在相关段落使用 `KB_LANG` 的自然表达标注矛盾。
3. **注明来源** — 分别标注两方信息的出处素材。
4. **更新时间** — 标注各自信息的日期，便于判断时效性。
5. **留给用户判断** — 如果矛盾涉及核心论点，在讨论中提醒用户。
