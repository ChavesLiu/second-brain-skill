# Second Brain Skill 使用手册

> 把你的第二大脑接入 Claude Code。基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 的理念，将个人知识封装成 Skill，让 AI 成为真正理解你上下文的助手。

**项目地址**: [github.com/ChavesLiu/second-brain-skill](https://github.com/ChavesLiu/second-brain-skill)

---

## 目录

- [核心理念](#核心理念)
- [环境准备](#环境准备)
- [安装 Skill](#安装-skill)
- [初始化知识库](#初始化知识库)
- [核心功能](#核心功能)
  - [收录素材 — /wiki ingest](#收录素材--wiki-ingest)
  - [查询知识 — /wiki query](#查询知识--wiki-query)
  - [健康检查 — /wiki lint](#健康检查--wiki-lint)
  - [删除与重置 — /wiki wipe](#删除与重置--wiki-wipe)
  - [自动化测试 — /wiki test](#自动化测试--wiki-test)
- [自然语言交互](#自然语言交互)
- [Obsidian 集成](#obsidian-集成)
- [接入 OpenClaw](#接入-openclaw)
- [多知识库管理](#多知识库管理)
- [适用场景](#适用场景)
- [FAQ](#faq)

---

## 核心理念

传统 RAG 是**解释器**——每次提问都从原始文档中重新检索、拼接、推理。Second Brain Skill 是**编译器**——LLM 预先将素材编译为结构化的 wiki，后续查询基于编译产物进行，知识随时间**持续复利增长**。

### 三层架构

```
┌────────────────────────────────────────────────┐
│  原始素材 (raw/)         ← 你写，LLM 只读       │
│  论文、文章、笔记、PDF、图片                      │
├────────────────────────────────────────────────┤
│  知识库 (wiki/)          ← LLM 写，你浏览        │
│  摘要、实体、概念、分析、交叉引用                  │
├────────────────────────────────────────────────┤
│  规范 (Skill)            ← 你和 LLM 共同演进     │
│  SCHEMA、workflows、scripts                     │
└────────────────────────────────────────────────┘
```

你负责挑选素材、提出好问题、思考洞见；LLM 负责所有繁重的整理工作——摘要、交叉引用、归档、一致性维护。

---

## 环境准备

### 必需

| 工具 | 说明 | 安装方式 |
|------|------|---------|
| **Claude Code** | Anthropic 官方 CLI 工具 | `npm install -g @anthropic-ai/claude-code` |
| **Python 3.10+** | 运行辅助脚本（router.py、lint.py） | 系统自带或 brew install python |
| **PyYAML** | lint.py 的依赖 | `pip install PyYAML` |

### 推荐

| 工具 | 说明 |
|------|------|
| **Obsidian** | 用于浏览 wiki 的图谱视图、反向链接和页面内容 |
| **Obsidian Web Clipper** | 浏览器扩展，一键将网页文章转为 Markdown 存入 raw/ |
| **Git** | 版本管理，知识库的演化历史天然记录在 git 中 |

---

## 安装 Skill

### 方式一：从 GitHub 克隆安装（推荐）

```bash
# 1. 克隆仓库
git clone https://github.com/ChavesLiu/second-brain-skill.git

# 2. 将 skill 目录复制到 Claude Code 全局 skills 目录
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki

# 3. 安装 Python 依赖
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

### 方式二：手动安装

下载仓库中的 `skills/wiki/` 目录，放置到 `~/.claude/skills/wiki/` 下即可。

### 验证安装

安装完成后，在 Claude Code 中输入：

```
/wiki help
```

如果看到命令列表，说明安装成功。

### 演示：从安装到首次使用

以下演示涵盖 `/wiki help` → `/wiki init` → `/wiki ingest` → `/wiki query` 的完整流程：

![演示：help → init → ingest → query 完整流程](images/guide.gif)

### 安装后的目录结构

```
~/.claude/skills/wiki/          # Skill 安装目录
├── SKILL.md                    #   主入口，路由逻辑
├── SCHEMA.md                   #   页面规范（frontmatter、交叉引用）
├── README.md                   #   Skill 说明
├── IDEA.md                     #   原始设计理念
├── registries.json             #   知识库注册表
├── workflows/                  #   各子命令的工作流定义
│   ├── init.md
│   ├── ingest.md
│   ├── query.md
│   ├── lint.md
│   ├── wipe.md
│   └── test.md
└── scripts/                    #   辅助脚本
    ├── router.py               #     确定性路由
    ├── lint.py                 #     确定性健康检查
    └── requirements.txt        #     Python 依赖
```

---

## 初始化知识库

运行以下命令创建你的第一个知识库：

```
/wiki init
```

Claude Code 会依次询问三个问题：

1. **知识库路径** — 将在此路径下创建 `raw/` 和 `wiki/` 子目录
2. **知识库名称** — 用于多知识库切换时的显示名称
3. **Wiki 语言** — `zh`（中文）或 `en`（English）


初始化完成后，你会得到如下目录结构：

```
~/my-kb/                        # 你指定的知识库路径
├── raw/                        #   存放原始素材（你写入，LLM 只读）
│   └── assets/                 #     图片和附件
└── wiki/                       #   LLM 生成和维护的知识库
    ├── index.md                #     内容索引（LLM 查询入口）
    ├── log.md                  #     操作日志（时间线）
    ├── overview.md             #     总览页（统计 + 知识图谱摘要）
    ├── conventions.md          #     使用约定（你的操作偏好）
    ├── sources/                #     素材摘要页
    ├── entities/               #     实体页（人物、组织、工具）
    ├── concepts/               #     概念页（理论、方法、模式）
    └── analyses/               #     分析页（对比、综合论述）
```

---

## 核心功能

### 收录素材 — `/wiki ingest`

这是知识库成长的核心操作。将新素材整合进知识库，一次收录可能触发 10-15 个页面的创建或更新。

#### 使用方式

```
/wiki ingest                        # 自动收录 raw/ 下所有新素材
/wiki ingest paper-attention.pdf    # 指定收录某个文件
```

#### 工作流程

```
  放入素材            LLM 阅读            自动分析            创建/更新页面
┌─────────┐      ┌───────────┐      ┌──────────────┐      ┌──────────────┐
│ raw/    │  →  │ Markdown  │  →  │ 核心要点     │  →  │ sources/     │
│ 文章.md │      │ PDF       │      │ 识别实体     │      │ entities/    │
│ 论文.pdf│      │ 图片      │      │ 识别概念     │      │ concepts/    │
└─────────┘      └───────────┘      │ 检查矛盾     │      │ index.md     │
                                    └──────────────┘      │ overview.md  │
                                                          │ log.md       │
                                                          └──────────────┘
```

#### 操作步骤

1. 将素材文件放入知识库的 `raw/` 目录（支持 Markdown、PDF、图片）
2. 执行 `/wiki ingest`
3. LLM 自动完成以下工作：
   - 阅读素材，提取核心要点
   - 创建素材摘要页（`wiki/sources/`）
   - 创建或更新实体页（`wiki/entities/`）和概念页（`wiki/concepts/`）
   - 维护双向交叉引用，确保图谱完整性
   - 更新 `index.md`、`overview.md`、`log.md`
   - 运行 lint 脚本检查，P0 问题自动修复

#### 何时需要人工介入

大多数情况下 ingest 全自动完成。仅以下场景会询问你：

| 场景 | 说明 |
|------|------|
| **内容矛盾** | 新素材与已有 wiki 内容冲突 → 选择保留双方/以新为准/保留旧 |
| **合并歧义** | 不确定新概念是否应与已有页面合并 → 选择合并/独立/重命名 |
| **大规模收录** | 计划创建 >5 个新页面 → 选择全部收录/仅核心/仅摘要 |

---

### 查询知识 — `/wiki query`

基于 wiki 中已编译的知识回答问题。核心理念：**每次查询都让知识库变得更好**。

#### 使用方式

```
/wiki query Memex 是什么？
/wiki query 对比一下 RAG 和 Wiki 模式的优劣
帮我整理一下目前知识库里关于强化学习的信息
```

#### 回答格式

LLM 会根据问题类型自动选择最佳输出格式：

| 问题类型 | 输出格式 | 示例 |
|---------|---------|------|
| 事实查询 | 简短回答 + 引用 | "Memex 是什么？" |
| 比较分析 | Markdown 表格 | "对比 RAG 和 Wiki 模式" |
| 综合论述 | 结构化长文 | "梳理知识管理的发展脉络" |
| 时间线 | 按时间排列的列表 | "XX 领域的发展时间线" |
| 概览 | 层级列表 | "整理 XX 的所有信息" |
| 汇报分享 | Marp 幻灯片 | "生成一个关于 XX 的 PPT" |
| 数据分析 | matplotlib 图表 | "对比各模型的性能数据" |
| 关系梳理 | Obsidian Canvas | "画出 XX 之间的关系" |

#### 知识回写机制

查询完成后，LLM 会评估回答是否产生了新知识：

- **自动回写**（不需确认）：补充已有页面的缺失信息、新增交叉引用、修正小错误
- **建议回写**（需确认）：将有价值的分析保存为 `wiki/analyses/` 下的新页面、创建新实体/概念页

```
📝 本次查询产生了以下知识更新：

自动更新:
  - 更新了 [[memex]] 页面，补充了与现代 RAG 系统的对比
  - 在 [[vannevar-bush]] 和 [[knowledge-management]] 之间添加了交叉引用

建议操作:
  - 💡 将本次对比分析保存为 wiki/analyses/memex-vs-rag.md？
```

#### 反馈与偏好

你也可以通过 query 通道告诉 LLM 你的操作偏好：

```
回答时要标注来源
比较类问题用表格
一笔带过的概念不要建独立页
```

这些偏好会被记录到 `wiki/conventions.md`，后续所有操作自动遵守。

---

### 健康检查 — `/wiki lint`

定期检查 wiki 的健康状况，发现和修复问题。建议每收录 5-10 篇素材后运行一次。

#### 使用方式

```
/wiki lint
```

#### 两层检查机制

| 层 | 工具 | 检查内容 |
|----|------|---------|
| **确定性脚本** | `lint.py` | 断链、raw wikilink 误用、frontmatter 完整性、索引一致性、双向链接、孤岛页面、sources 字段 |
| **LLM 语义补充** | Claude | 语言一致性、矛盾检测、缺失页面、陈旧信息、缺失交叉引用、标签不一致、知识扩展建议 |

#### 问题优先级

| 级别 | 含义 | 处理方式 |
|------|------|---------|
| 🔴 **P0** | 结构性错误，影响知识图谱完整性 | 建议立即修复 |
| 🟡 **P1** | 质量问题，影响知识准确性 | 逐项确认 |
| 🟢 **P2** | 优化建议，提升知识库深度 | 仅作建议 |

#### 输出示例

```
## Wiki 健康检查报告 (2026-04-14)

### 📊 统计
- 总页面数: 15
- 素材摘要: 5  |  实体页面: 4  |  概念页面: 5  |  分析页面: 1

### 🔴 P0 — 需要修复
- [ ] [broken_link] concepts/rag.md: [[llm-training]] 指向不存在的页面

### 🟡 P1 — 建议改进
- [ ] [orphan_page] entities/ted-nelson.md: 孤岛页面，没有其他页面链接到此

### 🟢 P2 — 可选优化
- [ ] 建议为 "RAG" 创建独立概念页（被 3 个页面引用但无独立页）

🔍 知识扩展建议（基于 web search）:
- [[memex]] 页面提到了 Ted Nelson 但无详细内容
  → 推荐: "Ted Nelson and the Xanadu Project"
  → 优先级: 中
```

也可以单独运行脚本做快速检查：

```bash
# 人类可读输出
python ~/.claude/skills/wiki/scripts/lint.py \
  --wiki-dir ~/my-kb/wiki --raw-dir ~/my-kb/raw

# JSON 格式（供程序使用）
python ~/.claude/skills/wiki/scripts/lint.py \
  --wiki-dir ~/my-kb/wiki --raw-dir ~/my-kb/raw --json
```

---

### 删除与重置 — `/wiki wipe`

所有删除操作均有回收站机制，可恢复。原始素材（`raw/`）永远不会被动。

#### 使用方式

| 命令 | 功能 |
|------|------|
| `/wiki wipe` | 交互式选择操作 |
| `/wiki wipe all` | 全量重置（所有页面移入回收站） |
| `/wiki wipe <关键词>` | 删除匹配的页面 |
| `/wiki wipe trash` | 查看回收站内容 |
| `/wiki wipe restore` | 从回收站恢复页面 |
| `/wiki wipe empty-trash` | 永久清空回收站（不可逆） |

#### 回收站机制

- 删除 = 移入 `wiki/.trash/`，按原目录结构存放
- 例如：`wiki/concepts/swiglu.md` → `wiki/.trash/concepts/swiglu.md`
- 恢复时自动移回原路径，并重新更新 index.md 和关联页面的链接
- 永久清空（`empty-trash`）后只能通过 git 恢复

---

### 自动化测试 — `/wiki test`

验证整个系统的完整性。

```
/wiki test
```

测试覆盖四个维度：

| 测试项 | 验证内容 |
|--------|---------|
| 架构完整性 | 目录结构、核心文件是否完整 |
| Ingest 工作流 | 使用测试素材跑通完整 ingest 流程 |
| Query 工作流 | 查询能否正确引用 wiki 页面 |
| Lint 工作流 | 健康检查能否生成结构化报告 |

---

## 自然语言交互

你**不需要记住任何命令**。Second Brain Skill 支持完全用自然语言操作——像和一个懂你知识库的助手对话一样。LLM 会自动判断你的意图，路由到对应的工作流。

### 意图识别

| 你说的话 | LLM 理解为 | 实际执行 |
|---------|-----------|---------|
| "收录这篇文章" | 收录素材 | → `ingest` 工作流 |
| "把 raw 里的新文件加到知识库" | 收录素材 | → `ingest` 工作流 |
| "Memex 是什么？" | 知识查询 | → `query` 工作流 |
| "对比 RAG 和 Wiki 模式的优劣" | 知识查询 | → `query` 工作流 |
| "整理一下目前关于强化学习的信息" | 知识查询 | → `query` 工作流 |
| "回答要标注来源" | 操作偏好 | → 写入 `conventions.md` |
| "你上次说错了，其实是 XX" | 内容纠正 | → 修正对应 wiki 页面 |
| "检查下知识库有没有问题" | 健康检查 | → `lint` 工作流 |
| "删掉 XX 相关的页面" | 删除内容 | → `wipe` 工作流 |

### 两种使用模式

| 模式 | 适用场景 | 示例 |
|------|---------|------|
| **命令模式** `/wiki <cmd>` | 明确知道要做什么操作 | `/wiki ingest`、`/wiki lint` |
| **自然语言模式** | 日常使用，像对话一样交互 | "这篇论文讲了什么？"、"帮我整理一下 XX" |

两种模式效果完全一致，自然语言模式更适合日常使用——尤其是在 **Web 端（OpenClaw）** 中，自然语言交互体验更好，无需记忆命令格式。

### 反馈即进化

自然语言模式的一个重要特性是**反馈回写**。你对 LLM 操作方式的任何偏好，都会被自动记录到 `wiki/conventions.md`，后续所有操作自动遵守：

```
你："比较类问题用表格"
→ 记录到 conventions.md 的 Query 分类下

你："一笔带过的概念不要建独立页"
→ 记录到 conventions.md 的 Ingest 分类下
```

知识库会随着你的使用越来越懂你的习惯。

---

## Obsidian 集成

Obsidian 是浏览和可视化 wiki 的最佳伴侣。LLM 在 Claude Code 中维护知识库，你在 Obsidian 中实时浏览结果。

### 基础配置

1. 用 Obsidian 打开知识库根目录（如 `~/my-kb/`）
2. 进行以下推荐配置：

| 配置项 | 设置 |
|--------|------|
| 附件路径 | Settings → Files and links → Attachment folder → `raw/assets/` |
| 下载附件快捷键 | Settings → Hotkeys → "Download attachments" → `Ctrl+Shift+D` |

### 推荐插件

| 插件 | 用途 | 必要性 |
|------|------|--------|
| **Front Matter Title** | 图谱和文件列表中显示中文标题（而非英文文件名） | 强烈推荐 |
| **Dataview** | 基于 frontmatter 的元数据查询 | 推荐 |
| **Web Clipper** | 浏览器中一键将网页裁剪为 Markdown | 推荐 |
| **Marp Slides** | 浏览 LLM 生成的幻灯片 | 可选 |

### Front Matter Title 插件

项目已预置了 Front Matter Title 插件的配置文件。安装插件后即可生效：

**安装**：Settings → Community plugins → Browse → 搜索 "Front Matter Title" → Install → Enable

**效果**：Obsidian 默认用英文文件名显示节点。插件会读取每个页面 frontmatter 中的 `title` 字段，替换为中文标题。

| 替换区域 | 效果 |
|---------|------|
| Graph | 图谱节点显示中文标题 |
| Explorer | 左侧文件列表显示中文标题 |
| Tab | 标签页标题显示中文 |
| Search | 搜索结果显示中文标题 |
| Suggest | `[[` 链接建议弹窗显示中文标题 |

### 图谱视图配置

打开图谱视图后，建议在左上角搜索栏设置过滤条件，隐藏辅助页面：

```
-file:index -file:log -file:overview
```

其他推荐设置（点击图谱左上角齿轮图标）：
- **Show tags**: 开启（在图谱中显示标签节点）
- **Show attachments**: 关闭
- **Show orphans**: 开启（方便发现孤岛页面）

### Web Clipper 收录流程

1. 在浏览器中安装 Obsidian Web Clipper 扩展
2. 浏览到想收录的文章，点击 Web Clipper 图标
3. 选择保存到知识库的 `raw/` 目录
4. （可选）按 `Ctrl+Shift+D` 下载文章中的图片到 `raw/assets/`
5. 回到 Claude Code 执行 `/wiki ingest`

---

## 接入 OpenClaw

[OpenClaw](https://github.com/openclaw/openclaw) ，实现跨设备的知识库管理。

**OpenClaw 是自然语言模式的最佳搭档**——有很多通道可接入，实现对话自由，体验天然适合自然语言交互，你无需记忆任何命令，像和助手聊天一样操作知识库。

### 前提条件

- 已在本地安装好 Skill 并初始化知识库
- 知识库目录通过 Git 同步或云盘同步到 OpenClaw 可访问的环境

### 配置步骤

1. **确保 Skill 文件就位**：OpenClaw 环境中的 `~/.openclaw/workspace/skills/` 目录需要包含完整的 Skill 文件
2. **同步知识库**：将知识库目录（含 `raw/` 和 `wiki/`）同步到 OpenClaw 可访问的路径
3. **更新注册表**：如果路径有变化，修改 `~/.openclaw/workspace/skills/wiki/registries.json` 中的知识库路径
4. **验证**：在 OpenClaw 中执行 `/wiki help` 确认 Skill 正常加载

### 使用方式

命令模式和自然语言模式均可使用：

**命令模式**（与本地 CLI 一致）：

```
/wiki ingest
/wiki query Memex 是什么？
/wiki lint
```

**自然语言模式**（推荐，更贴合 Web 端交互体验）：

```
收录 raw 里的新文章
Memex 和现代知识管理有什么关系？
对比一下 RAG 和 Wiki 模式的优劣
帮我整理一下目前知识库里关于 XX 的信息
检查下知识库有没有问题
```

在 Web 端，你可以像日常聊天一样与知识库交互——提问、收录、纠错、设置偏好，LLM 都能自动识别意图并执行。

### 进阶：配置记忆实现自动收录

通过在 OpenClaw 的记忆（Memory）中写入知识库配置，可以让 LLM **自动识别你发来的素材并收录**——甚至不需要你手动输入任何命令。

#### 配置方法

在 OpenClaw 的记忆中添加以下内容：

```
- 学习知识库：~/Documents/knowledge-wiki，ID: learning-kb，语言: zh
- 用户发来的前沿知识文章/论文/资料 → 直接存入 ~/Documents/knowledge-wiki/raw/
- 用户发来微信公众号链接 → 自动 playwright pdf 下载 + 自动 ingest，不用等用户指令
- /wiki ingest 时统一收录进知识库（也可手动触发）
- Wiki 技能路径：~/.openclaw/workspace/skills/wiki/
```

#### 效果

![OpenClaw 自动收录：发链接即入库](images/openclaw-wiki.gif)

配置完成后，你的使用方式可以极其简单：

**发一个微信公众号链接**：

```
https://mp.weixin.qq.com/s/xxxxxxx
```

LLM 会自动完成整个流水线：

```
检测到微信公众号链接
  → Playwright 打开链接，导出为 PDF
  → 保存到 ~/Documents/knowledge-wiki/raw/
  → 自动执行 /wiki ingest
  → 创建摘要页、实体页、概念页
  → 更新索引和图谱
✅ 收录完成
```

**发一篇文章或论文**：

```
这篇论文讲了一种新的注意力机制：[粘贴内容或文件]
```

LLM 自动存入 `raw/` 并触发 ingest，全程无需额外指令。

#### 典型工作流

```
你（在手机/电脑上看到好文章）
  → 复制链接，发给 OpenClaw
  → LLM 自动下载、收录、整理
  → 下次你问相关问题时，知识已经在库里了
```

这让知识库的喂养变得零摩擦——看到好内容，随手丢给 OpenClaw 就行。

---

## 多知识库管理

Second Brain Skill 支持管理多个知识库，通过 `registries.json` 统一注册。

### 创建多个知识库

```
/wiki init    # 第一次：创建 "AI 研究" 知识库
/wiki init    # 第二次：创建 "读书笔记" 知识库
```

### 切换知识库

当存在多个知识库时：

- **有默认库**：操作自动使用默认库，并提示可切换
- **无默认库**：每次操作前询问使用哪个知识库

### registries.json 格式

```json
{
  "default": "ai-research",
  "registries": {
    "ai-research": {
      "name": "AI 研究",
      "path": "/Users/you/knowledge/ai-research",
      "language": "zh",
      "created": "2026-04-13"
    },
    "book-notes": {
      "name": "读书笔记",
      "path": "/Users/you/knowledge/book-notes",
      "language": "zh",
      "created": "2026-04-14"
    }
  }
}
```

修改 `"default"` 字段即可切换默认知识库。

---

## 适用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| **研究** | 持续阅读论文/文章，逐步构建某领域的完整知识图谱 | 收录 AI 论文，自动追踪技术演进、对比不同方法 |
| **读书** | 按章节收录，自动构建角色、主题、情节线索的关联网络 | 读《指环王》，LLM 自动维护人物关系和事件时间线 |
| **个人成长** | 日记、文章、播客笔记，构建自我认知的结构化图景 | 收录心理学文章、播客摘要，追踪个人发展主题 |
| **竞品分析** | 持续跟踪竞品动态，自动维护对比分析 | 收录竞品发布、报告，自动更新对比表格 |
| **课程笔记** | 逐课收录，自动整理知识体系和概念关联 | 大学课程笔记，LLM 自动整理知识脉络 |
| **团队知识库** | 收录会议纪要、项目文档，LLM 自动维护 | 团队共享 git 仓库，LLM 帮助整理和检索 |

---

## FAQ

### Q: 知识库可以有多大？

当前架构在 ~100 个素材、~数百个 wiki 页面的规模下表现良好。`index.md` 配合 Grep 搜索足够高效。如果超过这个规模，建议集成 qmd 等搜索工具。

### Q: 支持哪些素材格式？

- **Markdown** (`.md`) — 直接读取
- **PDF** (`.pdf`) — 通过 Read 工具读取
- **图片** (`.png`, `.jpg` 等) — 通过 Read 工具查看（LLM 原生多模态能力）

### Q: wiki 页面可以手动编辑吗？

可以，但不建议。wiki 层由 LLM 完全管理。如果你想纠正内容，通过 `/wiki query` 告诉 LLM 哪里不对，它会自动更新相关页面。如果你想修改操作方式，告诉 LLM 你的偏好，它会记录到 `conventions.md`。

### Q: 如何备份知识库？

知识库就是一个目录下的 Markdown 文件，最佳实践是用 Git 管理：

```bash
cd ~/my-kb
git init
git add -A
git commit -m "ingest: 收录 XX"
```

建议的 commit 时机：每次 ingest 后、lint 修复后。

### Q: 可以在 ChatGPT / Codex 上使用吗？

核心理念是通用的（参见 [IDEA.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)）。但本项目的 Skill 实现是为 Claude Code 定制的。如果要用于其他 LLM 平台，需要将 Skill 逻辑适配为对应平台的 Agent 规范（如 OpenAI Codex 的 AGENTS.md）。

### Q: 收录新素材后，Obsidian 多久能看到变化？

实时。LLM 在 Claude Code 中创建/编辑文件时，Obsidian 会自动检测到文件系统变化并刷新显示。你可以把 Claude Code 放一边、Obsidian 放一边，实时观察知识库的成长。

### Q: 如何查看知识库的操作历史？

两种方式：

1. 在 Obsidian 中打开 `wiki/log.md`，查看完整的操作日志
2. 用命令行快速查看最近操作：
   ```bash
   grep "^## \[" ~/my-kb/wiki/log.md | head -5
   ```

---

## 页面规范速查

### Frontmatter 模板

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

### 文件命名规范

- 全部使用小写英文 + 连字符：`reinforcement-learning.md`
- 素材摘要页与原始文件同名：`raw/paper-x.pdf` → `wiki/sources/paper-x.md`
- 文件名控制在 50 字符以内

### 交叉引用语法

```markdown
[[page-name]]              # 基本链接
[[page-name|显示文本]]      # 别名链接
```

- 每个页面底部设 `## Related` 区块
- LLM 自动维护双向链接的完整性
- 原始素材链接使用普通 Markdown 语法 `[text](path)`，不用 `[[wikilink]]`

---

> 本手册随项目更新持续完善。反馈和建议请提交到 [GitHub Issues](https://github.com/ChavesLiu/second-brain-skill/issues)。
