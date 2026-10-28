# Init 工作流

创建并注册一个新的知识库。

## 语言分工

- `UI_LANG`：本流程中所有提问、选项说明、确认和最终报告使用该语言。
- `INIT_LANG`：由路由提供，固定等于首次/当前 `UI_LANG`，作为新知识库的 `KB_LANG` 写入注册表。
- init 路由结果中 `kb = null`，本流程不得读取或解引用 `kb.root`、`kb.wiki`、`kb.raw`、`kb.lang`。
- 不再询问第三个“Wiki 页面语言”问题；新库页面语言默认使用 `INIT_LANG`。
- 下方中文模板只表示内容结构。实际创建 `index.md`、`log.md`、`overview.md`、`conventions.md` 时，面向人阅读的标题、说明、摘要、日志均按 `INIT_LANG` 自然生成，不能把中文模板逐字输出到非中文库。

## 工作流程

### 1. 收集信息

使用 AskUserQuestion 只询问以下两个信息，题干、选项和说明使用 `UI_LANG`：

```json
{
  "questions": [
    {
      "question": "知识库根目录路径？（将在此路径下创建 raw/ 和 wiki/ 子目录）",
      "header": "路径",
      "multiSelect": false,
      "options": [
        {"label": "当前目录", "description": "使用当前工作目录作为知识库根目录"},
        {"label": "自定义路径", "description": "指定一个绝对路径"}
      ]
    },
    {
      "question": "给知识库起个名称（用于多库切换时显示）",
      "header": "名称",
      "multiSelect": false,
      "options": [
        {"label": "AI 研究", "description": ""},
        {"label": "读书笔记", "description": ""},
        {"label": "工作知识库", "description": ""}
      ]
    }
  ]
}
```

如果 `UI_LANG` 不是中文，必须按含义翻译上面问题和选项，但保留路径名 `raw/`、`wiki/` 不变。

### 2. 生成知识库 ID

从名称生成英文 slug 作为 ID（如 “AI 研究” → `ai-research`）。如果 `registries.json` 中已存在该 ID，用 `UI_LANG` 提示用户修改。

### 3. 创建目录结构

在目标路径下创建：

```bash
mkdir -p <path>/raw/assets
mkdir -p <path>/wiki/sources
mkdir -p <path>/wiki/entities
mkdir -p <path>/wiki/concepts
mkdir -p <path>/wiki/analyses
```

### 4. 初始化 wiki 核心文件

创建以下文件（如果不存在）。所有 human-readable 文本使用 `INIT_LANG`；文件名和目录名保持英文。

#### `<path>/wiki/index.md`

结构模板：

```markdown
# Wiki Index

> 此文件由 LLM 自动维护，是 wiki 的内容目录。按类别组织所有页面，每页一行摘要。
> LLM 在回答查询时优先阅读此文件以定位相关页面。

## Overview

- [Overview](overview.md) — Wiki 总览与当前知识图谱摘要
- [使用约定](conventions.md) — 用户对本知识库的操作偏好

## Sources

## Entities

## Concepts

## Analyses
```

非中文 `INIT_LANG` 时，说明文字、链接显示文本和摘要自然翻译；标题 `Sources`、`Entities`、`Concepts`、`Analyses` 可保持英文分类名以稳定结构。

#### `<path>/wiki/log.md`

结构模板：

```markdown
# Wiki Log

> 操作日志，按时间倒序记录所有 wiki 操作。

## [YYYY-MM-DD] init | 知识库初始化

- 创建知识库目录结构
- 初始化 index.md、log.md、overview.md、conventions.md
```

（YYYY-MM-DD 替换为当天日期；日志正文按 `INIT_LANG` 生成。）

#### `<path>/wiki/overview.md`

结构模板：

```markdown
---
title: Overview
aliases: [总览]
type: overview
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [overview]
---

# 知识库总览

## 统计

| 指标 | 数量 |
|------|------|
| 原始素材 | 0 |
| 素材摘要 | 0 |
| 实体页面 | 0 |
| 概念页面 | 0 |
| 分析页面 | 0 |

## 知识图谱摘要

（尚无内容，收录素材后自动更新）

## 近期活动

- [YYYY-MM-DD] 知识库初始化
```

`title`、`aliases`、tags、正文标题、表格字段和活动描述均按 `INIT_LANG` 生成；文件名仍为 `overview.md`。

#### `<path>/wiki/conventions.md`

结构模板：

```markdown
---
title: 使用约定
aliases: [约定]
type: conventions
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [meta]
---

# 使用约定

> 此页面记录用户对本知识库操作的偏好和约定。LLM 在执行任何操作前应先读取此页面。

## Query

（暂无）

## Ingest

（暂无）

## Lint

（暂无）

## 通用

（暂无）
```

`Query`、`Ingest`、`Lint` 可保持英文分类名；`通用` 可按 `INIT_LANG` 翻译为 General 等自然表达。其他可读文本按 `INIT_LANG` 生成。

### 5. 注册到 registries.json

读取 skill 目录下的 `registries.json`，添加新条目，并将新知识库设为默认：

```json
{
  "default": "<new-id>",
  "registries": {
    "<new-id>": {
      "name": "用户输入的名称",
      "path": "/absolute/path/to/kb",
      "language": "INIT_LANG",
      "created": "YYYY-MM-DD"
    }
  }
}
```

`language` 必须使用 `INIT_LANG` 的实际值（zh/en/ja/es/fr/ko），不得再次询问语言。

### 6. 处理已存在目录

如果目标路径已存在且包含 `raw/` 和 `wiki/` 子目录，用 `UI_LANG` 询问如何处理：

```json
{
  "questions": [{
    "question": "目标路径已存在知识库结构（包含 raw/ 和 wiki/）。如何处理？",
    "header": "已有目录",
    "multiSelect": false,
    "options": [
      {"label": "直接注册", "description": "跳过创建，仅将已有知识库注册到配置中"},
      {"label": "覆盖初始化", "description": "重新创建 wiki 核心文件（raw/ 保留不动）"},
      {"label": "取消", "description": "不做任何操作"}
    ]
  }]
}
```

### 7. 输出结果

最终报告使用 `UI_LANG`，语言字段显示实际 `INIT_LANG`：

```text
知识库已创建并注册

  名称: <name>
  路径: <path>
  语言: <INIT_LANG>
  ID:   <id>

  目录结构:
    <path>/raw/          ← 将素材放入此目录
    <path>/wiki/         ← LLM 维护的知识库

  下一步:
    1. 将素材文件放入 <path>/raw/
    2. 执行 /wiki ingest 开始收录
```

非中文 `UI_LANG` 时自然翻译报告说明，不改变命令 `/wiki ingest`、路径和 ID。
