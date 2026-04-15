#!/usr/bin/env python3
"""
Second Brain 确定性健康检查脚本。
用代码检测结构性问题，输出 JSON 供 /wiki lint 使用。

用法:
    python lint.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw
    python lint.py --wiki-dir /path/to/kb/wiki --raw-dir /path/to/kb/raw --json
"""

import argparse
import re
import sys
import json
import yaml
from pathlib import Path
from collections import defaultdict

REQUIRED_FRONTMATTER = {"title", "type", "created", "updated", "tags"}
VALID_TYPES = {"source", "entity", "concept", "analysis", "overview", "conventions"}
SPECIAL_PAGES = {"index.md", "log.md"}

# 由命令行参数设置
WIKI_DIR: Path
RAW_DIR: Path

# ---------- helpers ----------

def parse_frontmatter(filepath: Path) -> tuple[dict | None, str]:
    """返回 (frontmatter_dict, body_text)。解析失败返回 (None, full_text)。"""
    text = filepath.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?\n)---\n(.*)", text, re.DOTALL)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1))
        return fm if isinstance(fm, dict) else None, m.group(2)
    except yaml.YAMLError:
        return None, text


def extract_wikilinks(text: str) -> list[str]:
    """提取所有 [[target]] 或 [[target|alias]] 中的 target。"""
    return re.findall(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", text)


def resolve_wikilink(target: str) -> Path | None:
    """将 wikilink target 解析为 wiki/ 下的文件路径。"""
    for subdir in ["sources", "entities", "concepts", "analyses", ""]:
        candidate = WIKI_DIR / subdir / f"{target}.md" if subdir else WIKI_DIR / f"{target}.md"
        if candidate.exists():
            return candidate
    return None


def get_wiki_pages() -> list[Path]:
    """获取所有 wiki 页面（排除 index.md 和 log.md）。"""
    pages = []
    for f in WIKI_DIR.rglob("*.md"):
        if f.name not in SPECIAL_PAGES:
            pages.append(f)
    return sorted(pages)


def page_id(filepath: Path) -> str:
    """从文件路径提取 wikilink 可用的 ID（如 concepts/memex.md → memex）。"""
    return filepath.stem


# ---------- checks ----------

def check_broken_links(pages: list[Path]) -> list[dict]:
    """P0: 检查断链 — [[link]] 指向不存在的 wiki 页面。"""
    issues = []
    all_ids = {p.stem for p in pages}

    for page in pages:
        _, body = parse_frontmatter(page)
        full_text = page.read_text(encoding="utf-8")
        links = extract_wikilinks(full_text)
        for target in links:
            if target.startswith("raw/"):
                continue
            if target not in all_ids:
                issues.append({
                    "level": "P0",
                    "type": "broken_link",
                    "file": str(page.relative_to(WIKI_DIR)),
                    "detail": f"[[{target}]] 指向不存在的页面",
                })
    return issues


def check_raw_wikilinks(pages: list[Path]) -> list[dict]:
    """P0: 检查 [[raw/...]] wikilinks — 应使用普通 Markdown 链接。"""
    issues = []
    for page in pages:
        text = page.read_text(encoding="utf-8")
        matches = re.findall(r"\[\[(raw/[^\]|]+)(?:\|[^\]]+)?\]\]", text)
        for m in matches:
            issues.append({
                "level": "P0",
                "type": "raw_wikilink",
                "file": str(page.relative_to(WIKI_DIR)),
                "detail": f"[[{m}]] 应改为普通 Markdown 链接，避免图谱虚影节点",
            })
    return issues


def check_frontmatter(pages: list[Path]) -> list[dict]:
    """P0: 检查 frontmatter 完整性。"""
    issues = []
    for page in pages:
        fm, _ = parse_frontmatter(page)
        rel = str(page.relative_to(WIKI_DIR))
        if fm is None:
            issues.append({
                "level": "P0",
                "type": "no_frontmatter",
                "file": rel,
                "detail": "缺少 YAML frontmatter",
            })
            continue
        missing = REQUIRED_FRONTMATTER - set(fm.keys())
        if missing:
            issues.append({
                "level": "P0",
                "type": "incomplete_frontmatter",
                "file": rel,
                "detail": f"缺少字段: {', '.join(sorted(missing))}",
            })
        if fm.get("type") and fm["type"] not in VALID_TYPES:
            issues.append({
                "level": "P1",
                "type": "invalid_type",
                "file": rel,
                "detail": f"type '{fm['type']}' 不在合法值 {VALID_TYPES} 中",
            })
    return issues


def check_index_consistency(pages: list[Path]) -> list[dict]:
    """P0: 检查 index.md 与实际文件的一致性。"""
    issues = []
    index_path = WIKI_DIR / "index.md"
    if not index_path.exists():
        issues.append({
            "level": "P0",
            "type": "missing_index",
            "file": "index.md",
            "detail": "index.md 不存在",
        })
        return issues

    index_text = index_path.read_text(encoding="utf-8")
    index_refs = set(re.findall(r"\]\(([^)]+\.md)\)", index_text))

    content_pages = set()
    for page in pages:
        rel = str(page.relative_to(WIKI_DIR))
        if rel in ("overview.md",):
            continue
        if any(rel.startswith(d) for d in ("sources/", "entities/", "concepts/", "analyses/")):
            content_pages.add(rel)

    for ref in index_refs:
        full_path = WIKI_DIR / ref
        if not full_path.exists() and ref != "overview.md":
            issues.append({
                "level": "P0",
                "type": "index_dangling",
                "file": "index.md",
                "detail": f"索引引用 {ref} 但文件不存在",
            })

    for rel in content_pages:
        if rel not in index_refs:
            issues.append({
                "level": "P0",
                "type": "index_missing",
                "file": "index.md",
                "detail": f"文件 {rel} 存在但未在索引中列出",
            })

    return issues


def check_bidirectional_links(pages: list[Path]) -> list[dict]:
    """P1: 检查双向链接 — 如果 A 的 Related 链接到 B，B 的 Related 也应链接到 A。"""
    issues = []
    related_links = {}
    page_map = {p.stem: p for p in pages}

    for page in pages:
        text = page.read_text(encoding="utf-8")
        pid = page.stem
        related_match = re.search(r"## Related\n(.*?)(?:\n## |\Z)", text, re.DOTALL)
        if not related_match:
            continue
        related_section = related_match.group(1)
        targets = extract_wikilinks(related_section)
        related_links[pid] = set(targets)

    checked = set()
    for pid, targets in related_links.items():
        for target in targets:
            pair = tuple(sorted([pid, target]))
            if pair in checked:
                continue
            checked.add(pair)

            if target in related_links and pid not in related_links[target]:
                if target in page_map:
                    issues.append({
                        "level": "P1",
                        "type": "missing_reverse_link",
                        "file": str(page_map[target].relative_to(WIKI_DIR)),
                        "detail": f"Related 区块缺少到 [[{pid}]] 的反向链接（{pid} 已链接到此页）",
                    })

    return issues


def check_orphan_pages(pages: list[Path]) -> list[dict]:
    """P1: 检查孤岛页面 — 无任何入站链接（除 index.md 和 overview.md 外）。"""
    issues = []
    incoming = defaultdict(set)

    for page in pages:
        text = page.read_text(encoding="utf-8")
        pid = page.stem
        links = extract_wikilinks(text)
        for target in links:
            incoming[target].add(pid)

    for special in ("index.md", "overview.md"):
        sp = WIKI_DIR / special
        if sp.exists():
            for target in extract_wikilinks(sp.read_text(encoding="utf-8")):
                incoming[target].add(f"__{special}__")

    for page in pages:
        pid = page.stem
        rel = str(page.relative_to(WIKI_DIR))
        if rel == "overview.md":
            continue
        real_incoming = {s for s in incoming.get(pid, set()) if not s.startswith("__")}
        if not real_incoming:
            issues.append({
                "level": "P1",
                "type": "orphan_page",
                "file": rel,
                "detail": f"孤岛页面，没有其他 wiki 页面链接到此",
            })

    return issues


def check_sources_field(pages: list[Path]) -> list[dict]:
    """P1: 检查 entity/concept 页面是否有 sources 字段。"""
    issues = []
    for page in pages:
        fm, _ = parse_frontmatter(page)
        if fm is None:
            continue
        ptype = fm.get("type", "")
        if ptype in ("entity", "concept") and not fm.get("sources"):
            issues.append({
                "level": "P1",
                "type": "missing_sources",
                "file": str(page.relative_to(WIKI_DIR)),
                "detail": f"type={ptype} 但缺少 sources 字段（应标注引用的原始素材）",
            })
    return issues


# ---------- main ----------

def run_all_checks() -> list[dict]:
    pages = get_wiki_pages()
    issues = []
    issues += check_broken_links(pages)
    issues += check_raw_wikilinks(pages)
    issues += check_frontmatter(pages)
    issues += check_index_consistency(pages)
    issues += check_bidirectional_links(pages)
    issues += check_orphan_pages(pages)
    issues += check_sources_field(pages)
    level_order = {"P0": 0, "P1": 1, "P2": 2}
    issues.sort(key=lambda x: (level_order.get(x["level"], 9), x["file"]))
    return issues


def main():
    parser = argparse.ArgumentParser(description="Second Brain 健康检查")
    parser.add_argument("--wiki-dir", required=True, help="wiki 目录的绝对路径")
    parser.add_argument("--raw-dir", required=True, help="raw 目录的绝对路径")
    parser.add_argument("--json", action="store_true", dest="output_json", help="输出 JSON 格式")
    args = parser.parse_args()

    global WIKI_DIR, RAW_DIR
    WIKI_DIR = Path(args.wiki_dir).resolve()
    RAW_DIR = Path(args.raw_dir).resolve()

    if not WIKI_DIR.exists():
        print(f"错误: wiki 目录不存在: {WIKI_DIR}", file=sys.stderr)
        sys.exit(2)

    issues = run_all_checks()

    if args.output_json:
        print(json.dumps(issues, ensure_ascii=False, indent=2))
        return

    pages = get_wiki_pages()
    p0 = [i for i in issues if i["level"] == "P0"]
    p1 = [i for i in issues if i["level"] == "P1"]
    p2 = [i for i in issues if i["level"] == "P2"]

    print(f"Wiki 健康检查 — {WIKI_DIR}")
    print(f"共 {len(pages)} 个页面\n")

    if not issues:
        print("✅ 未发现问题！")
        return

    if p0:
        print(f"🔴 P0 — 需要修复 ({len(p0)})")
        for i in p0:
            print(f"  [{i['type']}] {i['file']}: {i['detail']}")
        print()

    if p1:
        print(f"🟡 P1 — 建议改进 ({len(p1)})")
        for i in p1:
            print(f"  [{i['type']}] {i['file']}: {i['detail']}")
        print()

    if p2:
        print(f"🟢 P2 — 可选优化 ({len(p2)})")
        for i in p2:
            print(f"  [{i['type']}] {i['file']}: {i['detail']}")
        print()

    print(f"总计: {len(p0)} P0 / {len(p1)} P1 / {len(p2)} P2")

    if p0:
        sys.exit(1)


if __name__ == "__main__":
    main()
