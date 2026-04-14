# Second Brain Skill

> 把你的第二大脑接入 Claude Code。基于 [Karpathy LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 的理念，将个人知识封装成 Skill，让 AI 成为真正理解你上下文的助手。

传统 RAG 是**解释器**——每次提问都从原始文档重新检索推理。Second Brain Skill 是**编译器**——LLM 预先将素材编译为结构化的 wiki，知识随时间**持续复利增长**。

你负责挑选素材、提出好问题；LLM 负责所有繁重的整理——摘要、交叉引用、归档、一致性维护。

## 演示

![演示：help → init → ingest → query 完整流程](docs/images/guide.gif)

## 三层架构

```
┌──────────────────────────────────────────┐
│  原始素材 (raw/)      ← 你写，LLM 只读    │
│  论文、文章、笔记、PDF、图片                │
├──────────────────────────────────────────┤
│  知识库 (wiki/)       ← LLM 写，你浏览     │
│  摘要、实体、概念、分析、交叉引用            │
├──────────────────────────────────────────┤
│  规范 (Skill)         ← 你和 LLM 共同演进  │
│  SCHEMA、workflows、scripts               │
└──────────────────────────────────────────┘
```

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/ChavesLiu/second-brain-skill.git

# 将 skill 复制到 Claude Code 全局目录
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki

# 安装依赖
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

### 2. 初始化知识库

```
/wiki init
```

按提示选择路径、名称和语言（zh/en），即可创建知识库。

### 3. 收录第一份素材

```bash
# 将素材放入 raw/ 目录
cp my-article.md ~/my-kb/raw/

# 收录
/wiki ingest
```

LLM 自动阅读素材、创建摘要页、拆分实体和概念页、维护交叉引用。一次收录可能触发 10-15 个页面的创建或更新。

### 4. 查询知识

```
/wiki query Memex 是什么？
```

也可以直接用自然语言：

```
对比一下 RAG 和 Wiki 模式的优劣
```

## 核心命令

| 命令 | 功能 |
|------|------|
| `/wiki init` | 创建并注册新知识库 |
| `/wiki ingest` | 收录新素材（支持 Markdown、PDF、图片） |
| `/wiki query <问题>` | 基于知识库回答问题 |
| `/wiki lint` | 知识库健康检查 |
| `/wiki wipe` | 删除/重置（有回收站，可恢复） |
| `/wiki test` | 自动化测试 |

所有命令也支持**自然语言**触发——"收录这篇文章"、"检查下知识库"、"整理 XX 的信息"，LLM 会自动识别意图。

## 自然语言模式

你不需要记住任何命令。Skill 会自动判断你的意图：

| 你说的话 | 执行的操作 |
|---------|-----------|
| "收录这篇文章" | ingest |
| "Memex 是什么？" | query |
| "对比 RAG 和 Wiki 模式" | query |
| "回答要标注来源" | 记录偏好到 conventions.md |
| "检查下知识库" | lint |

这在 Web 端（OpenClaw）中体验尤其好——像聊天一样操作知识库。

## Obsidian 集成

用 [Obsidian](https://obsidian.md/) 打开知识库目录，即可实时浏览图谱视图、反向链接和页面内容。推荐插件：

- **Front Matter Title** — 图谱节点显示中文标题（项目已预置配置）
- **Dataview** — 基于 frontmatter 的元数据查询
- **Web Clipper** — 浏览器一键裁剪网页文章到 raw/

## OpenClaw（Web 端）

在 OpenClaw 记忆中配置知识库路径后，可以实现**零摩擦收录**——发一个微信公众号链接，LLM 自动下载、收录、整理，全程无需额外指令。

![OpenClaw 自动收录演示](docs/images/openclaw-wiki.gif)

详见 [使用手册 — 接入 OpenClaw](docs/user-guide.md#接入-openclawclaude-code-web)。

## 知识库目录结构

```
~/my-kb/                        # 知识库实例
├── raw/                        #   原始素材（你写入，LLM 只读）
│   ├── assets/                 #     图片和附件
│   └── *.md / *.pdf            #     素材文件
└── wiki/                       #   LLM 生成和维护的知识库
    ├── index.md                #     内容索引
    ├── log.md                  #     操作日志
    ├── overview.md             #     总览页
    ├── conventions.md          #     使用约定（你的操作偏好）
    ├── sources/                #     素材摘要页
    ├── entities/               #     实体页（人物、组织、工具）
    ├── concepts/               #     概念页（理论、方法、模式）
    └── analyses/               #     分析页（对比、综合论述）
```

## 适用场景

- **研究** — 持续阅读论文，逐步构建领域知识图谱
- **读书** — 按章节收录，自动构建角色、主题、情节的关联网络
- **个人成长** — 日记、文章、播客笔记，构建自我认知的结构化图景
- **竞品分析** — 持续跟踪竞品动态，自动维护对比分析
- **团队知识库** — 收录会议纪要、项目文档，LLM 自动维护

## 文档

- **[使用手册](docs/user-guide.md)** — 完整的安装配置、功能详解、Obsidian 集成、OpenClaw 接入
- **[设计理念](skills/wiki/IDEA.md)** — Karpathy LLM Wiki 的原始构想
- **[Skill 技术文档](skills/wiki/README.md)** — 页面规范、工作流详解、目录结构

## 致谢

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — LLM Wiki 的原始理念
- [Vannevar Bush](https://en.wikipedia.org/wiki/Vannevar_Bush) — 1945 年提出 Memex 构想，个人知识管理的思想源头

## License

MIT
