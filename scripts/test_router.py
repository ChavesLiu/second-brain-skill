#!/usr/bin/env python3
"""wiki router 的 stdlib unittest 覆盖。"""

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROUTER_PATH = Path(__file__).resolve().parents[1] / "skills" / "wiki" / "scripts" / "router.py"


def load_router():
    spec = importlib.util.spec_from_file_location("wiki_router_under_test", ROUTER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


router = load_router()


class RouterTestCase(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.skill_dir = self.root / "skill"
        self.skill_dir.mkdir()
        self.settings_file = self.skill_dir / "settings.json"
        self.registries_file = self.skill_dir / "registries.json"
        self.kb_root = self.root / "kb"
        self.kb_root.mkdir()
        self.patcher = mock.patch.multiple(
            router,
            SKILL_DIR=self.skill_dir,
            SETTINGS_FILE=self.settings_file,
            REGISTRIES_FILE=self.registries_file,
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.tempdir.cleanup()

    def write_settings(self, data):
        self.settings_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def write_registries(self, data):
        self.registries_file.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def single_registry(self, language=None):
        kb = {"name": "Main", "path": str(self.kb_root)}
        if language is not None:
            kb["language"] = language
        return {"default": None, "registries": {"main": kb}}

    def test_first_run_needs_language_for_all_six_retry_ok(self):
        for code in router.SUPPORTED_LANGUAGES:
            with self.subTest(code=code):
                if self.settings_file.exists():
                    self.settings_file.unlink()
                first = router.safe_route(["query", "hello"])
                self.assertEqual(first["status"], "needs_language")
                self.assertEqual(first["original_args"], ["query", "hello"])
                self.assertIn(code, first["supported_languages"])

                second = router.safe_route(["language", code])
                self.assertEqual(second["status"], "ok")
                self.assertEqual(second["ui_lang"], code)
                self.assertEqual(json.loads(self.settings_file.read_text(encoding="utf-8"))["interaction_language"], code)

                self.write_registries(self.single_registry())
                retry = router.safe_route(["query", "hello"])
                self.assertEqual(retry["status"], "ok")
                self.assertEqual(retry["ui_lang"], code)

    def test_original_args_for_init_and_query_and_empty_help(self):
        self.assertEqual(router.safe_route([])["original_args"], [])
        self.assertEqual(router.safe_route(["init"])["original_args"], ["init"])
        self.assertEqual(router.safe_route(["query", "a", "b"])["original_args"], ["query", "a", "b"])

    def test_help_and_language_without_config_do_not_read_registry(self):
        self.registries_file.write_text("{bad", encoding="utf-8")
        self.assertEqual(router.safe_route([])["status"], "needs_language")
        self.assertEqual(router.safe_route(["language"])["status"], "needs_language")

        self.write_settings({"interaction_language": "en"})
        self.assertEqual(router.safe_route([])["status"], "ok")
        lang = router.safe_route(["language"])
        self.assertEqual(lang["status"], "ok")
        self.assertEqual(lang["interaction_language"], "en")

    def test_no_kb_single_multi_default_and_select(self):
        self.write_settings({"interaction_language": "zh"})

        self.write_registries({"default": None, "registries": {}})
        self.assertEqual(router.safe_route(["query", "x"])["status"], "no_kb")

        self.write_registries(self.single_registry(language="ja"))
        single = router.safe_route(["query", "x"])
        self.assertEqual(single["status"], "ok")
        self.assertEqual(single["kb"]["lang"], "ja")

        kb2 = self.root / "kb2"
        kb2.mkdir()
        self.write_registries(
            {
                "default": "two",
                "registries": {
                    "one": {"name": "One", "path": str(self.kb_root)},
                    "two": {"name": "Two", "path": str(kb2)},
                },
            }
        )
        defaulted = router.safe_route(["query", "x"])
        self.assertEqual(defaulted["status"], "ok")
        self.assertTrue(defaulted["multiple_kbs"])
        self.assertEqual(defaulted["kb"]["id"], "two")

        self.write_registries(
            {
                "default": None,
                "registries": {
                    "one": {"name": "One", "path": str(self.kb_root)},
                    "two": {"name": "Two", "path": str(kb2)},
                },
            }
        )
        self.assertEqual(router.safe_route(["query", "x"])["status"], "select")

    def test_multilingual_kb_selection_preserves_language(self):
        self.write_settings({"interaction_language": "ko"})
        kb2 = self.root / "kb2"
        kb2.mkdir()
        registries = {
            "default": None,
            "registries": {
                "one": {"name": "One", "path": str(self.kb_root), "language": "ja"},
                "two": {"name": "Two", "path": str(kb2), "language": "fr"},
            },
        }
        self.write_registries(registries)
        selected = router.safe_route(["query", "Memex?"])
        self.assertEqual(selected["status"], "select")
        self.assertEqual(selected["ui_lang"], "ko")
        self.assertEqual([kb["lang"] for kb in selected["kb_list"]], ["ja", "fr"])
        registries["default"] = "two"
        self.write_registries(registries)
        resumed = router.safe_route(["query", "Memex?"])
        self.assertEqual(resumed["status"], "ok")
        self.assertEqual(resumed["kb"]["lang"], "fr")
        self.assertEqual(resumed["ui_lang"], "ko")
        self.assertEqual(resumed["args"], "Memex?")
        registries["registries"]["one"]["language"] = "de"
        self.write_registries(registries)
        self.assertEqual(router.safe_route(["query", "Memex?"])["status"], "error")

    def test_invalid_values_bad_structures_and_bad_registry_json_error(self):
        self.write_settings({"interaction_language": "de"})
        self.assertEqual(router.safe_route(["query", "x"])["status"], "error")

        self.settings_file.write_text("[]", encoding="utf-8")
        self.assertEqual(router.safe_route(["query", "x"])["status"], "error")

        self.settings_file.write_text("{bad", encoding="utf-8")
        self.assertEqual(router.safe_route(["query", "x"])["status"], "error")

        self.write_settings({"interaction_language": "zh"})
        self.registries_file.write_text("{bad", encoding="utf-8")
        self.assertEqual(router.safe_route(["query", "x"])["status"], "error")

        self.write_registries([])
        self.assertEqual(router.safe_route(["query", "x"])["status"], "error")

    def test_invalid_language_commands_do_not_change_files(self):
        self.write_settings({"interaction_language": "en"})
        self.write_registries(self.single_registry(language="fr"))
        before = self.settings_file.read_bytes()
        registry_before = self.registries_file.read_bytes()
        for args in (["language", "de"], ["language", "ja", "extra"]):
            with self.subTest(args=args):
                self.assertEqual(router.safe_route(args)["status"], "error")
                self.assertEqual(self.settings_file.read_bytes(), before)
        router.safe_route(["language", "ja"])
        self.assertEqual(self.registries_file.read_bytes(), registry_before)

    def test_corrupt_config_is_not_overwritten(self):
        for content in (b"null", b"[]", b"{bad", b"\xff", b'{"interaction_language": null}'):
            with self.subTest(content=content):
                self.settings_file.write_bytes(content)
                self.assertEqual(router.safe_route(["language", "ja"])["status"], "error")
                self.assertEqual(self.settings_file.read_bytes(), content)

    def test_failed_update_preserves_existing_settings(self):
        self.write_settings({"interaction_language": "en"})
        before = self.settings_file.read_bytes()
        with mock.patch.object(router.os, "replace", side_effect=OSError("boom")):
            self.assertEqual(router.safe_route(["language", "fr"])["status"], "error")
        self.assertEqual(self.settings_file.read_bytes(), before)
        self.assertEqual(list(self.skill_dir.glob(".settings.json.*.tmp")), [])

    def test_missing_language_field_prompts_once(self):
        self.write_settings({"theme": "dark"})
        self.assertEqual(router.safe_route(["init"])["status"], "needs_language")
        router.safe_route(["language", "ko"])
        for args in ([], ["help"], ["init"], ["language"]):
            self.assertEqual(router.safe_route(args)["status"], "ok")
        self.assertEqual(json.loads(self.settings_file.read_text())["theme"], "dark")

    def test_write_failure_and_temp_cleanup(self):
        with mock.patch.object(router.os, "replace", side_effect=OSError("boom")):
            result = router.safe_route(["language", "fr"])
        self.assertEqual(result["status"], "error")
        self.assertFalse(self.settings_file.exists())
        self.assertEqual(list(self.skill_dir.glob(".settings.json.*.tmp")), [])

    def test_permission_errors_are_explicit(self):
        self.write_settings({"interaction_language": "zh"})
        with mock.patch("builtins.open", side_effect=PermissionError("denied")):
            result = router.safe_route(["query", "x"])
        self.assertEqual(result["status"], "error")
        self.assertIn("权限", result["message"])

        with mock.patch.object(router.tempfile, "mkstemp", side_effect=PermissionError("denied")):
            result = router.safe_route(["language", "ko"])
        self.assertEqual(result["status"], "error")
        self.assertIn("权限", result["message"])

    def test_unknown_fields_preserved(self):
        self.write_settings({"interaction_language": "zh", "theme": "dark", "nested": {"x": 1}})
        result = router.safe_route(["language", "en"])
        self.assertEqual(result["status"], "ok")
        saved = json.loads(self.settings_file.read_text(encoding="utf-8"))
        self.assertEqual(saved["interaction_language"], "en")
        self.assertEqual(saved["theme"], "dark")
        self.assertEqual(saved["nested"], {"x": 1})

    def test_existing_kb_language_not_overridden_and_legacy_default_zh(self):
        self.write_settings({"interaction_language": "ko"})
        self.write_registries(self.single_registry(language="fr"))
        result = router.safe_route(["query", "x"])
        self.assertEqual(result["ui_lang"], "ko")
        self.assertEqual(result["kb"]["lang"], "fr")

        self.write_registries(self.single_registry())
        result = router.safe_route(["query", "x"])
        self.assertEqual(result["kb"]["lang"], "zh")

    def test_preserve_query_args_and_init_lang(self):
        self.write_settings({"interaction_language": "es"})
        self.write_registries(self.single_registry())
        result = router.safe_route(["query", "keep", "these", "args"])
        self.assertEqual(result["args"], "keep these args")
        self.assertEqual(result["workflow"], "workflows/query.md")

        init = router.safe_route(["init"])
        self.assertEqual(init["ui_lang"], "es")
        self.assertEqual(init["init_lang"], "es")
        self.assertIsNone(init["kb"])


if __name__ == "__main__":
    unittest.main()
