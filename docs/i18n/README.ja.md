<div align="center">

<h1>🧠 Second Brain Skill</h1>

<p><strong>AIで育てる、あなただけのセカンドブレイン</strong></p>

<p>
  <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">KarpathyのLLM Wiki構想</a>に着想を得た、進化し続ける知識ベースを構築するための軽量で拡張可能な基盤です。
</p>

<p>
  <a href="https://github.com/ChavesLiu/second-brain-skill/stargazers"><img src="https://img.shields.io/github/stars/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHubスター数"></a>
  <a href="https://github.com/ChavesLiu/second-brain-skill/network/members"><img src="https://img.shields.io/github/forks/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHubフォーク数"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MITライセンス"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=flat-square" alt="Claude Code Skill">
</p>

<p><a href="../../README.md">中文</a> | <a href="../../README.en.md">English</a> | <strong>日本語</strong> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <a href="README.ko.md">한국어</a></p>

</div>

---

## 概要

**Second Brain Skill** は、Andrej KarpathyのLLM Wiki構想に着想を得たオープンソースの実装です。散在する個人の情報を、構造化され相互に関連付けられた、継続的に進化するWikiへ変換します。

開発者が簡単にForkし、カスタマイズして独自のセカンドブレインを作れるよう、**小さく実用的で拡張可能な基盤**を提供します。

### 検索から知識の蓄積へ

**従来のRAGはインタープリタのように動作し、Second Brain Skillはコンパイラに着想を得たアプローチを採用します。** 従来のRAGが主に問い合わせ時に情報を検索するのに対し、このプロジェクトではLLMが原資料を構造化Wikiへ段階的に変換し、出典・エンティティ・概念の関係を維持します。

**RAGは知識を検索する。LLM Wikiは知識を育てる。**

あなたは資料を選び、良い質問をするだけ。要約、相互参照、アーカイブ、整合性の維持はLLMが担当します。

## デモ

資料が構造化された知識ベースへ変わる流れをご覧ください。

![help → init → ingest → queryの操作デモ](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/guide.gif)

## 3層アーキテクチャ

原資料、構造化された知識、運用ルールを3層に分離します。

| 層 | 場所 | 書き手 | 読み手 | 内容 |
| --- | --- | --- | --- | --- |
| **原資料** | `raw/` | あなた | LLM | 論文、記事、メモ、PDF、画像 |
| **知識ベース** | `wiki/` | LLM | あなた | 要約、エンティティ、概念、分析、相互参照 |
| **仕様** | `Skill` | 共同で更新 | LLM | SCHEMA、ワークフロー、スクリプト |

原資料を変更せずに、知識ベースと運用ルールを独立して進化させられます。

## クイックスタート

### 1. インストール

リポジトリをクローンします。

```bash
git clone https://github.com/ChavesLiu/second-brain-skill.git
```

SkillをClaude CodeのグローバルSkillディレクトリへコピーします。

```bash
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki
```

必要な依存関係をインストールします。

```bash
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

インストール後、以下でコマンド一覧が表示されれば成功です。

```text
/wiki help
```

### 2. 知識ベースの初期化

```text
/wiki init
```

画面の案内に従い、保存先、名前、Wikiページの内容言語（`zh` / `en`）を選択します。ここで選ぶ言語は、生成されるWikiコンテンツの言語です。このREADMEの翻訳言語を切り替えるものではありません。

### 3. 最初の資料を取り込む

取り込みたい資料を知識ベースの`raw/`ディレクトリに置きます。

```bash
cp my-article.md ~/my-kb/raw/
```

```text
/wiki ingest
```

LLMが資料を読み、要約ページを生成し、エンティティや概念を抽出して相互参照を維持します。資料によっては一度に10〜15ページが作成・更新されます。

### 4. 知識を検索する

```text
/wiki query Memexとは何ですか？
```

```text
RAG方式とWiki方式の長所・短所を比較して
```

自然言語で質問することもできます。LLMは蓄積された知識ベースを使って関連情報を結び付け、回答します。

## 主なコマンド

| コマンド | 機能 |
| --- | --- |
| `/wiki help` | 利用できるコマンドと使い方を表示 |
| `/wiki init` | 知識ベースを作成・登録 |
| `/wiki ingest` | 新しい資料を取り込む（Markdown、PDF、画像） |
| `/wiki query <question>` | 知識ベースに基づいて回答 |
| `/wiki lint` | 知識ベースの健全性と整合性を確認 |
| `/wiki wipe` | Wikiページを削除・リセット（`wiki/.trash/`から復元可能、`raw/`は変更しない） |
| `/wiki test` | 自動テストを実行 |

すべてのコマンドは自然言語でも実行できます。専用コマンドを覚える必要はありません。

## 自然言語モード

Skillが意図を判定して適切な処理を実行します。

| 入力例 | 実行内容 |
| --- | --- |
| 「この記事を取り込んで」 | 資料を取り込む |
| 「Memexとは？」 | 知識ベースを検索 |
| 「RAGとWikiを比較して」 | 関連知識を検索して統合 |
| 「回答には必ず出典を付けて」 | `conventions.md` に設定を保存 |
| 「知識ベースをチェックして」 | 健全性を確認 |

OpenClawなどの会話型インターフェースでも自然に操作できます。

## Obsidianとの連携

Markdown形式の知識ベースを[Obsidian](https://obsidian.md/)で直接開き、知識グラフ、バックリンク、ページ内容を閲覧できます。

![Obsidianで知識グラフを閲覧する例](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/obsidian.png)

推奨プラグイン：

- **Front Matter Title** — frontmatterのタイトルをグラフのノードに表示（設定済み）
- **Dataview** — frontmatterを使ったメタデータ検索
- **Web Clipper** — ブラウザから記事を`raw/`へ保存

## OpenClaw（Web）

OpenClawでも利用できますが、追加設定なしですぐに使えるわけではありません。Skillファイルと知識ベースをOpenClawから参照できる場所に置き、`registries.json`のパスを合わせ、OpenClawのMemoryに自動収録ルールを設定する必要があります。WeChat記事リンクなどを自動で取り込むには、リンクを開いてPDF化・保存できるブラウザ操作ツール（例：Playwright）やダウンロード手段もOpenClaw環境で利用可能にしておく必要があります。

![OpenClawでリンクを送って知識ベースに取り込む例](https://raw.githubusercontent.com/ChavesLiu/second-brain-skill/refs/heads/main/docs/images/openclaw-wiki.gif)

詳細は[ユーザーガイド（英語）— OpenClaw連携](../user-guide.en.md#openclaw-integration)を参照してください。

## 知識ベースのディレクトリ構造

典型的な知識ベースは、次のようなディレクトリ構造になります。

```text
~/my-kb/
├── raw/
│   ├── assets/
│   └── *.md / *.pdf
└── wiki/
    ├── index.md
    ├── log.md
    ├── overview.md
    ├── conventions.md
    ├── sources/
    ├── entities/
    ├── concepts/
    └── analyses/
```

| パス | 説明 |
| --- | --- |
| `~/my-kb/` | 知識ベースのルートディレクトリ |
| `raw/` | あなたが置く原資料。LLMは読み取り専用として扱います |
| `raw/assets/` | 画像や添付ファイル |
| `wiki/` | LLMが生成・保守する知識ベース |
| `wiki/index.md` | 内容インデックス |
| `wiki/log.md` | 操作ログ |
| `wiki/overview.md` | 概要ページ |
| `wiki/conventions.md` | 利用上の約束や好み |
| `wiki/sources/` | 原資料の要約ページ |
| `wiki/entities/` | 人物・組織・ツールなどのエンティティページ |
| `wiki/concepts/` | 理論・手法・パターンなどの概念ページ |
| `wiki/analyses/` | 比較・統合などの分析ページ |

## 削除とリセットについて

Wikiの内容ページを削除・リセットすると`wiki/.trash/`へ移動され、`/wiki wipe restore`で復元できます。`raw/`の原資料は変更しません。`/wiki wipe empty-trash`は確認後にごみ箱を完全に空にします。その後は、Gitの履歴に保存済みの内容だけをGitから復元できます。

## ユースケース

- **研究** — 論文を継続的に取り込み、分野別の知識ネットワークを構築
- **読書** — 章ごとに読み込み、登場人物、テーマ、概念を関連付ける
- **自己成長** — 日記、記事、ポッドキャストのメモを整理
- **競合分析** — 競合の動向を追跡し、比較分析を更新
- **チーム知識ベース** — 議事録やプロジェクト文書を整理・維持

## Forkして自分だけのものを作る

Second Brain Skillは完成品ではなく、**出発点**です。知識構造、ワークフロー、運用ルールを自由に変更し、研究アシスタントやチーム向け知識システムを作れます。**Forkして、カスタマイズして、自分だけのセカンドブレインを構築しましょう。** フィードバックや貢献を歓迎します。

## ドキュメント

- **[ユーザーガイド（英語）](../user-guide.en.md)** — インストール、機能、Obsidian、OpenClaw
- **[設計思想（中国語）](../../skills/wiki/IDEA.md)** — KarpathyのLLM Wikiから着想を得た設計原則
- **[Skill技術ドキュメント（英語）](../../skills/wiki/README.en.md)** — ページ仕様、ワークフロー、構造

## 謝辞

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — LLM Wiki構想を提唱し、本プロジェクトに着想を与えたことに感謝します。

- [Vannevar Bush](https://en.wikipedia.org/wiki/Vannevar_Bush) — 1945年にMemexを構想し、連想型の個人知識管理の先駆けとなりました。

## スター履歴

[![スター履歴チャート](https://api.star-history.com/chart?repos=chavesliu/second-brain-skill&type=date&legend=top-left)](https://www.star-history.com/?repos=chavesliu%2Fsecond-brain-skill&type=date&legend=top-left)

## ライセンス

このプロジェクトは[MIT License](../../LICENSE)の下で公開されています。
