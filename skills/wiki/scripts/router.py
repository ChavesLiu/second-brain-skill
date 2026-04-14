#!/usr/bin/env python3
"""
Second Brain 确定性路由脚本。
解析子命令、选择知识库、输出路径变量，让 LLM 跳过路由直接进入工作流。

用法:
    python router.py ingest
    python router.py ingest paper.pdf
    python router.py query "Memex 是什么？"
    python router.py lint
    python router.py wipe all
    python router.py init
    python router.py help

输出 JSON:
    {
        "status": "ok",
        "subcommand": "ingest",
        "args": "paper.pdf",
        "workflow": "workflows/ingest.md",
        "schema": "SCHEMA.md",
        "kb": {
            "id": "ai-research",
            "name": "AI 研究",
            "root": "/path/to/kb",
            "wiki": "/path/to/kb/wiki",
            "raw": "/path/to/kb/raw",
            "lang": "zh"
        }
    }

多知识库时输出 status=select，附带候选列表让 LLM 询问用户。
"""

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRIES_FILE = SKILL_DIR / "registries.json"

VALID_SUBCOMMANDS = {"init", "ingest", "query", "lint", "wipe", "test", "help"}

# 不需要 KB 选择的子命令
NO_KB_REQUIRED = {"init", "help"}

# 需要读 SCHEMA.md 的子命令（会创建/修改 wiki 页面）
NEEDS_SCHEMA = {"ingest", "query", "lint", "wipe"}


def load_registries() -> dict:
    if not REGISTRIES_FILE.exists():
        return {"default": None, "registries": {}}
    with open(REGISTRIES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def make_kb_info(kb_id: str, kb_data: dict) -> dict:
    root = kb_data["path"]
    return {
        "id": kb_id,
        "name": kb_data["name"],
        "root": root,
        "wiki": f"{root}/wiki",
        "raw": f"{root}/raw",
        "lang": kb_data.get("language", "zh"),
    }


def route(args: list[str]) -> dict:
    # 解析子命令
    if not args:
        return {
            "status": "ok",
            "subcommand": "help",
            "args": "",
            "workflow": None,
            "schema": None,
            "kb": None,
            "skill_dir": str(SKILL_DIR),
        }

    subcommand = args[0].lower()
    remaining = " ".join(args[1:]) if len(args) > 1 else ""

    if subcommand not in VALID_SUBCOMMANDS:
        return {
            "status": "error",
            "message": f"未知子命令: {subcommand}",
            "valid_subcommands": sorted(VALID_SUBCOMMANDS),
            "skill_dir": str(SKILL_DIR),
        }

    result = {
        "status": "ok",
        "subcommand": subcommand,
        "args": remaining,
        "workflow": f"workflows/{subcommand}.md" if subcommand not in ("help",) else None,
        "schema": "SCHEMA.md" if subcommand in NEEDS_SCHEMA else None,
        "kb": None,
        "skill_dir": str(SKILL_DIR),
    }

    # help 和 init 不需要选库
    if subcommand in NO_KB_REQUIRED:
        return result

    # 需要选库的命令
    registries = load_registries()
    kbs = registries.get("registries", {})

    if not kbs:
        return {
            "status": "no_kb",
            "message": "尚未注册任何知识库。请先运行 /wiki init 创建一个知识库。",
            "skill_dir": str(SKILL_DIR),
        }

    if len(kbs) == 1:
        # 唯一知识库，自动选择
        kb_id = next(iter(kbs))
        kb_data = kbs[kb_id]

        # 验证路径存在
        root = Path(kb_data["path"])
        if not root.exists():
            return {
                "status": "error",
                "message": f"知识库路径不存在: {kb_data['path']}",
                "skill_dir": str(SKILL_DIR),
            }

        result["kb"] = make_kb_info(kb_id, kb_data)
        return result

    # 多个知识库，检查是否有 default
    default_id = registries.get("default")
    if default_id and default_id in kbs:
        # 有默认知识库，使用它但告知 LLM
        result["kb"] = make_kb_info(default_id, kbs[default_id])
        result["multiple_kbs"] = True
        result["kb_list"] = [
            {"id": kid, "name": kd["name"], "path": kd["path"], "is_default": kid == default_id}
            for kid, kd in kbs.items()
        ]
        return result

    # 多个知识库且无默认，需要 LLM 询问用户
    result["status"] = "select"
    result["message"] = "有多个知识库，请询问用户选择。"
    result["kb_list"] = [
        {"id": kid, "name": kd["name"], "path": kd["path"]}
        for kid, kd in kbs.items()
    ]
    return result


def main():
    result = route(sys.argv[1:])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
