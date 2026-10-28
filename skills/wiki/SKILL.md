---
name: wiki
version: v1.0.0
author: ChavesLiu
description: |
  知识库管理工具。收录素材、查询知识、健康检查、重置删除。
  TRIGGER when: 用户使用 zh/en/ja/es/fr/ko 任一语言提到「收录」「加到知识库」「ingest」，或提出知识库中可能有答案的问题（如「XX 是什么」「对比 XX 和 YY」「整理 XX 的信息」），或要求「检查知识库」「lint」，或要求「清空」「删除」「重置」知识库内容，或明确表达修改交互语言/语言设置的意图。
  DO NOT TRIGGER when: 问题与知识库无关（纯代码任务、文件操作、通用对话），或用户明确说不需要查知识库；用户只是用另一种语言普通提问，不等同于修改默认语言。
user-invocable: true
---

# Second Brain Skill

知识库的统一管理入口。支持命令式调用（`/wiki <cmd>`）和自然语言触发。

## 语言职责

- `UI_LANG`：界面交互、帮助文本、回答、确认问题、执行报告。
- `KB_LANG`：wiki 页面、frontmatter 中面向人的字段、tags、index、overview、conventions、log。
- 用户用某种语言普通提问，不会改变已保存的交互语言偏好。
- 查询时用户可单次明确指定回答语言；这只影响本次回答，不写入 `settings.json`，也不改变 `KB_LANG`。
- 已有知识库内容和已有偏好不因普通提问语言自动翻译或迁移。
- 语言优先级：本次明确要求的回答语言仅覆盖本次回答；其余用户交互以 `settings.json` 的 `UI_LANG` 为准，页面写入以 `KB_LANG` 为准。`conventions.md` 中历史语言偏好不得覆盖这两项配置。明确要求“以后默认用某语言回复”时使用 `language <code>` 持久化，不另存为 conventions 语言规则。

## 自然语言路由

当 skill 被自然语言触发（非 `/wiki` 命令格式）时，先判断意图再映射子命令。支持 zh/en/ja/es/fr/ko 六种自然语言表达：

| 用户意图 | 映射子命令 | args 规则 | 示例 |
|---------|-----------|----------|------|
| 收录/添加素材 | `ingest` | 原始输入作为参数 | "收录这篇文章"、"ingest this note"、"raw の新しいファイルを取り込んで" |
| 提问/查询/对比/整理 | `query` | 原始输入作为问题 | "Memex 是什么"、"compare RAG and Wiki mode"、"XX の情報を整理して" |
| 反馈/偏好/纠正 | `query`（走反馈分支） | 原始输入作为反馈 | "回答要标注来源"、"cite sources in answers"、"前回の回答は違う" |
| 检查/审计 | `lint` | 原始输入作为参数 | "检查下知识库有没有问题"、"check the wiki health" |
| 删除/清空/重置 | `wipe` | 原始输入作为参数 | "删掉 XX 相关的页面"、"reset the knowledge base" |
| 初始化 | `init` | 原始输入作为参数 | "创建一个新的知识库"、"create a new wiki" |
| 明确修改交互语言 | `language` | 必须映射为合法的单个语言代码 `zh/en/ja/es/fr/ko`；不得把整句自然语言作为 args | "切换为英文界面" → `language en`；"set UI language to Japanese" → `language ja`；"réponds-moi en français par défaut" → `language fr` |

确定子命令后调用路由脚本。注意：用户只是用另一种语言提出普通查询时，不自动修改配置；只有明确表达“更改默认语言/交互语言”的意图才路由到 `language`。

## 路由契约

路由脚本读取 `settings.json` 顶层字段 `interaction_language` 作为 UI 交互语言，支持：`zh`、`en`、`ja`、`es`、`fr`、`ko`。不得使用 `runtime.interaction_language`。

路由结果字段约定：

- `status: "needs_language"`：首次使用或缺少交互语言配置。必须包含 `supported_languages` 和 `original_args`（数组，保留原始 argv，不拼接字符串）。
- `status: "ok"`：正常执行。必须包含 `subcommand`、`args`、`ui_lang`。
- `subcommand: "init"`：必须返回 `init_lang = ui_lang`，且 `kb = null`；执行 init 时不得解引用 `kb`。
- `subcommand: "language"`：语言命令。`/wiki language <code>` 由 `router.py language <code>` 原子保存到 `settings.json` 顶层 `interaction_language`，并返回 `status: "ok"`、`subcommand: "language"`、`interaction_language`、`ui_lang`；`/wiki language` 无参数时显示当前语言和支持语言。
- `kb.lang`：知识库内容语言。旧版 `registries.json` 没有 language 时，缺省为 `zh`，不迁移、不翻译旧库内容。
- 有效命令包括空参数（等价 `help`）、`help`、`language`、`init`、`ingest`、`query`、`lint`、`wipe`、`test`。首次使用即使是无参数 `help` 也需要先处理 `needs_language`，以便帮助文本使用 UI_LANG。

## 执行步骤

### 1. 运行路由脚本

运行 `python <skill-dir>/scripts/router.py <子命令> [参数]` 获取路由结果（JSON）。

`<skill-dir>` 为本文件所在目录的绝对路径。对于自然语言触发，先按上表映射出子命令再调用；自然语言语言切换必须先归一化成合法单个 code。

### 2. 根据路由结果执行

根据 JSON 中的 `status` 字段分支：

#### `status: "needs_language"` — 需要选择交互语言

使用 AskUserQuestion 且只询问一次。题干必须同时包含六种语言原生表达，含义为选择界面语言：

```text
选择界面语言 / Choose interface language / 表示言語を選択 / Elige el idioma de la interfaz / Choisissez la langue de l’interface / 인터페이스 언어를 선택하세요
```

选项固定为四个直接选项：

- `zh` — 中文
- `en` — English
- `ja` — 日本語
- `es` — Español

通过工具的 Other/自定义输入接收 `fr` 或 `ko`，题干需清楚说明也可输入 `fr`（Français）或 `ko`（한국어）。如果用户取消，立即停止，不继续执行原命令。

用户选择后，不要直接 Write `settings.json`。必须调用 `python <skill-dir>/scripts/router.py language <code>`，让 router 原子保存顶层 `interaction_language`。保存成功后，用 `original_args` 重新执行原始命令：必须逐参数安全引用（例如使用参数数组或逐项 shell quote），不得把未转义的用户文本拼接成命令字符串。重新执行后按新的路由结果继续。

#### `status: "ok"` — 正常执行

```
路由结果字段:
  subcommand           — 子命令名
  args                 — 子命令参数
  ui_lang              — UI 交互语言（zh/en/ja/es/fr/ko）
  init_lang            — init 专用，等于 ui_lang，作为新库 KB_LANG；仅 init 出现
  interaction_language — language 子命令保存/显示的交互语言代码；适用时出现
  workflow             — 工作流文件路径（相对于 skill 目录；help/language 可为 null）
  schema               — SCHEMA.md 路径（需要时非 null）
  kb                   — 知识库信息（id, name, root, wiki, raw, lang；help/language/init 可为 null）
  skill_dir            — skill 目录绝对路径
  multiple_kbs         — 是否有多个知识库（可选）
  kb_list              — 知识库列表（可选，multiple_kbs 时出现）
```

执行顺序：
1. 如果 `subcommand` 是 `help` 或 `language`，在任何 workflow/kb 读取之前直接处理，不要求已有知识库。
2. 如果 `subcommand` 是 `init`，读取 `SCHEMA.md` 与 `workflows/init.md`，用 `ui_lang` 替换 `UI_LANG`，用 `init_lang` 替换 `INIT_LANG`；不得访问 `kb.root`、`kb.wiki`、`kb.raw` 或 `kb.lang`。
3. 其他子命令：如果 `schema` 非 null → 读取 `<skill_dir>/<schema>` 了解页面规范。
4. 其他子命令：如果 `<kb.wiki>/conventions.md` 存在 → 读取，作为本次操作的额外约束。
5. 其他子命令：读取 `<skill_dir>/<workflow>` 获取工作流。
6. 其他子命令：用 `kb` 中的路径（`root`、`wiki`、`raw`）和语言（`lang`）替换 workflow 中的 `KB_ROOT`、`KB_WIKI`、`KB_RAW`、`KB_LANG`，用 `ui_lang` 替换 `UI_LANG`。
7. 按工作流执行，`args` 作为子命令参数传入，遵守 conventions.md 中的约定。
8. 如果 `multiple_kbs` 为 true，先用 UI_LANG 告知用户当前使用的是哪个知识库（kb.name），提示可在 registries.json 中修改 default。

#### `status: "select"` — 需要用户选择知识库

用 AskUserQuestion 展示 `kb_list` 让用户选择，题干、选项说明、确认文本使用 `UI_LANG`。选择后保留注册表其他字段，仅更新 `registries.json` 的 `default` 为选中 ID，再用原始子命令和参数重新运行 router，取得完整 `kb`（包括内容语言、路径校验）后执行工作流；不得用 `UI_LANG` 替代选中库的 `kb.lang`。

#### `status: "no_kb"` — 无知识库

用 `UI_LANG` 输出提示信息，例如 `{message}`，并建议先运行 `/wiki init`。

#### `status: "error"` — 错误

用 `UI_LANG` 输出错误信息。

#### `subcommand: "help"` — 帮助

在常规读取 workflow/kb 之前处理。按 `UI_LANG` 输出等价帮助内容；以下中文只表示含义，非中文 UI_LANG 时要自然翻译，不要逐字照抄：

```text
Second Brain — LLM 驱动的知识库管理工具

命令:
  /wiki init                  创建并注册一个新的知识库
  /wiki ingest [文件名]       收录 raw/ 中的新素材（不指定则收录全部）
  /wiki query <问题>          基于知识库回答问题
  /wiki lint                  知识库健康检查
  /wiki wipe [子命令]         重置/删除（all | <关键词> | trash | restore | empty-trash）
  /wiki language [语言代码]   显示或切换交互语言（zh/en/ja/es/fr/ko）
  /wiki test                  手动测试指南
  /wiki help                  显示本帮助

首次使用请先运行 /wiki init
```

其他语言按含义翻译，不改变命令名和参数名。

#### `subcommand: "language"` — 语言

在常规读取 workflow/kb 之前处理，不要求已有知识库。

- 无参数：用当前 `UI_LANG` 显示当前交互语言和支持语言列表。
- 有语言代码：必须已经由 router 原子保存到 `settings.json` 顶层 `interaction_language`；成功后用新 `ui_lang` 报告已切换，字段名使用 `interaction_language`。
- 非支持代码：用当前 `UI_LANG` 报错并列出 `zh/en/ja/es/fr/ko`。
