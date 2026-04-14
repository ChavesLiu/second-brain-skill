# Init 工作流

创建并注册一个新的知识库。

## 工作流程

### 1. 收集信息

使用 AskUserQuestion 询问以下信息：

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
    },
    {
      "question": "Wiki 页面使用什么语言撰写？",
      "header": "语言",
      "multiSelect": false,
      "options": [
        {"label": "zh（中文）", "description": "用中文撰写 wiki 内容，专有名词保留英文原文"},
        {"label": "en（English）", "description": "Write all wiki content in English"}
      ]
    }
  ]
}
```

### 2. 生成知识库 ID

从名称生成 slug 作为 ID（如 "AI 研究" → "ai-research"）。如果 registries.json 中已存在该 ID，提示用户修改。

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

创建以下文件（如果不存在）：

#### `<path>/wiki/index.md`

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

#### `<path>/wiki/log.md`

```markdown
# Wiki Log

> 操作日志，按时间倒序记录所有 wiki 操作。

## [YYYY-MM-DD] init | 知识库初始化

- 创建知识库目录结构
- 初始化 index.md、log.md、overview.md、conventions.md
```

（YYYY-MM-DD 替换为当天日期）

#### `<path>/wiki/overview.md`

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

#### `<path>/wiki/conventions.md`

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

### 5. 注册到 registries.json

读取 skill 目录下的 `registries.json`，添加新条目：

```json
{
  "default": "<new-id>",
  "registries": {
    "<new-id>": {
      "name": "用户输入的名称",
      "path": "/absolute/path/to/kb",
      "language": "zh",
      "created": "YYYY-MM-DD"
    }
  }
}
```

将 `default` 设为新创建的知识库 ID。

### 6. 处理已存在目录

如果目标路径已存在且包含 `raw/` 和 `wiki/` 子目录：

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

```
✅ 知识库已创建并注册

  名称: <name>
  路径: <path>
  语言: zh
  ID:   <id>

  目录结构:
    <path>/raw/          ← 将素材放入此目录
    <path>/wiki/         ← LLM 维护的知识库

  下一步:
    1. 将素材文件放入 <path>/raw/
    2. 执行 /wiki ingest 开始收录
```
