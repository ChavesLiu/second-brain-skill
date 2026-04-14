---
name: wiki
version: v1.0.0
author: ChavesLiu
description: |
  知识库管理工具。收录素材、查询知识、健康检查、重置删除。
  TRIGGER when: 用户提到「收录」「加到知识库」「ingest」，或提出知识库中可能有答案的问题（如「XX 是什么」「对比 XX 和 YY」「整理 XX 的信息」），或要求「检查知识库」「lint」，或要求「清空」「删除」「重置」知识库内容，或给出对知识库操作方式的反馈/偏好。
  DO NOT TRIGGER when: 问题与知识库无关（纯代码任务、文件操作、通用对话），或用户明确说不需要查知识库。
user-invocable: true
---

# Second Brain Skill

知识库的统一管理入口。支持命令式调用（`/wiki <cmd>`）和自然语言触发。

## 自然语言路由

当 skill 被自然语言触发（非 `/wiki` 命令格式）时，先判断意图再映射子命令：

| 用户意图 | 映射子命令 | 示例 |
|---------|-----------|------|
| 收录/添加素材 | `ingest` | "收录这篇文章"、"把 raw 里的新文件加到知识库" |
| 提问/查询/对比/整理 | `query` | "Memex 是什么"、"对比 RAG 和 Wiki 模式"、"整理一下 XX 的信息" |
| 反馈/偏好/纠正 | `query`（走反馈分支） | "回答要标注来源"、"你上次说错了" |
| 检查/审计 | `lint` | "检查下知识库有没有问题" |
| 删除/清空/重置 | `wipe` | "删掉 XX 相关的页面"、"重置知识库" |
| 初始化 | `init` | "创建一个新的知识库" |

确定子命令后，将用户原始输入作为 `args`，进入下方执行步骤。

## 执行步骤

### 1. 运行路由脚本

运行 `python <skill-dir>/scripts/router.py <子命令> [参数]` 获取路由结果（JSON）。

`<skill-dir>` 为本文件所在目录的绝对路径。对于自然语言触发，先按上表映射出子命令再调用。

### 2. 根据路由结果执行

根据 JSON 中的 `status` 字段分支：

#### `status: "ok"` — 正常执行

```
路由结果字段:
  subcommand  — 子命令名
  args        — 子命令参数
  workflow    — 工作流文件路径（相对于 skill 目录）
  schema      — SCHEMA.md 路径（需要时非 null）
  kb          — 知识库信息（id, name, root, wiki, raw, lang）
  skill_dir   — skill 目录绝对路径
  multiple_kbs — 是否有多个知识库（可选）
  kb_list     — 知识库列表（可选，multiple_kbs 时出现）
```

执行顺序：
1. 如果 `schema` 非 null → 读取 `<skill_dir>/<schema>` 了解页面规范
2. 如果 `<kb.wiki>/conventions.md` 存在 → 读取，作为本次操作的额外约束（用户对该知识库的操作偏好）
3. 读取 `<skill_dir>/<workflow>` 获取工作流
4. 用 `kb` 中的路径（`root`、`wiki`、`raw`）和语言（`lang`）替换 workflow 中的 `KB_ROOT`、`KB_WIKI`、`KB_RAW`、`KB_LANG`
5. 按工作流执行，`args` 作为子命令参数传入，遵守 conventions.md 中的约定
6. 如果 `multiple_kbs` 为 true，先告知用户当前使用的是哪个知识库（kb.name），提示可在 registries.json 中修改 default

#### `status: "select"` — 需要用户选择知识库

用 AskUserQuestion 展示 `kb_list` 让用户选择，然后用选中的知识库信息继续执行。选择后更新 `registries.json` 的 `default` 字段。

#### `status: "no_kb"` — 无知识库

输出: `⚠️ {message}`

#### `status: "error"` — 错误

输出错误信息。

#### `subcommand: "help"` — 帮助

直接输出：

```
Second Brain — LLM 驱动的知识库管理工具

命令:
  /wiki init                  创建并注册一个新的知识库
  /wiki ingest [文件名]       收录 raw/ 中的新素材（不指定则收录全部）
  /wiki query <问题>          基于知识库回答问题
  /wiki lint                  知识库健康检查
  /wiki wipe [子命令]         重置/删除（all | <关键词> | trash | restore | empty-trash）
  /wiki test                  自动化测试
  /wiki help                  显示本帮助

首次使用请先运行 /wiki init
```
