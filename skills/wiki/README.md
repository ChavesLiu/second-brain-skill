# Second Brain Skill

用 LLM 构建和维护的个人知识库。LLM 负责所有繁重的整理工作 — 摘要、交叉引用、归档、一致性维护 — 你负责挑选素材、提出好问题、思考这一切意味着什么。

> 原始设计理念见 [IDEA.md](IDEA.md)

---

## 快速开始

### 1. 环境准备

- 安装 [Claude Code](https://claude.ai/code)（CLI 工具）
- 安装 [Obsidian](https://obsidian.md/)（可选，用于浏览 wiki）

### 2. 初始化知识库

```
/wiki init
```

按提示输入知识库路径、名称和语言。支持多个知识库，多库时会自动询问操作哪个。

### 3. 可用命令

| 命令 | 功能 |
|------|------|
| `/wiki init` | 创建并注册新知识库 |
| `/wiki ingest` | 收录新素材到知识库 |
| `/wiki query <问题>` | 基于知识库回答问题 |
| `/wiki lint` | 对知识库进行健康检查 |
| `/wiki wipe` | 重置/删除知识库内容 |
| `/wiki test` | 运行自动化测试 |

### 4. 收录你的第一份素材

```
1. 将素材文件（Markdown、PDF 等）放入知识库的 raw/ 目录
2. 在 Claude Code 中执行 /wiki ingest
3. LLM 自动阅读素材、创建摘要页、拆分实体和概念页、维护交叉引用
   （遇到矛盾或歧义时才会询问你）
```

### 5. 用 Obsidian 浏览

用 Obsidian 打开知识库目录，即可实时浏览 wiki 的图谱视图、反向链接和页面内容。

---

## 目录结构

Skill 安装在全局位置，知识库目录由用户通过 `/wiki init` 创建，可以有多个。

```
~/.claude/skills/wiki/        # Skill（全局安装）
├── SKILL.md                  #   主入口，路由子命令
├── SCHEMA.md                 #   Schema（LLM 页面规范）
├── README.md                 #   本文件
├── IDEA.md                   #   原始设计理念
├── registries.json           #   知识库注册表
├── workflows/                #   各子命令的详细工作流
└── scripts/                  #   辅助脚本（lint.py 等）

~/my-kb/                      # 知识库实例（用户指定路径）
├── raw/                      #   原始素材（只读）
│   ├── assets/               #   图片和附件
│   └── *.md / *.pdf          #   素材文件
└── wiki/                     #   LLM 生成和维护的知识库
    ├── index.md              #   内容索引
    ├── log.md                #   操作日志
    ├── overview.md           #   总览页
    ├── sources/              #   素材摘要页
    ├── entities/             #   实体页
    ├── concepts/             #   概念页
    └── analyses/             #   分析页
```

### 三层架构

| 层 | 位置 | 谁写 | 谁读 | 说明 |
|----|------|------|------|------|
| 原始素材 | `<kb>/raw/` | 你 | LLM | 不可变的信息源，LLM 只读不写 |
| 知识库 | `<kb>/wiki/` | LLM | 你 | LLM 完全拥有，你通过 Obsidian 浏览 |
| 规范 | `~/.claude/skills/wiki/` | 你 + LLM | LLM | Skill 代码、Schema、注册表 |

---

## 核心操作详解

### `/wiki ingest` — 收录素材

将新素材整合进知识库。**默认全自动执行**，仅在需要人工判断时才询问。一次收录可能触发 10-15 个页面的创建或更新。

**流程：**

1. **发现新素材** — 扫描 `raw/` 找出未收录的文件
2. **阅读素材** — 支持 Markdown、PDF、图片
3. **分析与决策** — 自动分析核心要点、识别实体和概念、检查矛盾。常规情况直接执行，仅以下情况询问用户：
   - 新素材与已有内容**矛盾** → 询问处理方式
   - 新概念与已有页面**可能重复** → 询问是否合并
   - 计划创建 **>5 个新页面** → 询问收录范围
4. **创建素材摘要页** — 在 `wiki/sources/` 下生成结构化摘要
5. **创建/更新实体和概念页** — 实体（人物、组织、工具）→ `wiki/entities/`，概念（理论、方法、模式）→ `wiki/concepts/`
6. **维护图谱完整性** — 确保双向链接完整、更新 index.md、overview.md、log.md
7. **确定性检查** — 自动运行 lint.py 脚本，有 P0 问题立即修复

**示例：**
```
> /wiki ingest                        # 自动收录所有新素材
> /wiki ingest paper-attention.pdf    # 指定文件
```

### `/wiki query` — 查询知识库

基于 wiki 中已积累的知识回答问题，而非每次从零推导。

**流程：**

1. **索引定位** — 读取 index.md 找到相关页面
2. **深度阅读** — 读取相关 wiki 页面和原始素材
3. **综合回答** — 带引用的结构化回答
4. **知识复利** — 有价值的回答可保存为 `wiki/analyses/` 下的新页面

**支持的回答格式：**

| 问题类型 | 输出格式 |
|---------|---------|
| 事实查询 | 简短回答 + 引用 |
| 比较分析 | Markdown 表格 |
| 综合论述 | 结构化长文 |
| 时间线 | 按时间排列的列表 |
| 概览 | 层级列表 |
| 汇报分享 | Marp 幻灯片 |
| 数据分析 | matplotlib 图表 |
| 关系梳理 | Obsidian Canvas |

**示例：**
```
> /wiki query Memex 和现代知识管理工具有什么关系？
> /wiki query 对比一下 RAG 和 Wiki 模式的优劣
> 帮我整理一下目前知识库里关于 XX 的所有信息
```

### `/wiki lint` — 健康检查

定期检查 wiki 的健康状况，发现和修复问题。建议每收录 5-10 篇素材后运行一次。

**两层检查机制：**

1. **确定性脚本**（`python ~/.claude/skills/wiki/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw`）— 用代码检测结构性问题，结果 100% 可重复
2. **LLM 语义补充** — 检查脚本无法判断的内容质量问题

**检查项（按优先级）：**

| 级别 | 脚本检查（确定性） | LLM 补充（语义） |
|------|------------------|-----------------|
| P0 | 断链、raw wikilink 误用、Frontmatter 完整性、索引一致性 | — |
| P1 | 双向链接缺失、孤岛页面、sources 字段缺失 | 语言一致性、矛盾检测、缺失页面、陈旧信息 |
| P2 | — | 缺失交叉引用、标签不一致、可合并页面、知识缺口 |

**输出**：结构化报告，P0 建议立即修复，P1 逐项确认，P2 仅作建议。

也可以单独运行脚本快速检查：
```bash
python ~/.claude/skills/wiki/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw          # 人类可读输出
python ~/.claude/skills/wiki/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw --json   # JSON 格式（供程序使用）
```

**示例：**
```
> /wiki lint
> 检查一下 wiki 有没有问题
```

### `/wiki test` — 自动化测试

验证整个系统的完整性：目录结构、ingest 工作流、交叉引用、lint 逻辑。

```
> /wiki test
```

---

## 页面规范

### Frontmatter

每个 wiki 页面都有 YAML 元数据头，兼容 Obsidian Dataview 插件：

```yaml
---
title: 页面标题
aliases: [中文别名]              # Front Matter Title 插件显示用
type: source | entity | concept | analysis
created: 2026-04-13
updated: 2026-04-13
tags: [标签1, 标签2]
sources: [引用的原始素材文件名]
---
```

### 交叉引用

使用 Obsidian 双链语法，确保图谱视图正常：

```markdown
[[page-name]]              # 基本链接
[[page-name|显示文本]]      # 别名链接
```

每个页面底部都有 `## Related` 区块，列出所有相关链接。LLM 负责维护双向引用的完整性。

### 命名规范

- 文件名：小写英文 + 连字符，如 `reinforcement-learning.md`
- 素材摘要页与原始文件同名：`raw/paper-x.pdf` → `wiki/sources/paper-x.md`

---

## 索引与日志

### index.md — 内容索引

wiki 的目录，按类别组织所有页面。LLM 回答查询时先读此文件定位相关页面。

```markdown
## Sources
- [素材标题](sources/filename.md) — 一句话摘要 (日期)

## Entities
- [实体名](entities/filename.md) — 一句话描述 [N 个素材引用]
```

### log.md — 操作日志

按时间倒序记录所有操作，格式统一可解析：

```markdown
## [2026-04-13] ingest | 文章标题
- Pages created: ...
- Pages updated: ...
```

用 grep 快速查看最近操作：
```bash
grep "^## \[" wiki/log.md | head -5
```

---

## Obsidian 配置建议

用 Obsidian 打开知识库目录后，建议做以下配置：

| 配置项     | 设置                                                             |
| ------- | -------------------------------------------------------------- |
| 附件路径    | Settings → Files and links → Attachment folder → `raw/assets/` |
| 下载附件快捷键 | Settings → Hotkeys → "Download attachments" → `Ctrl+Shift+D`   |
| 推荐插件    | Dataview（元数据查询）、Marp Slides（幻灯片）、Web Clipper（网页裁剪）、**Front Matter Title**（图谱/文件列表显示中文标题） |

**Web Clipper** 是快速收录网页文章的利器：浏览器中一键将文章转为 Markdown，保存到 `raw/` 目录，然后 `/wiki ingest` 即可。

### Front Matter Title 插件配置

知识库目录可预置 Front Matter Title 插件配置（`.obsidian/plugins/obsidian-front-matter-title-plugin/data.json`），安装后即可生效。

**作用**：Obsidian 默认用文件名（英文）显示节点和文件列表。此插件读取每个页面 frontmatter 中的 `title` 字段，替换为中文标题显示。

**安装**：Settings → Community plugins → Browse → 搜索 "Front Matter Title" → Install → Enable

**已启用的替换区域**：

| 区域 | 效果 |
|------|------|
| Graph | 图谱节点显示中文标题 |
| Explorer | 左侧文件列表显示中文标题 |
| Tab | 标签页标题显示中文 |
| Search | 搜索结果显示中文标题 |
| Suggest | `[[` 链接建议弹窗显示中文标题 |

**原理**：插件的全局模板 `common.main` 设为 `"title"`，即读取 frontmatter 的 `title` 字段。每个 wiki 页面的 frontmatter 都包含 `title`，因此所有页面都会显示中文标题。如需自定义某个 feature 的模板，可在插件设置中为对应 feature 单独设置 `templates.main`（留空则使用全局模板）。

### 图谱视图配置

打开图谱视图后，建议在左上角搜索栏设置过滤条件，隐藏非知识页面：

```
-file:index -file:log -file:overview
```

其他推荐设置（点击图谱左上角齿轮图标）：
- **Show tags**: 开启，在图谱中显示标签节点
- **Show attachments**: 关闭
- **Show orphans**: 开启，方便发现孤岛页面

---

## Git 版本管理

知识库可以是一个 git 仓库，版本历史是知识演化的天然记录。

- LLM 不会自动 commit，由你决定何时保存版本
- 建议的 commit 时机：每次 ingest 后、lint 修复后
- Commit message 格式：`ingest: 收录 XXX`、`lint: 修复 N 处问题`

---

## 扩展：搜索工具

当前阶段（< 100 页面），index.md + Grep 足够高效。当 wiki 增长后，可集成搜索引擎：

- [qmd](https://github.com/tobi/qmd) — 本地 Markdown 搜索引擎，支持 BM25/向量混合搜索和 LLM 重排，提供 CLI 和 MCP server
- 或在 `.claude/skills/wiki/scripts/` 下自行编写搜索脚本

---

## 适用场景

| 场景 | 说明 |
|------|------|
| 研究 | 持续阅读论文/文章，逐步构建某领域的完整知识图谱 |
| 读书 | 按章节收录，自动构建角色、主题、情节线索的关联网络 |
| 个人成长 | 日记、文章、播客笔记，构建自我认知的结构化图景 |
| 竞品分析 | 持续跟踪竞品动态，自动维护对比分析 |
| 课程笔记 | 逐课收录，自动整理知识体系和概念关联 |
| 团队知识库 | 收录会议纪要、Slack 讨论、项目文档，LLM 自动维护 |
