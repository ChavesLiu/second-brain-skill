<div align="center">

<h1>🧠 Second Brain Skill</h1>

<p><strong>构建属于你的 AI 第二大脑</strong></p>

<p>
  灵感来自 <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">Karpathy 的 LLM Wiki</a>。<br>
  一个轻量、可扩展的基础框架，让知识库持续积累、关联与演进。
</p>

<p>
  <a href="https://github.com/ChavesLiu/second-brain-skill/stargazers"><img src="https://img.shields.io/github/stars/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/ChavesLiu/second-brain-skill/network/members"><img src="https://img.shields.io/github/forks/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHub Forks"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=flat-square" alt="Claude Code Skill">
</p>

<p>
  <strong>中文</strong> |
  <a href="README.en.md">English</a> |
  <a href="docs/i18n/README.ja.md">日本語</a> |
  <a href="docs/i18n/README.es.md">Español</a> |
  <a href="docs/i18n/README.fr.md">Français</a> |
  <a href="docs/i18n/README.ko.md">한국어</a> |
  <a href="docs/user-guide.md">使用文档</a>
</p>

</div>

---

## 项目简介

**Second Brain Skill** 是一个受 Andrej Karpathy [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 理念启发的开源实现。

它将零散的个人知识转化为**结构化、相互关联、持续演进的 Wiki**，让 AI 助手能够更好地理解并利用你长期积累的上下文。

项目提供一套**简洁、可运行、易扩展的基础框架**，方便开发者快速 Fork、定制，并构建属于自己的第二大脑。

### 从信息检索到知识积累

**传统 RAG 更像解释器；Second Brain Skill 则采用类似编译器的思路。**

传统 RAG 主要在查询时检索相关信息，而 Second Brain Skill 借助 LLM，将原始素材逐步整理为结构化 Wiki，持续维护素材、实体和概念之间的关联。

知识不再只是每次提问时被临时检索和理解，而是能够不断组织、连接和完善。

**RAG 检索知识，LLM Wiki 积累知识。**

你负责挑选素材、提出好问题；LLM 负责繁重的整理工作——摘要、交叉引用、归档和一致性维护。

## 演示

看看原始素材如何逐步转化为结构化、相互关联的知识库。

![演示：help → init → ingest → query 完整流程](docs/images/guide.gif)

## 三层架构

Second Brain Skill 将原始素材、结构化知识和运行规范划分为三个层次。

| 层 | 位置 | 谁写 | 谁读 | 包含内容 |
|:--:|------|:----:|:----:|----------|
| **原始素材** | `raw/` | 你 | LLM | 论文、文章、笔记、PDF、图片 |
| **知识库** | `wiki/` | LLM | 你 | 摘要、实体、概念、分析、交叉引用 |
| **规范** | `Skill` | 共同演进 | LLM | SCHEMA、workflows、scripts |

这种分层设计既能保留原始素材，又能让知识库和运行规范独立演进。

## 快速开始

### 1. 安装

```bash
# 克隆仓库
git clone https://github.com/ChavesLiu/second-brain-skill.git

# 将 Skill 复制到 Claude Code 全局目录
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki

# 安装依赖
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

### 2. 初始化知识库

```text
/wiki init
```

按提示选择知识库路径、名称和内容语言，即可创建知识库。当前初始化工作流定义的 Wiki 内容语言为 `zh`（中文）和 `en`（英文）；README 的翻译版本不代表新增知识库生成语言支持。

### 3. 收录第一份素材

```bash
# 将素材放入 raw/ 目录
cp my-article.md ~/my-kb/raw/
```

然后执行：

```text
/wiki ingest
```

LLM 自动阅读素材、生成摘要页、提取实体和概念，并维护交叉引用。

根据素材内容，一次收录可能创建或更新 10–15 个相互关联的 Wiki 页面。

### 4. 查询知识

```text
/wiki query Memex 是什么？
```

也可以直接用自然语言提问：

```text
对比一下 RAG 和 Wiki 模式的优劣
```

LLM 会基于已积累的知识库回答问题，并关联相关信息。

## 核心命令

| 命令 | 功能 |
|------|------|
| `/wiki help` | 查看命令列表和使用说明 |
| `/wiki init` | 创建并注册新知识库 |
| `/wiki ingest` | 收录新素材（支持 Markdown、PDF、图片） |
| `/wiki query <问题>` | 基于知识库回答问题 |
| `/wiki lint` | 检查知识库健康状态和一致性 |
| `/wiki wipe` | 删除或重置 Wiki 内容页面（移入 `wiki/.trash/`，不修改 `raw/`） |
| `/wiki test` | 运行自动化测试 |

删除或重置的内容页面可用 `/wiki wipe restore` 恢复；`/wiki wipe empty-trash` 会永久清空回收站，之后只有已纳入 Git 历史的内容才能通过 Git 恢复。

所有命令也支持**自然语言触发**。

例如，直接说“收录这篇文章”“检查下知识库”或“整理 XX 的信息”，无需记忆具体命令。

## 自然语言模式

你不需要记住任何命令。Skill 会自动识别意图并执行对应工作流。

| 你说的话 | 执行的操作 |
|---------|-----------|
| “收录这篇文章” | 收录素材 |
| “Memex 是什么？” | 查询知识库 |
| “对比 RAG 和 Wiki 模式” | 检索并综合相关知识 |
| “回答要标注来源” | 将偏好记录到 `conventions.md` |
| “检查下知识库” | 执行知识库健康检查 |

这种方式也适用于 OpenClaw 等对话式交互界面，让你像聊天一样操作知识库。

## Obsidian 集成

Second Brain Skill 生成基于 Markdown 的知识库，可以直接使用 [Obsidian](https://obsidian.md/) 打开。

你可以探索：

- **知识图谱** — 可视化实体与概念之间的关系。
- **反向链接** — 在相互关联的知识页面间快速跳转。
- **结构化笔记** — 浏览摘要、分析和素材引用。

![Obsidian 知识图谱视图](docs/images/obsidian.png)

推荐插件：

- **Front Matter Title** — 图谱节点显示中文标题（项目已预置配置）。
- **Dataview** — 基于 frontmatter 查询元数据。
- **Web Clipper** — 将网页文章一键裁剪到 `raw/`。

## OpenClaw（Web 端）

Second Brain Skill 也可以与 OpenClaw 集成，实现对话式知识管理。

让 OpenClaw 能访问 Skill 和知识库，并在 Memory 中配置知识库路径及自动收录规则后，可以通过对话收录素材，无需每次输入命令。

例如，发送一个微信公众号文章链接；如果 OpenClaw 环境具备所需的浏览器或下载工具（如 Playwright），LLM 可以尝试下载内容、保存到 `raw/` 并执行收录。这需要额外配置，并非只设置知识库路径就能开箱即用。

![OpenClaw 自动收录演示](docs/images/openclaw-wiki.gif)

详见 [使用手册 — 接入 OpenClaw](docs/user-guide.md#接入-openclaw)。

## 知识库目录结构

```text
~/my-kb/                        # 知识库实例
├── raw/                        # 原始素材（你写入，LLM 只读）
│   ├── assets/                 # 图片和附件
│   └── *.md / *.pdf            # 素材文件
└── wiki/                       # LLM 生成和维护的知识库
    ├── index.md                # 内容索引
    ├── log.md                  # 操作日志
    ├── overview.md             # 总览页
    ├── conventions.md          # 使用约定和偏好
    ├── sources/                # 素材摘要页
    ├── entities/               # 实体页（人物、组织、工具）
    ├── concepts/               # 概念页（理论、方法、模式）
    └── analyses/               # 分析页（对比、综合论述）
```

## 适用场景

- **研究** — 持续收录论文，逐步构建相互关联的领域知识库。
- **读书** — 按章节处理书籍，自动关联人物、主题和概念。
- **个人成长** — 整理日记、文章和播客笔记，构建结构化的个人知识图景。
- **竞品分析** — 持续跟踪竞品动态，维护不断演进的对比与分析。
- **团队知识库** — 收录会议纪要和项目文档，由 LLM 维护结构化知识。

## Fork 并构建自己的版本

Second Brain Skill 的定位是一个**起点，而不是最终产品**。

项目希望降低 Karpathy LLM Wiki 理念的实践门槛，让更多开发者能够轻松探索、实验和扩展。

你可以 Fork 本仓库，根据自己的需求调整知识结构、工作流和使用规范。

无论是个人研究助手、垂直领域知识库，还是团队知识系统，都可以从这个基础框架开始构建。

**Fork、定制，打造属于自己的第二大脑。**

欢迎反馈、贡献代码和分享新的想法！

## 文档

- **[使用手册](docs/user-guide.md)** — 安装配置、功能详解、Obsidian 集成及 OpenClaw 接入。
- **[设计理念](skills/wiki/IDEA.md)** — 受 Karpathy LLM Wiki 启发的背景与设计原则。
- **[Skill 技术文档](skills/wiki/README.md)** — 页面规范、工作流和目录结构。

## 致谢

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — 提出启发本项目的 LLM Wiki 理念。
- [Vannevar Bush](https://en.wikipedia.org/wiki/Vannevar_Bush) — 于 1945 年提出 Memex 构想，是关联式个人知识管理的重要思想源头。

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=chavesliu/second-brain-skill&type=date&legend=top-left)](https://www.star-history.com/?repos=chavesliu%2Fsecond-brain-skill&type=date&legend=top-left)

## License

本项目采用 [MIT License](LICENSE) 开源许可证。
