<div align="center">

<h1>🧠 Second Brain Skill</h1>

<p><strong>Build Your Own AI-Powered Second Brain</strong></p>

<p>
  Inspired by <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">Karpathy's LLM Wiki</a>.<br>
  A lightweight, extensible foundation for building a continuously evolving knowledge base.
</p>

<p>
  <a href="https://github.com/ChavesLiu/second-brain-skill/stargazers"><img src="https://img.shields.io/github/stars/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/ChavesLiu/second-brain-skill/network/members"><img src="https://img.shields.io/github/forks/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHub Forks"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT License"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=flat-square" alt="Claude Code Skill">
</p>

<p>
  <a href="README.md">中文</a> |
  <strong>English</strong> |
  <a href="docs/i18n/README.ja.md">日本語</a> |
  <a href="docs/i18n/README.es.md">Español</a> |
  <a href="docs/i18n/README.fr.md">Français</a> |
  <a href="docs/i18n/README.ko.md">한국어</a> |
  <a href="docs/user-guide.en.md">Documentation</a> |
  <a href="#quick-start">Quick Start</a>
</p>

</div>

---

## Overview

**Second Brain Skill** is an open-source implementation inspired by Andrej Karpathy's [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) concept.

It transforms scattered personal knowledge into a structured, interconnected, and continuously evolving wiki — enabling AI assistants to better understand and work with your accumulated context.

The project provides a **minimal, functional, and extensible foundation** that developers can easily fork, customize, and build upon to create their own second brain.

### From Retrieval to Knowledge Accumulation

**Traditional RAG behaves like an interpreter; Second Brain Skill takes a compiler-inspired approach.**

While traditional RAG primarily retrieves relevant information at query time, Second Brain Skill uses LLMs to progressively transform raw materials into a structured wiki, maintaining relationships between sources, entities, and concepts.

Instead of repeatedly interpreting isolated documents, knowledge is organized, connected, and refined over time.

**RAG retrieves knowledge. LLM Wiki builds knowledge.**

You curate materials and ask good questions. The LLM handles the heavy lifting — summarization, cross-referencing, archiving, and consistency maintenance.

## Demo

See how raw materials become a structured, interconnected knowledge base.

![Demo: help → init → ingest → query full workflow](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/guide.gif)

## Three-Layer Architecture

Second Brain Skill separates raw materials, structured knowledge, and operating conventions into three layers.

| Layer | Location | Writer | Reader | Contents |
|:-----:|----------|:------:|:------:|----------|
| **Raw Materials** | `raw/` | You | LLM | Papers, articles, notes, PDFs, images |
| **Knowledge Base** | `wiki/` | LLM | You | Summaries, entities, concepts, analyses, cross-references |
| **Spec** | `Skill` | Co-evolve | LLM | SCHEMA, workflows, scripts |

This separation keeps original materials intact while allowing the knowledge base and its operating conventions to evolve independently.

## Quick Start

### 1. Install

```bash
# Clone the repository
git clone https://github.com/ChavesLiu/second-brain-skill.git

# Copy the Skill to Claude Code's global directory
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki

# Install dependencies
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

### 2. Initialize a Knowledge Base

```text
/wiki init
```

Follow the prompts to choose a path, name, and content language for your knowledge base. The initialization workflow currently defines `zh` (Chinese) and `en` (English) for generated wiki content; translated READMEs do not add support for other content languages.

### 3. Ingest Your First Material

```bash
# Place materials in the raw/ directory
cp my-article.md ~/my-kb/raw/
```

Then run:

```text
/wiki ingest
```

The LLM automatically reads the material, generates summary pages, extracts entities and concepts, and maintains cross-references.

A single ingestion may create or update 10–15 interconnected wiki pages, depending on the material.

### 4. Query Your Knowledge

```text
/wiki query What is Memex?
```

Or simply ask in natural language:

```text
Compare the pros and cons of RAG vs Wiki approaches
```

The LLM uses your accumulated knowledge base to answer questions and connect relevant information.

## Core Commands

| Command | Function |
|---------|----------|
| `/wiki help` | Show available commands and usage instructions |
| `/wiki init` | Create and register a new knowledge base |
| `/wiki ingest` | Ingest new materials (Markdown, PDF, images) |
| `/wiki query <question>` | Answer questions based on the knowledge base |
| `/wiki lint` | Check knowledge base health and consistency |
| `/wiki wipe` | Delete or reset wiki content pages (moved to `wiki/.trash/`; `raw/` is unchanged) |
| `/wiki test` | Run automated tests |

Use `/wiki wipe restore` to recover deleted or reset content pages. `/wiki wipe empty-trash` permanently empties the recycle bin; afterward, only content already saved in Git history can be recovered through Git.

All commands also support **natural language triggers**.

For example, you can say "ingest this article", "check the knowledge base", or "summarize information about XX" without remembering specific commands.

## Natural Language Mode

You don't need to memorize commands. The Skill automatically recognizes your intent and executes the corresponding workflow.

| What you say | Action taken |
|-------------|--------------|
| "Ingest this article" | Ingest the material |
| "What is Memex?" | Query the knowledge base |
| "Compare RAG and Wiki approaches" | Retrieve and synthesize relevant knowledge |
| "Always cite sources in answers" | Record the preference in `conventions.md` |
| "Check the knowledge base" | Run a knowledge base health check |

This approach also works well with conversational interfaces such as OpenClaw, allowing you to interact with your knowledge base naturally.

## Obsidian Integration

Second Brain Skill generates a Markdown-based knowledge base that can be opened directly in [Obsidian](https://obsidian.md/).

You can explore:

- **Knowledge graphs** — Visualize relationships between entities and concepts.
- **Backlinks** — Navigate interconnected knowledge pages.
- **Structured notes** — Browse summaries, analyses, and source references.

![Obsidian knowledge graph view](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/obsidian.png)

Recommended plugins:

- **Front Matter Title** — Display Chinese titles on graph nodes (pre-configured).
- **Dataview** — Query metadata using frontmatter.
- **Web Clipper** — Clip web articles directly into `raw/`.

## OpenClaw (Web)

Second Brain Skill can also be integrated with OpenClaw for conversational knowledge management.

Give OpenClaw access to the Skill and knowledge base, then configure the knowledge base path and auto-ingest rules in its Memory to ingest materials conversationally without typing a command each time.

For example, when you send a WeChat article link, the LLM can attempt to download it, save it to `raw/`, and ingest it if the OpenClaw environment provides the required browser or download tools (such as Playwright). This requires additional setup; configuring the knowledge base path alone is not sufficient.

![OpenClaw auto-ingest demo](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/openclaw-wiki.gif)

See [User Guide — OpenClaw Integration](docs/user-guide.en.md#openclaw-integration) for details.

## Knowledge Base Directory Structure

```text
~/my-kb/                        # Knowledge base instance
├── raw/                        # Raw materials (you write, LLM reads only)
│   ├── assets/                 # Images and attachments
│   └── *.md / *.pdf            # Material files
└── wiki/                       # LLM-generated and maintained knowledge base
    ├── index.md                # Content index
    ├── log.md                  # Operation log
    ├── overview.md             # Overview page
    ├── conventions.md          # Usage conventions and preferences
    ├── sources/                # Material summary pages
    ├── entities/               # Entity pages (people, organizations, tools)
    ├── concepts/               # Concept pages (theories, methods, patterns)
    └── analyses/               # Analysis pages (comparisons, syntheses)
```

## Use Cases

- **Research** — Continuously ingest papers and progressively build an interconnected domain knowledge base.
- **Reading** — Process books chapter by chapter, automatically connecting characters, themes, and concepts.
- **Personal Growth** — Organize journals, articles, and podcast notes into a structured landscape of personal knowledge.
- **Competitive Analysis** — Track competitors and maintain evolving comparisons and analyses.
- **Team Knowledge Base** — Ingest meeting notes and project documents while allowing the LLM to maintain structured knowledge.

## Fork & Build Your Own

Second Brain Skill is designed as a **starting point, not a finished product**.

The goal is to make Karpathy's LLM Wiki concept easier to explore, experiment with, and extend.

You can fork this repository and adapt its knowledge structure, workflows, and conventions to your own needs.

Whether you're building a personal research assistant, a domain-specific knowledge base, or a team knowledge system, this project provides a practical foundation to get started.

**Fork it. Customize it. Build your own second brain.**

Contributions, feedback, and new ideas are welcome!

## Documentation

- **[User Guide](docs/user-guide.en.md)** — Installation, features, Obsidian integration, and OpenClaw setup.
- **[Design Philosophy](skills/wiki/IDEA.md)** — Background and design principles inspired by Karpathy's LLM Wiki (in Chinese).
- **[Skill Technical Docs](skills/wiki/README.en.md)** — Page specifications, workflows, and directory structure.

## Acknowledgments

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — For introducing the LLM Wiki concept that inspired this project.
- [Vannevar Bush](https://en.wikipedia.org/wiki/Vannevar_Bush) — For proposing the Memex concept in 1945, an early vision of associative personal knowledge management.

## Star History

[![Star History Chart](https://api.star-history.com/chart?repos=chavesliu/second-brain-skill&type=date&legend=top-left)](https://www.star-history.com/?repos=chavesliu%2Fsecond-brain-skill&type=date&legend=top-left)

## License

This project is licensed under the [MIT License](LICENSE).
