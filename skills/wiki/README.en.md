# Second Brain Skill

[中文](README.md) | **English**

An LLM-built and maintained personal knowledge base. The LLM handles all the heavy lifting — summarization, cross-referencing, archiving, consistency maintenance — while you curate materials, ask good questions, and think about what it all means.

> See [IDEA.md](IDEA.md) for the original design philosophy.

---

## Quick Start

### 1. Prerequisites

- Install [Claude Code](https://claude.ai/code) (CLI tool)
- Install [Obsidian](https://obsidian.md/) (optional, for browsing the wiki)

### 2. Initialize a Knowledge Base

```
/wiki init
```

Follow the prompts to enter a path, name, and language. Multiple knowledge bases are supported — when multiple exist, the system will ask which one to use.

### 3. Available Commands

| Command | Function |
|---------|----------|
| `/wiki init` | Create and register a new knowledge base |
| `/wiki ingest` | Ingest new materials into the knowledge base |
| `/wiki query <question>` | Answer questions based on the knowledge base |
| `/wiki lint` | Run a health check on the knowledge base |
| `/wiki wipe` | Reset/delete knowledge base content |
| `/wiki test` | Run automated tests |

### 4. Ingest Your First Material

```
1. Place material files (Markdown, PDF, etc.) in the knowledge base's raw/ directory
2. Run /wiki ingest in Claude Code
3. The LLM automatically reads materials, creates summary pages, splits out entity
   and concept pages, and maintains cross-references
   (only asks you when encountering conflicts or ambiguities)
```

### 5. Browse with Obsidian

Open the knowledge base directory with Obsidian to browse the wiki's graph view, backlinks, and page content in real time.

---

## Directory Structure

The Skill is installed globally; knowledge base directories are created by the user via `/wiki init` and can be multiple.

```
~/.claude/skills/wiki/        # Skill (global installation)
├── SKILL.md                  #   Main entry point, routes sub-commands
├── SCHEMA.md                 #   Schema (LLM page specification)
├── README.md                 #   This file
├── IDEA.md                   #   Original design philosophy
├── registries.json           #   Knowledge base registry
├── workflows/                #   Detailed workflows for each sub-command
└── scripts/                  #   Helper scripts (lint.py, etc.)

~/my-kb/                      # Knowledge base instance (user-specified path)
├── raw/                      #   Raw materials (read-only)
│   ├── assets/               #   Images and attachments
│   └── *.md / *.pdf          #   Material files
└── wiki/                     #   LLM-generated and maintained knowledge base
    ├── index.md              #   Content index
    ├── log.md                #   Operation log
    ├── overview.md           #   Overview page
    ├── sources/              #   Material summary pages
    ├── entities/             #   Entity pages
    ├── concepts/             #   Concept pages
    └── analyses/             #   Analysis pages
```

### Three-Layer Architecture

| Layer | Location | Who writes | Who reads | Description |
|-------|----------|-----------|-----------|-------------|
| Raw materials | `<kb>/raw/` | You | LLM | Immutable source of truth; LLM reads only |
| Knowledge base | `<kb>/wiki/` | LLM | You | Fully owned by LLM; you browse via Obsidian |
| Spec | `~/.claude/skills/wiki/` | You + LLM | LLM | Skill code, Schema, registry |

---

## Core Operations

### `/wiki ingest` — Ingest Materials

Integrates new materials into the knowledge base. **Runs fully automatically by default**, only asking when human judgment is needed. A single ingest may trigger the creation or update of 10–15 pages.

**Workflow:**

1. **Discover new materials** — Scan `raw/` for un-ingested files
2. **Read materials** — Supports Markdown, PDF, images
3. **Analyze & decide** — Automatically analyzes key points, identifies entities and concepts, checks for conflicts. Proceeds directly in normal cases; only asks in these situations:
   - New material **contradicts** existing content → ask how to handle
   - New concept **may duplicate** an existing page → ask whether to merge
   - Planning to create **>5 new pages** → ask about ingestion scope
4. **Create source summary page** — Generate structured summary under `wiki/sources/`
5. **Create/update entity and concept pages** — Entities (people, orgs, tools) → `wiki/entities/`, Concepts (theories, methods, patterns) → `wiki/concepts/`
6. **Maintain graph integrity** — Ensure bidirectional links are complete; update index.md, overview.md, log.md
7. **Deterministic check** — Auto-run lint.py script; fix P0 issues immediately

**Examples:**
```
> /wiki ingest                        # Auto-ingest all new materials
> /wiki ingest paper-attention.pdf    # Ingest a specific file
```

### `/wiki query` — Query the Knowledge Base

Answers questions based on accumulated knowledge in the wiki, rather than reasoning from scratch each time.

**Workflow:**

1. **Index lookup** — Read index.md to locate relevant pages
2. **Deep reading** — Read relevant wiki pages and raw materials
3. **Synthesize answer** — Structured answer with citations
4. **Knowledge compounding** — Valuable answers can be saved as new pages under `wiki/analyses/`

**Supported response formats:**

| Question type | Output format |
|--------------|---------------|
| Fact lookup | Short answer + citations |
| Comparison | Markdown table |
| Synthesis | Structured long-form |
| Timeline | Chronological list |
| Overview | Hierarchical list |
| Presentation | Marp slides |
| Data analysis | matplotlib charts |
| Relationship mapping | Obsidian Canvas |

**Examples:**
```
> /wiki query What is the relationship between Memex and modern knowledge management?
> /wiki query Compare the pros and cons of RAG vs Wiki approaches
> Summarize everything in the knowledge base about XX
```

### `/wiki lint` — Health Check

Periodically checks the wiki's health to find and fix issues. Recommended after every 5–10 material ingests.

**Two-layer check mechanism:**

1. **Deterministic script** (`python ~/.claude/skills/wiki/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw`) — Detects structural issues with code; results are 100% reproducible
2. **LLM semantic supplement** — Checks content quality issues that scripts cannot judge

**Check items (by priority):**

| Level | Script checks (deterministic) | LLM supplement (semantic) |
|-------|------------------------------|--------------------------|
| P0 | Broken links, raw wikilink misuse, frontmatter completeness, index consistency | — |
| P1 | Missing bidirectional links, orphan pages, missing sources field | Language consistency, contradiction detection, missing pages, stale info |
| P2 | — | Missing cross-references, tag inconsistency, mergeable pages, knowledge gaps |

**Output**: Structured report — P0 items should be fixed immediately, P1 reviewed individually, P2 are suggestions only.

You can also run the script standalone for a quick check:
```bash
python ~/.claude/skills/wiki/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw          # Human-readable output
python ~/.claude/skills/wiki/scripts/lint.py --wiki-dir <kb>/wiki --raw-dir <kb>/raw --json   # JSON format (for programmatic use)
```

**Examples:**
```
> /wiki lint
> Check if there are any issues with the wiki
```

### `/wiki test` — Automated Testing

Verifies the integrity of the entire system: directory structure, ingest workflow, cross-references, lint logic.

```
> /wiki test
```

---

## Page Specification

### Frontmatter

Every wiki page has a YAML metadata header, compatible with Obsidian's Dataview plugin:

```yaml
---
title: Page Title
aliases: [Alternative names]              # Used by Front Matter Title plugin
type: source | entity | concept | analysis
created: 2026-04-13
updated: 2026-04-13
tags: [tag1, tag2]
sources: [referenced raw material filenames]
---
```

### Cross-References

Uses Obsidian's wikilink syntax to ensure the graph view works correctly:

```markdown
[[page-name]]              # Basic link
[[page-name|Display Text]] # Alias link
```

Every page has a `## Related` section at the bottom listing all related links. The LLM maintains bidirectional reference integrity.

### Naming Convention

- Filenames: lowercase English + hyphens, e.g. `reinforcement-learning.md`
- Source summary pages share the same name as the raw file: `raw/paper-x.pdf` → `wiki/sources/paper-x.md`

---

## Index & Log

### index.md — Content Index

The wiki's table of contents, organizing all pages by category. The LLM reads this file first when answering queries to locate relevant pages.

```markdown
## Sources
- [Material Title](sources/filename.md) — One-line summary (date)

## Entities
- [Entity Name](entities/filename.md) — One-line description [N source references]
```

### log.md — Operation Log

Records all operations in reverse chronological order, with a consistent parseable format:

```markdown
## [2026-04-13] ingest | Article Title
- Pages created: ...
- Pages updated: ...
```

Quick view of recent operations with grep:
```bash
grep "^## \[" wiki/log.md | head -5
```

---

## Obsidian Configuration

After opening the knowledge base directory with Obsidian, the following settings are recommended:

| Setting | Configuration |
|---------|--------------|
| Attachment path | Settings → Files and links → Attachment folder → `raw/assets/` |
| Download attachments hotkey | Settings → Hotkeys → "Download attachments" → `Ctrl+Shift+D` |
| Recommended plugins | Dataview (metadata queries), Marp Slides (presentations), Web Clipper (web clipping), **Front Matter Title** (display localized titles in graph/file list) |

**Web Clipper** is great for quickly ingesting web articles: one click in the browser converts an article to Markdown, saves to `raw/`, then `/wiki ingest` does the rest.

### Front Matter Title Plugin Configuration

The knowledge base directory can include pre-configured Front Matter Title plugin settings (`.obsidian/plugins/obsidian-front-matter-title-plugin/data.json`), which take effect after installation.

**Purpose**: By default, Obsidian displays English filenames as node and file list labels. This plugin reads the `title` field from each page's frontmatter and displays the localized title instead.

**Install**: Settings → Community plugins → Browse → Search "Front Matter Title" → Install → Enable

**Enabled replacement areas:**

| Area | Effect |
|------|--------|
| Graph | Graph nodes display localized titles |
| Explorer | Left sidebar file list displays localized titles |
| Tab | Tab titles display localized names |
| Search | Search results display localized titles |
| Suggest | `[[` link suggestion popup displays localized titles |

**How it works**: The plugin's global template `common.main` is set to `"title"`, reading the frontmatter `title` field. Since every wiki page includes `title` in its frontmatter, all pages display localized titles. To customize a specific feature's template, set a separate `templates.main` in the plugin settings for that feature (leave empty to use the global template).

### Graph View Configuration

After opening the graph view, set a filter in the top-left search bar to hide non-knowledge pages:

```
-file:index -file:log -file:overview
```

Other recommended settings (click the gear icon in the top-left of the graph):
- **Show tags**: On — display tag nodes in the graph
- **Show attachments**: Off
- **Show orphans**: On — helps discover orphan pages

---

## Git Version Control

The knowledge base can be a git repository — version history is a natural record of knowledge evolution.

- The LLM does not auto-commit; you decide when to save versions
- Recommended commit timing: after each ingest, after lint fixes
- Commit message format: `ingest: ingested XXX`, `lint: fixed N issues`

---

## Extension: Search Tools

At the current stage (< 100 pages), index.md + Grep is efficient enough. As the wiki grows, you can integrate search engines:

- [qmd](https://github.com/tobi/qmd) — Local Markdown search engine with BM25/vector hybrid search and LLM re-ranking, provides CLI and MCP server
- Or write custom search scripts under `.claude/skills/wiki/scripts/`

---

## Use Cases

| Scenario | Description |
|----------|-------------|
| Research | Continuously read papers/articles; progressively build a complete domain knowledge graph |
| Reading | Ingest chapter by chapter; auto-build character, theme, and plot association networks |
| Personal growth | Journals, articles, podcast notes; build a structured landscape of self-knowledge |
| Competitive analysis | Continuously track competitors; auto-maintain comparison analyses |
| Course notes | Ingest lecture by lecture; auto-organize knowledge systems and concept relationships |
| Team knowledge base | Ingest meeting notes, Slack discussions, project docs; LLM auto-maintains |
