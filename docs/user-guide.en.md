# Second Brain Skill User Guide

[中文](user-guide.md) | **English**

> Plug your second brain into Claude Code. Inspired by [Karpathy's LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f), this project packages personal knowledge as a Skill, turning AI into an assistant that truly understands your context.

**Repository**: [github.com/ChavesLiu/second-brain-skill](https://github.com/ChavesLiu/second-brain-skill)

---

## Table of Contents

- [Core Philosophy](#core-philosophy)
- [Prerequisites](#prerequisites)
- [Installing the Skill](#installing-the-skill)
- [Initializing a Knowledge Base](#initializing-a-knowledge-base)
- [Core Features](#core-features)
  - [Ingesting Materials — /wiki ingest](#ingesting-materials--wiki-ingest)
  - [Querying Knowledge — /wiki query](#querying-knowledge--wiki-query)
  - [Health Check — /wiki lint](#health-check--wiki-lint)
  - [Delete & Reset — /wiki wipe](#delete--reset--wiki-wipe)
  - [Automated Testing — /wiki test](#automated-testing--wiki-test)
- [Natural Language Interaction](#natural-language-interaction)
- [Obsidian Integration](#obsidian-integration)
- [OpenClaw Integration](#openclaw-integration)
- [Multi-KB Management](#multi-kb-management)
- [Use Cases](#use-cases)
- [FAQ](#faq)

---

## Core Philosophy

Traditional RAG is an **interpreter** — every query re-retrieves, assembles, and reasons over raw documents from scratch. Second Brain Skill is a **compiler** — the LLM pre-compiles materials into a structured wiki, and subsequent queries operate on the compiled artifacts. Knowledge **compounds over time**.

### Three-Layer Architecture

```
┌────────────────────────────────────────────────┐
│  Raw Materials (raw/)    ← You write, LLM reads │
│  Papers, articles, notes, PDFs, images          │
├────────────────────────────────────────────────┤
│  Knowledge Base (wiki/)  ← LLM writes, you browse │
│  Summaries, entities, concepts, analyses,       │
│  cross-references                               │
├────────────────────────────────────────────────┤
│  Spec (Skill)            ← You and LLM co-evolve │
│  SCHEMA, workflows, scripts                     │
└────────────────────────────────────────────────┘
```

You curate materials, ask good questions, and think about insights; the LLM handles all the heavy lifting — summarization, cross-referencing, archiving, and consistency maintenance.

---

## Prerequisites

### Required

| Tool | Description | Installation |
|------|-------------|-------------|
| **Claude Code** | Anthropic's official CLI tool | `npm install -g @anthropic-ai/claude-code` |
| **Python 3.10+** | Runs helper scripts (router.py, lint.py) | System default or `brew install python` |
| **PyYAML** | Dependency for lint.py | `pip install PyYAML` |

### Recommended

| Tool | Description |
|------|-------------|
| **Obsidian** | Browse wiki graph views, backlinks, and page content |
| **Obsidian Web Clipper** | Browser extension for one-click web article clipping to raw/ |
| **Git** | Version control — knowledge base evolution is naturally tracked in git |

---

## Installing the Skill

### Option 1: Clone from GitHub (Recommended)

```bash
# 1. Clone the repo
git clone https://github.com/ChavesLiu/second-brain-skill.git

# 2. Copy the skill directory to Claude Code's global skills directory
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki

# 3. Install Python dependencies
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

### Option 2: Manual Install

Download the `skills/wiki/` directory from the repo and place it at `~/.claude/skills/wiki/`.

### Verify Installation

After installation, run in Claude Code:

```
/wiki help
```

If you see a command list, the installation was successful.

### Demo: From Installation to First Use

The following demo covers the full `/wiki help` → `/wiki init` → `/wiki ingest` → `/wiki query` workflow:

![Demo: help → init → ingest → query full workflow](images/guide.gif)

### Post-Installation Directory Structure

```
~/.claude/skills/wiki/          # Skill installation directory
├── SKILL.md                    #   Main entry point, routing logic
├── SCHEMA.md                   #   Page specification (frontmatter, cross-references)
├── README.md                   #   Skill documentation
├── IDEA.md                     #   Original design philosophy
├── registries.json             #   Knowledge base registry
├── workflows/                  #   Sub-command workflow definitions
│   ├── init.md
│   ├── ingest.md
│   ├── query.md
│   ├── lint.md
│   ├── wipe.md
│   └── test.md
└── scripts/                    #   Helper scripts
    ├── router.py               #     Deterministic routing
    ├── lint.py                 #     Deterministic health checks
    └── requirements.txt        #     Python dependencies
```

---

## Initializing a Knowledge Base

Run the following command to create your first knowledge base:

```
/wiki init
```

Claude Code will ask three questions in sequence:

1. **Knowledge base path** — `raw/` and `wiki/` subdirectories will be created here
2. **Knowledge base name** — Display name used when switching between multiple KBs
3. **Wiki language** — `zh` (Chinese) or `en` (English)

After initialization, you'll have the following directory structure:

```
~/my-kb/                        # Your specified KB path
├── raw/                        #   Raw materials (you write, LLM reads only)
│   └── assets/                 #     Images and attachments
└── wiki/                       #   LLM-generated and maintained knowledge base
    ├── index.md                #     Content index (LLM query entry point)
    ├── log.md                  #     Operation log (timeline)
    ├── overview.md             #     Overview page (stats + knowledge graph summary)
    ├── conventions.md          #     Usage conventions (your preferences)
    ├── sources/                #     Material summary pages
    ├── entities/               #     Entity pages (people, orgs, tools)
    ├── concepts/               #     Concept pages (theories, methods, patterns)
    └── analyses/               #     Analysis pages (comparisons, syntheses)
```

---

## Core Features

### Ingesting Materials — `/wiki ingest`

This is the core operation for growing your knowledge base. It integrates new materials into the wiki — a single ingest may trigger the creation or update of 10–15 pages.

#### Usage

```
/wiki ingest                        # Auto-ingest all new materials in raw/
/wiki ingest paper-attention.pdf    # Ingest a specific file
```

#### Workflow

```
  Add materials        LLM reads          Auto-analyze        Create/update pages
┌─────────┐      ┌───────────┐      ┌──────────────┐      ┌──────────────┐
│ raw/    │  →  │ Markdown  │  →  │ Key points   │  →  │ sources/     │
│ article │      │ PDF       │      │ ID entities  │      │ entities/    │
│ paper   │      │ Images    │      │ ID concepts  │      │ concepts/    │
└─────────┘      └───────────┘      │ Check contra-│      │ index.md     │
                                    │ dictions     │      │ overview.md  │
                                    └──────────────┘      │ log.md       │
                                                          └──────────────┘
```

#### Steps

1. Place material files in the knowledge base's `raw/` directory (supports Markdown, PDF, images)
2. Run `/wiki ingest`
3. The LLM automatically:
   - Reads materials and extracts key points
   - Creates material summary pages (`wiki/sources/`)
   - Creates or updates entity pages (`wiki/entities/`) and concept pages (`wiki/concepts/`)
   - Maintains bidirectional cross-references to ensure graph integrity
   - Updates `index.md`, `overview.md`, `log.md`
   - Runs the lint script; P0 issues are auto-fixed

#### When Manual Intervention Is Needed

Most ingests complete fully automatically. You'll only be asked in these scenarios:

| Scenario | Description |
|----------|-------------|
| **Content conflict** | New material contradicts existing wiki content → choose to keep both / prefer new / keep old |
| **Merge ambiguity** | Unclear whether a new concept should merge with an existing page → choose merge / keep separate / rename |
| **Large-scale ingest** | Planning to create >5 new pages → choose ingest all / core only / summaries only |

---

### Querying Knowledge — `/wiki query`

Answers questions based on compiled knowledge in the wiki. Core principle: **every query makes the knowledge base better**.

#### Usage

```
/wiki query What is Memex?
/wiki query Compare the pros and cons of RAG vs Wiki approaches
Summarize everything in the knowledge base about reinforcement learning
```

#### Response Formats

The LLM automatically selects the best output format based on question type:

| Question Type | Output Format | Example |
|--------------|---------------|---------|
| Fact lookup | Short answer + citations | "What is Memex?" |
| Comparison | Markdown table | "Compare RAG and Wiki approaches" |
| Synthesis | Structured long-form | "Trace the evolution of knowledge management" |
| Timeline | Chronological list | "Timeline of developments in XX" |
| Overview | Hierarchical list | "Summarize all info about XX" |
| Presentation | Marp slides | "Generate a PPT about XX" |
| Data analysis | matplotlib charts | "Compare model performance data" |
| Relationship mapping | Obsidian Canvas | "Map the relationships between XX" |

#### Knowledge Write-Back

After answering, the LLM evaluates whether the response produced new knowledge:

- **Auto write-back** (no confirmation needed): Fill gaps in existing pages, add cross-references, fix minor errors
- **Suggested write-back** (needs confirmation): Save valuable analyses as new pages under `wiki/analyses/`, create new entity/concept pages

```
📝 Knowledge updates from this query:

Auto-updated:
  - Updated [[memex]] page with comparison to modern RAG systems
  - Added cross-reference between [[vannevar-bush]] and [[knowledge-management]]

Suggested actions:
  - 💡 Save this comparison as wiki/analyses/memex-vs-rag.md?
```

#### Feedback & Preferences

You can also tell the LLM your preferences via the query channel:

```
Always cite sources in answers
Use tables for comparison questions
Don't create standalone pages for briefly mentioned concepts
```

These preferences are recorded in `wiki/conventions.md` and automatically followed in all subsequent operations.

---

### Health Check — `/wiki lint`

Periodically check the wiki's health to find and fix issues. Recommended after every 5–10 material ingests.

#### Usage

```
/wiki lint
```

#### Two-Layer Check Mechanism

| Layer | Tool | Checks |
|-------|------|--------|
| **Deterministic script** | `lint.py` | Broken links, raw wikilink misuse, frontmatter completeness, index consistency, bidirectional links, orphan pages, sources field |
| **LLM semantic supplement** | Claude | Language consistency, contradiction detection, missing pages, stale info, missing cross-references, tag inconsistency, knowledge expansion suggestions |

#### Issue Priority

| Level | Meaning | Action |
|-------|---------|--------|
| 🔴 **P0** | Structural errors affecting knowledge graph integrity | Fix immediately |
| 🟡 **P1** | Quality issues affecting knowledge accuracy | Review individually |
| 🟢 **P2** | Optimization suggestions to deepen the knowledge base | Suggestions only |

#### Example Output

```
## Wiki Health Check Report (2026-04-14)

### 📊 Statistics
- Total pages: 15
- Source summaries: 5  |  Entity pages: 4  |  Concept pages: 5  |  Analysis pages: 1

### 🔴 P0 — Needs Fixing
- [ ] [broken_link] concepts/rag.md: [[llm-training]] points to non-existent page

### 🟡 P1 — Suggested Improvements
- [ ] [orphan_page] entities/ted-nelson.md: Orphan page, no other pages link to it

### 🟢 P2 — Optional Optimizations
- [ ] Suggest creating a standalone concept page for "RAG" (referenced by 3 pages but has no page)

🔍 Knowledge expansion suggestions (based on web search):
- [[memex]] page mentions Ted Nelson but lacks detail
  → Recommended: "Ted Nelson and the Xanadu Project"
  → Priority: Medium
```

You can also run the script standalone for a quick check:

```bash
# Human-readable output
python ~/.claude/skills/wiki/scripts/lint.py \
  --wiki-dir ~/my-kb/wiki --raw-dir ~/my-kb/raw

# JSON format (for programmatic use)
python ~/.claude/skills/wiki/scripts/lint.py \
  --wiki-dir ~/my-kb/wiki --raw-dir ~/my-kb/raw --json
```

---

### Delete & Reset — `/wiki wipe`

All delete operations use a recycle bin mechanism and are recoverable. Raw materials (`raw/`) are never touched.

#### Usage

| Command | Function |
|---------|----------|
| `/wiki wipe` | Interactive selection |
| `/wiki wipe all` | Full reset (all pages moved to recycle bin) |
| `/wiki wipe <keyword>` | Delete matching pages |
| `/wiki wipe trash` | View recycle bin contents |
| `/wiki wipe restore` | Restore pages from recycle bin |
| `/wiki wipe empty-trash` | Permanently empty recycle bin (irreversible) |

#### Recycle Bin Mechanism

- Delete = move to `wiki/.trash/`, preserving original directory structure
- Example: `wiki/concepts/swiglu.md` → `wiki/.trash/concepts/swiglu.md`
- Restore automatically moves back to original path and re-updates index.md and related page links
- After permanent deletion (`empty-trash`), recovery is only possible via git

---

### Automated Testing — `/wiki test`

Verify the integrity of the entire system.

```
/wiki test
```

Tests cover four dimensions:

| Test | Verification |
|------|-------------|
| Architecture integrity | Directory structure, core files present |
| Ingest workflow | Run full ingest flow with test materials |
| Query workflow | Verify queries correctly reference wiki pages |
| Lint workflow | Health check generates structured report |

---

## Natural Language Interaction

You **don't need to remember any commands**. Second Brain Skill supports fully natural language operation — interact with your knowledge base like chatting with an assistant who knows your knowledge. The LLM automatically detects your intent and routes to the corresponding workflow.

### Intent Detection

| What you say | LLM understands | Action taken |
|-------------|----------------|-------------|
| "Ingest this article" | Ingest materials | → `ingest` workflow |
| "Add the new files in raw to the KB" | Ingest materials | → `ingest` workflow |
| "What is Memex?" | Knowledge query | → `query` workflow |
| "Compare RAG and Wiki approaches" | Knowledge query | → `query` workflow |
| "Summarize everything about RL" | Knowledge query | → `query` workflow |
| "Always cite sources in answers" | Preference | → Write to `conventions.md` |
| "You were wrong last time, it's actually XX" | Content correction | → Fix corresponding wiki page |
| "Check if there are any issues with the KB" | Health check | → `lint` workflow |
| "Delete pages related to XX" | Delete content | → `wipe` workflow |

### Two Usage Modes

| Mode | Best for | Example |
|------|----------|---------|
| **Command mode** `/wiki <cmd>` | When you know exactly what to do | `/wiki ingest`, `/wiki lint` |
| **Natural language mode** | Daily use, conversational interaction | "What does this paper say?", "Summarize XX for me" |

Both modes produce identical results. Natural language mode is better for everyday use — especially on the **web (OpenClaw)**, where conversational interaction feels more natural and requires no command memorization.

### Feedback as Evolution

A key feature of natural language mode is **feedback write-back**. Any preference you express about how the LLM should operate is automatically recorded in `wiki/conventions.md` and followed in all subsequent operations:

```
You: "Use tables for comparisons"
→ Recorded under the Query section of conventions.md

You: "Don't create standalone pages for briefly mentioned concepts"
→ Recorded under the Ingest section of conventions.md
```

The knowledge base progressively learns your habits as you use it.

---

## Obsidian Integration

Obsidian is the ideal companion for browsing and visualizing the wiki. The LLM maintains the knowledge base in Claude Code; you browse results in Obsidian in real time.

### Basic Setup

1. Open the knowledge base root directory (e.g., `~/my-kb/`) with Obsidian
2. Apply the following recommended settings:

| Setting | Configuration |
|---------|--------------|
| Attachment path | Settings → Files and links → Attachment folder → `raw/assets/` |
| Download attachments hotkey | Settings → Hotkeys → "Download attachments" → `Ctrl+Shift+D` |

### Recommended Plugins

| Plugin | Purpose | Necessity |
|--------|---------|-----------|
| **Front Matter Title** | Display Chinese titles in graph and file list (instead of English filenames) | Highly recommended |
| **Dataview** | Metadata queries based on frontmatter | Recommended |
| **Web Clipper** | One-click web article clipping in the browser | Recommended |
| **Marp Slides** | Browse LLM-generated slides | Optional |

### Front Matter Title Plugin

The project includes pre-configured settings for the Front Matter Title plugin. Just install and it works:

**Install**: Settings → Community plugins → Browse → Search "Front Matter Title" → Install → Enable

**Effect**: By default, Obsidian shows English filenames as node labels. The plugin reads the `title` field from each page's frontmatter and replaces it with the localized title.

| Replacement Area | Effect |
|-----------------|--------|
| Graph | Graph nodes show localized titles |
| Explorer | Left sidebar file list shows localized titles |
| Tab | Tab titles show localized names |
| Search | Search results show localized titles |
| Suggest | `[[` link suggestion popup shows localized titles |

### Graph View Configuration

After opening the graph view, set a filter in the top-left search bar to hide auxiliary pages:

```
-file:index -file:log -file:overview
```

Other recommended settings (click the gear icon in the top-left of the graph):
- **Show tags**: On (shows tag nodes in the graph)
- **Show attachments**: Off
- **Show orphans**: On (helps discover orphan pages)

### Web Clipper Ingestion Flow

1. Install the Obsidian Web Clipper browser extension
2. Browse to an article you want to ingest, click the Web Clipper icon
3. Save to the knowledge base's `raw/` directory
4. (Optional) Press `Ctrl+Shift+D` to download article images to `raw/assets/`
5. Return to Claude Code and run `/wiki ingest`

---

## OpenClaw Integration

[OpenClaw](https://github.com/openclaw/openclaw) enables cross-device knowledge base management.

**OpenClaw is the perfect companion for natural language mode** — with multiple input channels available, it provides conversational freedom. The experience is naturally suited for natural language interaction — you don't need to remember any commands, just chat with your knowledge base like talking to an assistant.

### Prerequisites

- Skill installed locally and knowledge base initialized
- Knowledge base directory synced to OpenClaw's accessible environment via Git or cloud sync

### Setup Steps

1. **Ensure Skill files are in place**: The `~/.openclaw/workspace/skills/` directory in the OpenClaw environment needs the complete Skill files
2. **Sync knowledge base**: Sync the knowledge base directory (with `raw/` and `wiki/`) to an OpenClaw-accessible path
3. **Update registry**: If paths have changed, update the knowledge base path in `~/.openclaw/workspace/skills/wiki/registries.json`
4. **Verify**: Run `/wiki help` in OpenClaw to confirm the Skill loads correctly

### Usage

Both command mode and natural language mode work:

**Command mode** (same as local CLI):

```
/wiki ingest
/wiki query What is Memex?
/wiki lint
```

**Natural language mode** (recommended — better suited for web interaction):

```
Ingest the new articles in raw
What's the relationship between Memex and modern knowledge management?
Compare the pros and cons of RAG vs Wiki approaches
Summarize everything in the KB about XX
Check if there are any issues with the knowledge base
```

On the web, you can interact with your knowledge base like a regular chat — ask questions, ingest, correct errors, set preferences — the LLM automatically detects intent and executes.

### Advanced: Configure Memory for Auto-Ingest

By writing knowledge base configuration into OpenClaw's Memory, you can have the LLM **automatically detect materials you send and ingest them** — without needing to type any commands at all.

#### Configuration

Add the following to OpenClaw's memory:

```
- Learning KB: ~/Documents/knowledge-wiki, ID: learning-kb, Language: zh
- When user sends articles/papers/resources → save directly to ~/Documents/knowledge-wiki/raw/
- When user sends a WeChat article link → auto Playwright PDF download + auto ingest, no need to wait for commands
- /wiki ingest to batch-ingest into KB (can also be triggered manually)
- Wiki skill path: ~/.openclaw/workspace/skills/wiki/
```

#### Result

![OpenClaw auto-ingest: send a link, it goes into the KB](images/openclaw-wiki.gif)

After configuration, your workflow becomes extremely simple:

**Send a WeChat article link**:

```
https://mp.weixin.qq.com/s/xxxxxxx
```

The LLM automatically completes the entire pipeline:

```
Detected WeChat article link
  → Playwright opens the link, exports as PDF
  → Saves to ~/Documents/knowledge-wiki/raw/
  → Auto-runs /wiki ingest
  → Creates summary, entity, and concept pages
  → Updates index and graph
✅ Ingestion complete
```

**Send an article or paper**:

```
This paper describes a new attention mechanism: [paste content or file]
```

The LLM automatically saves to `raw/` and triggers ingest — no additional commands needed.

#### Typical Workflow

```
You (spot a great article on your phone/computer)
  → Copy link, send to OpenClaw
  → LLM auto-downloads, ingests, and organizes
  → Next time you ask a related question, the knowledge is already in the KB
```

This makes feeding your knowledge base zero-friction — see great content, toss it to OpenClaw, done.

---

## Multi-KB Management

Second Brain Skill supports managing multiple knowledge bases through a unified `registries.json`.

### Creating Multiple KBs

```
/wiki init    # First time: create "AI Research" KB
/wiki init    # Second time: create "Book Notes" KB
```

### Switching KBs

When multiple KBs exist:

- **Has default**: Operations automatically use the default KB, with a prompt to switch
- **No default**: Asks which KB to use before each operation

### registries.json Format

```json
{
  "default": "ai-research",
  "registries": {
    "ai-research": {
      "name": "AI Research",
      "path": "/Users/you/knowledge/ai-research",
      "language": "zh",
      "created": "2026-04-13"
    },
    "book-notes": {
      "name": "Book Notes",
      "path": "/Users/you/knowledge/book-notes",
      "language": "zh",
      "created": "2026-04-14"
    }
  }
}
```

Change the `"default"` field to switch the default knowledge base.

---

## Use Cases

| Scenario | Description | Example |
|----------|-------------|---------|
| **Research** | Continuously read papers/articles; progressively build a complete domain knowledge graph | Ingest AI papers; auto-track technology evolution and compare methods |
| **Reading** | Ingest chapter by chapter; auto-build character, theme, and plot association networks | Reading *Lord of the Rings* — LLM auto-maintains character relationships and event timelines |
| **Personal Growth** | Journals, articles, podcast notes; build a structured landscape of self-knowledge | Ingest psychology articles and podcast summaries; track personal development themes |
| **Competitive Analysis** | Continuously track competitors; auto-maintain comparison analyses | Ingest competitor releases and reports; auto-update comparison tables |
| **Course Notes** | Ingest lecture by lecture; auto-organize knowledge systems and concept relationships | University course notes — LLM auto-organizes knowledge structure |
| **Team KB** | Ingest meeting notes and project docs; LLM auto-maintains | Shared team git repo — LLM helps organize and retrieve |

---

## FAQ

### Q: How large can a knowledge base be?

The current architecture performs well at ~100 materials and ~hundreds of wiki pages. `index.md` combined with Grep search is efficient enough. Beyond this scale, consider integrating search tools like qmd.

### Q: What material formats are supported?

- **Markdown** (`.md`) — Read directly
- **PDF** (`.pdf`) — Read via the Read tool
- **Images** (`.png`, `.jpg`, etc.) — Viewed via the Read tool (LLM native multimodal capabilities)

### Q: Can wiki pages be edited manually?

Yes, but not recommended. The wiki layer is fully managed by the LLM. To correct content, tell the LLM what's wrong via `/wiki query` and it will auto-update the relevant pages. To change how things work, tell the LLM your preferences and it will record them in `conventions.md`.

### Q: How to back up the knowledge base?

The knowledge base is just a directory of Markdown files. Best practice is to manage with Git:

```bash
cd ~/my-kb
git init
git add -A
git commit -m "ingest: ingested XX"
```

Recommended commit timing: after each ingest, after lint fixes.

### Q: Can this be used with ChatGPT / Codex?

The core philosophy is universal (see [IDEA.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)). However, this project's Skill implementation is built for Claude Code. To use with other LLM platforms, you'd need to adapt the Skill logic to the target platform's agent specification (e.g., OpenAI Codex's AGENTS.md).

### Q: How quickly do changes appear in Obsidian after ingesting?

Instantly. When the LLM creates/edits files in Claude Code, Obsidian automatically detects filesystem changes and refreshes the display. You can keep Claude Code on one side and Obsidian on the other, watching your knowledge base grow in real time.

### Q: How to view knowledge base operation history?

Two ways:

1. Open `wiki/log.md` in Obsidian to view the complete operation log
2. Quick CLI view of recent operations:
   ```bash
   grep "^## \[" ~/my-kb/wiki/log.md | head -5
   ```

---

## Page Specification Quick Reference

### Frontmatter Template

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

### File Naming Convention

- All lowercase English + hyphens: `reinforcement-learning.md`
- Source summary pages share the same name as the raw file: `raw/paper-x.pdf` → `wiki/sources/paper-x.md`
- Filenames should be 50 characters or fewer

### Cross-Reference Syntax

```markdown
[[page-name]]              # Basic link
[[page-name|Display Text]] # Alias link
```

- Each page has a `## Related` section at the bottom
- The LLM automatically maintains bidirectional link integrity
- Raw material links use standard Markdown syntax `[text](path)`, not `[[wikilink]]`

---

> This guide is continuously updated with the project. Feedback and suggestions are welcome at [GitHub Issues](https://github.com/ChavesLiu/second-brain-skill/issues).
