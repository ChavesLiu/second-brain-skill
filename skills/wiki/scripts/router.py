#!/usr/bin/env python3
"""
Second Brain 确定性路由脚本。
解析子命令、选择知识库、输出路径变量，让 LLM 跳过路由直接进入工作流。
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
REGISTRIES_FILE = SKILL_DIR / "registries.json"
SETTINGS_FILE = SKILL_DIR / "settings.json"

VALID_SUBCOMMANDS = {"init", "ingest", "query", "lint", "wipe", "test", "help", "language"}

# 不需要 KB 选择、也不应读取注册表的子命令
NO_KB_REQUIRED = {"init", "help", "language"}

# 需要读 SCHEMA.md 的子命令（会创建/修改 wiki 页面）
NEEDS_SCHEMA = {"ingest", "query", "lint", "wipe"}

# 支持的 UI 交互语言集中在一个常量，便于 workflow 复用同一份能力边界。
SUPPORTED_LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "ja": "日本語",
    "es": "Español",
    "fr": "Français",
    "ko": "한국어",
}

LANGUAGE_PROMPTS = {
    "zh": "首次使用 /wiki 前，请先选择交互语言：zh/en/ja/es/fr/ko。",
    "en": "Before using /wiki for the first time, choose an interaction language: zh/en/ja/es/fr/ko.",
    "ja": "/wiki を初めて使う前に、対話言語を選択してください: zh/en/ja/es/fr/ko。",
    "es": "Antes de usar /wiki por primera vez, elige un idioma de interacción: zh/en/ja/es/fr/ko.",
    "fr": "Avant d’utiliser /wiki pour la première fois, choisissez une langue d’interaction : zh/en/ja/es/fr/ko.",
    "ko": "/wiki를 처음 사용하기 전에 상호작용 언어를 선택하세요: zh/en/ja/es/fr/ko.",
}


class RouterError(Exception):
    """可预期的路由错误，直接作为 JSON error 返回。"""


class LanguageNeeded(Exception):
    """缺少运行时交互语言配置。"""


def json_error(message: str, ui_lang: str | None = None, **extra: Any) -> dict:
    result = {
        "status": "error",
        "message": message,
        "ui_lang": ui_lang,
        "skill_dir": str(SKILL_DIR),
    }
    result.update(extra)
    return result


def load_json_file(path: Path, default: Any = None) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default
    except UnicodeError as exc:
        raise RouterError(f"文件编码无效: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RouterError(f"JSON 解析失败: {path}: {exc.msg}") from exc
    except PermissionError as exc:
        raise RouterError(f"没有权限读取文件: {path}") from exc
    except OSError as exc:
        raise RouterError(f"读取文件失败: {path}: {exc}") from exc


def load_registries() -> dict:
    registries = load_json_file(REGISTRIES_FILE, {"default": None, "registries": {}})
    if not isinstance(registries, dict):
        raise RouterError("注册表配置必须是 JSON object")
    kbs = registries.get("registries", {})
    if not isinstance(kbs, dict):
        raise RouterError("注册表 registries 字段必须是 JSON object")
    return registries


def validate_language(value: Any, field_name: str = "language") -> str:
    if not isinstance(value, str) or value not in SUPPORTED_LANGUAGES:
        raise RouterError(f"非法 {field_name}: {value!r}，仅支持 {', '.join(SUPPORTED_LANGUAGES)}")
    return value


def load_settings() -> dict | None:
    missing = object()
    settings = load_json_file(SETTINGS_FILE, missing)
    if settings is missing:
        return None
    if not isinstance(settings, dict):
        raise RouterError("settings.json 必须是 JSON object")
    if "interaction_language" in settings:
        validate_language(settings["interaction_language"], "interaction_language")
    return settings


def get_ui_lang(require_config: bool) -> str | None:
    settings = load_settings()
    if settings and "interaction_language" in settings:
        return settings["interaction_language"]
    if require_config:
        raise LanguageNeeded()
    return None


def needs_language_result(original_args: list[str], ui_lang: str | None = None) -> dict:
    # 缺配置时 ui_lang 没有可信来源，保持 null。
    prompt_lang = ui_lang if ui_lang in LANGUAGE_PROMPTS else "zh"
    return {
        "status": "needs_language",
        "message": LANGUAGE_PROMPTS[prompt_lang],
        "supported_languages": SUPPORTED_LANGUAGES,
        "original_args": original_args,
        "ui_lang": ui_lang,
        "skill_dir": str(SKILL_DIR),
    }


def write_settings_atomic(settings: dict) -> None:
    tmp_name: str | None = None
    try:
        SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(
            prefix=f".{SETTINGS_FILE.name}.",
            suffix=".tmp",
            dir=str(SETTINGS_FILE.parent),
            text=True,
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
                f.write("\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_name, SETTINGS_FILE)
            tmp_name = None
        except Exception:
            # fd 已由 fdopen 接管，异常时仅清理临时文件。
            raise
    except PermissionError as exc:
        raise RouterError(f"没有权限写入设置: {SETTINGS_FILE}") from exc
    except OSError as exc:
        raise RouterError(f"写入设置失败: {SETTINGS_FILE}: {exc}") from exc
    finally:
        if tmp_name:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
            except OSError:
                pass


def set_interaction_language(language: str) -> dict:
    validate_language(language, "interaction_language")
    settings = load_settings()
    if settings is None:
        settings = {}
    settings["interaction_language"] = language
    write_settings_atomic(settings)
    return {
        "status": "ok",
        "subcommand": "language",
        "args": language,
        "workflow": None,
        "schema": None,
        "kb": None,
        "ui_lang": language,
        "interaction_language": language,
        "supported_languages": SUPPORTED_LANGUAGES,
        "skill_dir": str(SKILL_DIR),
    }


def make_kb_info(kb_id: str, kb_data: dict) -> dict:
    if not isinstance(kb_data, dict):
        raise RouterError(f"知识库 {kb_id} 配置必须是 JSON object")
    for field in ("path", "name"):
        if not isinstance(kb_data.get(field), str) or not kb_data[field]:
            raise RouterError(f"知识库 {kb_id} 的 {field} 字段必须是非空字符串")
    root = kb_data["path"]
    name = kb_data["name"]
    validate_language(kb_data.get("language", "zh"), f"知识库 {kb_id} language")
    if not Path(root).is_dir():
        raise RouterError(f"知识库路径不存在或不是目录: {root}")

    return {
        "id": kb_id,
        "name": name,
        "root": root,
        "wiki": f"{root}/wiki",
        "raw": f"{root}/raw",
        # 已有 kb.language 不被 UI 语言覆盖；旧配置缺字段继续默认 zh。
        "lang": kb_data.get("language", "zh"),
    }


def make_base_result(subcommand: str, remaining: str, ui_lang: str | None) -> dict:
    result = {
        "status": "ok",
        "subcommand": subcommand,
        "args": remaining,
        "workflow": f"workflows/{subcommand}.md" if subcommand not in ("help", "language") else None,
        "schema": "SCHEMA.md" if subcommand in NEEDS_SCHEMA else None,
        "kb": None,
        "ui_lang": ui_lang,
        "skill_dir": str(SKILL_DIR),
    }
    if subcommand == "init":
        result["init_lang"] = ui_lang
    return result


def route(args: list[str]) -> dict:
    original_args = list(args)

    # 无参数等同 help，但首次仍要先收集交互语言。
    if not args:
        ui_lang = get_ui_lang(require_config=True)
        return make_base_result("help", "", ui_lang)

    subcommand = args[0].lower()
    remaining = " ".join(args[1:]) if len(args) > 1 else ""

    if subcommand not in VALID_SUBCOMMANDS:
        ui_lang = get_ui_lang(require_config=False)
        return json_error(
            f"未知子命令: {subcommand}",
            ui_lang=ui_lang,
            valid_subcommands=sorted(VALID_SUBCOMMANDS),
        )

    if subcommand == "language":
        if len(args) == 1:
            ui_lang = get_ui_lang(require_config=False)
            if ui_lang is None:
                return needs_language_result(original_args)
            return {
                "status": "ok",
                "subcommand": "language",
                "args": "",
                "workflow": None,
                "schema": None,
                "kb": None,
                "ui_lang": ui_lang,
                "interaction_language": ui_lang,
                "supported_languages": SUPPORTED_LANGUAGES,
                "skill_dir": str(SKILL_DIR),
            }
        if len(args) != 2:
            ui_lang = get_ui_lang(require_config=False)
            return json_error("language 命令只接受一个语言代码参数", ui_lang=ui_lang)
        return set_interaction_language(args[1])

    ui_lang = get_ui_lang(require_config=True)
    result = make_base_result(subcommand, remaining, ui_lang)

    # help 和 init 不需要选库，也不读取注册表。
    if subcommand in NO_KB_REQUIRED:
        return result

    registries = load_registries()
    kbs = registries.get("registries", {})

    if not kbs:
        return {
            "status": "no_kb",
            "message": "尚未注册任何知识库。请先运行 /wiki init 创建一个知识库。",
            "ui_lang": ui_lang,
            "skill_dir": str(SKILL_DIR),
        }

    if len(kbs) == 1:
        # 唯一知识库，自动选择。
        kb_id = next(iter(kbs))
        kb_data = kbs[kb_id]
        result["kb"] = make_kb_info(kb_id, kb_data)
        return result

    # 多个知识库，检查是否有 default。
    default_id = registries.get("default")
    if default_id is not None and not isinstance(default_id, str):
        raise RouterError("注册表 default 字段必须是字符串或 null")
    for kid, kd in kbs.items():
        if not isinstance(kd, dict) or not all(isinstance(kd.get(field), str) and kd[field] for field in ("name", "path")):
            raise RouterError(f"知识库 {kid} 配置必须包含非空 name/path 字符串")
        validate_language(kd.get("language", "zh"), f"知识库 {kid} language")
    if default_id and default_id in kbs:
        result["kb"] = make_kb_info(default_id, kbs[default_id])
        result["multiple_kbs"] = True
        result["kb_list"] = [
            {"id": kid, "name": kd["name"], "path": kd["path"], "lang": kd.get("language", "zh"), "is_default": kid == default_id}
            for kid, kd in kbs.items()
        ]
        return result

    # 多个知识库且无默认，需要 LLM 询问用户。
    result["status"] = "select"
    result["message"] = "有多个知识库，请询问用户选择。"
    result["kb_list"] = [
        {"id": kid, "name": kd["name"], "path": kd["path"], "lang": kd.get("language", "zh")}
        for kid, kd in kbs.items()
    ]
    return result


def safe_route(args: list[str]) -> dict:
    try:
        return route(args)
    except LanguageNeeded:
        return needs_language_result(list(args))
    except RouterError as exc:
        ui_lang: str | None = None
        try:
            settings = load_settings()
            if settings and isinstance(settings.get("interaction_language"), str):
                ui_lang = settings["interaction_language"]
        except Exception:
            ui_lang = None
        return json_error(str(exc), ui_lang=ui_lang)
    except PermissionError as exc:
        return json_error(f"权限错误: {exc}", ui_lang=None)


def main() -> None:
    result = safe_route(sys.argv[1:])
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
