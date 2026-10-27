<div align="center">

<h1>🧠 Second Brain Skill</h1>

<p><strong>나만의 AI 세컨드 브레인을 구축하세요</strong></p>

<p>
  <a href="https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f">Karpathy의 LLM Wiki 구상</a>에서 영감을 받은, 지속적으로 발전하는 지식 베이스를 위한 가볍고 확장 가능한 기반입니다.
</p>

<p>
  <a href="https://github.com/ChavesLiu/second-brain-skill/stargazers"><img src="https://img.shields.io/github/stars/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHub 스타 수"></a>
  <a href="https://github.com/ChavesLiu/second-brain-skill/network/members"><img src="https://img.shields.io/github/forks/ChavesLiu/second-brain-skill?style=flat-square" alt="GitHub 포크 수"></a>
  <a href="../../LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue?style=flat-square" alt="MIT 라이선스"></a>
  <img src="https://img.shields.io/badge/Claude_Code-Skill-blueviolet?style=flat-square" alt="Claude Code Skill">
</p>

<p><a href="../../README.md">中文</a> | <a href="../../README.en.md">English</a> | <a href="README.ja.md">日本語</a> | <a href="README.es.md">Español</a> | <a href="README.fr.md">Français</a> | <strong>한국어</strong></p>

</div>

---

## 개요

**Second Brain Skill**은 Andrej Karpathy의 LLM Wiki 구상에서 영감을 받은 오픈 소스 구현입니다. 흩어진 개인 정보를 구조화되고 서로 연결되며 지속적으로 발전하는 위키로 변환합니다.

누구나 쉽게 Fork하고 수정하여 자신만의 세컨드 브레인을 만들 수 있는 **작동하는 최소한의 확장 가능한 기반**을 제공합니다.

### 검색에서 지식 축적으로

**전통적인 RAG가 인터프리터에 가깝다면, Second Brain Skill은 컴파일러에서 영감을 받은 접근법을 사용합니다.** RAG가 주로 질의 시점에 정보를 검색하는 반면, 여기서는 LLM이 원본 자료를 구조화된 위키로 점진적으로 변환하고 출처, 엔터티, 개념 간 연결을 유지합니다.

**RAG는 지식을 검색하고, LLM Wiki는 지식을 구축합니다.**

사용자는 자료를 선택하고 좋은 질문을 던집니다. 요약, 상호 참조, 보관, 일관성 관리는 LLM이 담당합니다.

## 데모

원본 자료가 구조화되고 연결된 지식 베이스로 바뀌는 과정을 확인하세요.

![help → init → ingest → query 작업 흐름 데모](../images/guide.gif)

## 3계층 아키텍처

원본 자료, 구조화된 지식, 운영 규칙을 세 계층으로 분리합니다.

| 계층 | 위치 | 작성자 | 독자 | 내용 |
| --- | --- | --- | --- | --- |
| **원본 자료** | `raw/` | 사용자 | LLM | 논문, 기사, 메모, PDF, 이미지 |
| **지식 베이스** | `wiki/` | LLM | 사용자 | 요약, 엔터티, 개념, 분석, 상호 참조 |
| **명세** | `Skill` | 함께 발전 | LLM | SCHEMA, 워크플로, 스크립트 |

원본 자료를 유지하면서 지식 베이스와 운영 규칙을 독립적으로 발전시킬 수 있습니다.

## 빠른 시작

### 1. 설치

저장소를 클론합니다.

```bash
git clone https://github.com/ChavesLiu/second-brain-skill.git
```

Skill을 Claude Code의 전역 Skill 디렉터리로 복사합니다.

```bash
cp -r second-brain-skill/skills/wiki ~/.claude/skills/wiki
```

필요한 의존성을 설치합니다.

```bash
pip install -r ~/.claude/skills/wiki/scripts/requirements.txt
```

설치 후 다음 명령에서 명령어 목록이 보이면 성공입니다.

```text
/wiki help
```

### 2. 지식 베이스 초기화

```text
/wiki init
```

안내에 따라 경로, 이름, Wiki 페이지의 콘텐츠 언어(`zh` / `en`)를 선택합니다. 여기서 선택하는 언어는 생성되는 Wiki 콘텐츠의 언어이며, 이 README의 번역 언어 지원을 뜻하지 않습니다.

### 3. 첫 자료 수집

수집할 자료를 지식 베이스의 `raw/` 디렉터리에 둡니다.

```bash
cp my-article.md ~/my-kb/raw/
```

```text
/wiki ingest
```

LLM이 자료를 읽고 요약 페이지를 만들며 엔터티와 개념을 추출하고 상호 참조를 관리합니다. 자료에 따라 한 번에 10~15개 페이지를 생성하거나 갱신할 수 있습니다.

### 4. 지식 검색

```text
/wiki query Memex란 무엇인가요?
```

```text
RAG 방식과 Wiki 방식의 장단점을 비교해 줘
```

자연어로 질문할 수도 있습니다. LLM은 축적된 지식을 연결하여 답변합니다.

## 핵심 명령어

| 명령어 | 기능 |
| --- | --- |
| `/wiki help` | 사용 가능한 명령어와 사용법 표시 |
| `/wiki init` | 지식 베이스 생성 및 등록 |
| `/wiki ingest` | 새 자료 수집(Markdown, PDF, 이미지) |
| `/wiki query <question>` | 지식 베이스 기반 질의응답 |
| `/wiki lint` | 지식 베이스 상태 및 일관성 검사 |
| `/wiki wipe` | Wiki 페이지 삭제 또는 초기화(`wiki/.trash/`에서 복구 가능, `raw/`는 변경하지 않음) |
| `/wiki test` | 자동 테스트 실행 |

모든 명령어는 자연어로도 실행할 수 있으므로 별도 명령어를 외울 필요가 없습니다.

## 자연어 모드

Skill이 의도를 파악해 해당 작업을 실행합니다.

| 사용자 요청 | 실행 작업 |
| --- | --- |
| “이 기사 수집해 줘” | 자료 수집 |
| “Memex가 뭐야?” | 지식 베이스 검색 |
| “RAG와 Wiki를 비교해 줘” | 관련 지식 검색 및 종합 |
| “항상 출처를 표시해 줘” | `conventions.md`에 선호 설정 기록 |
| “지식 베이스 점검해 줘” | 상태 검사 |

OpenClaw와 같은 대화형 인터페이스에서도 자연스럽게 사용할 수 있습니다.

## Obsidian 연동

Markdown 지식 베이스를 [Obsidian](https://obsidian.md/)에서 열어 그래프, 백링크, 페이지를 탐색할 수 있습니다.

![Obsidian에서 지식 그래프를 보는 예](../images/obsidian.png)

권장 플러그인:

- **Front Matter Title** — frontmatter의 제목을 그래프 노드에 표시(사전 설정)
- **Dataview** — frontmatter 기반 메타데이터 검색
- **Web Clipper** — 웹 문서를 `raw/`에 저장

## OpenClaw(Web)

OpenClaw에서도 사용할 수 있지만, 바로 동작하는 것은 아닙니다. Skill 파일과 지식 베이스를 OpenClaw가 접근할 수 있는 위치에 두고, `registries.json`의 경로를 맞추며, OpenClaw Memory에 자동 수집 규칙을 설정해야 합니다. WeChat 기사 링크 등을 자동으로 수집하려면 링크를 열어 PDF로 저장할 수 있는 브라우저 조작 도구(예: Playwright)나 다운로드 수단도 OpenClaw 환경에서 사용할 수 있어야 합니다.

![OpenClaw에 링크를 보내 지식 베이스로 수집하는 예](../images/openclaw-wiki.gif)

자세한 내용은 [사용자 가이드(영어) — OpenClaw 연동](../user-guide.en.md#openclaw-integration)을 참고하세요.

## 지식 베이스 디렉터리 구조

일반적인 지식 베이스는 다음과 같은 디렉터리 구조를 가집니다.

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

| 경로 | 설명 |
| --- | --- |
| `~/my-kb/` | 지식 베이스 루트 디렉터리 |
| `raw/` | 사용자가 넣는 원본 자료. LLM은 읽기 전용으로 취급합니다 |
| `raw/assets/` | 이미지와 첨부 파일 |
| `wiki/` | LLM이 생성하고 유지하는 지식 베이스 |
| `wiki/index.md` | 콘텐츠 색인 |
| `wiki/log.md` | 작업 로그 |
| `wiki/overview.md` | 개요 페이지 |
| `wiki/conventions.md` | 사용 규칙과 선호 설정 |
| `wiki/sources/` | 원본 자료 요약 페이지 |
| `wiki/entities/` | 인물, 조직, 도구 등 엔터티 페이지 |
| `wiki/concepts/` | 이론, 방법, 패턴 등 개념 페이지 |
| `wiki/analyses/` | 비교와 종합 등 분석 페이지 |

## 삭제와 초기화에 대해

Wiki 콘텐츠 페이지를 삭제하거나 초기화하면 `wiki/.trash/`로 이동하며, `/wiki wipe restore`로 복구할 수 있습니다. `raw/`의 원본 자료는 변경하지 않습니다. `/wiki wipe empty-trash`는 확인 후 휴지통을 영구적으로 비웁니다. 이후에는 Git 이력에 저장된 콘텐츠만 Git을 통해 복구할 수 있습니다.

## 활용 사례

- **연구** — 논문을 지속적으로 수집해 분야별 지식 네트워크 구축
- **독서** — 책을 장별로 정리하고 인물과 주제 연결
- **개인 성장** — 일기, 기사, 팟캐스트 메모 정리
- **경쟁사 분석** — 경쟁사 동향 추적 및 비교 분석 갱신
- **팀 지식 베이스** — 회의록과 프로젝트 문서 관리

## Fork하여 나만의 버전 만들기

Second Brain Skill은 완성된 제품이 아니라 **출발점**입니다. 지식 구조, 워크플로, 규칙을 필요에 맞게 수정하여 연구 도우미나 팀 지식 시스템을 만들 수 있습니다. **Fork하고, 맞춤화하고, 나만의 세컨드 브레인을 만드세요.** 피드백과 기여를 환영합니다.

## 문서

- **[사용자 가이드(영어)](../user-guide.en.md)** — 설치, 기능, Obsidian, OpenClaw
- **[설계 철학(중국어)](../../skills/wiki/IDEA.md)** — Karpathy의 LLM Wiki에서 영감을 받은 원칙
- **[Skill 기술 문서(영어)](../../skills/wiki/README.en.md)** — 페이지 명세, 워크플로, 구조

## 감사의 말

- [Andrej Karpathy](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) — 이 프로젝트에 영감을 준 LLM Wiki 구상을 제안해 주셔서 감사합니다.

- [Vannevar Bush](https://en.wikipedia.org/wiki/Vannevar_Bush) — 1945년 연상형 개인 지식 관리의 선구적 개념인 Memex를 제안했습니다.

## 스타 기록

[![스타 기록 차트](https://api.star-history.com/chart?repos=chavesliu/second-brain-skill&type=date&legend=top-left)](https://www.star-history.com/?repos=chavesliu%2Fsecond-brain-skill&type=date&legend=top-left)

## 라이선스

이 프로젝트는 [MIT License](../../LICENSE)에 따라 배포됩니다.
