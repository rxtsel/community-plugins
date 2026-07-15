from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).with_name("validate-plugins.py")
SPEC = importlib.util.spec_from_file_location("validate_plugins", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
validate_plugins = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validate_plugins)


class LauncherPrefixTests(unittest.TestCase):
    def validate_prefix(self, prefix: str) -> list[str]:
        validator = validate_plugins.Validator(Path("/repo"))
        validator.validate_launcher_fields(
            Path("/repo/example/plugin.toml"),
            "launcher_provider[0]",
            {"prefix": prefix},
        )
        return validator.errors

    def test_accepts_lowercase_ascii_letters(self) -> None:
        self.assertEqual(self.validate_prefix("bla"), [])

    def test_rejects_leading_symbol(self) -> None:
        self.assertNotEqual(self.validate_prefix("/bla"), [])

    def test_rejects_uppercase_letters(self) -> None:
        self.assertNotEqual(self.validate_prefix("Bla"), [])

    def test_rejects_digits(self) -> None:
        self.assertNotEqual(self.validate_prefix("bla2"), [])

    def test_rejects_other_symbols(self) -> None:
        self.assertNotEqual(self.validate_prefix("bla-bla"), [])


class AllowedTagsTests(unittest.TestCase):
    def validate_tags(self, tags: object) -> list[str]:
        validator = validate_plugins.Validator(Path("/repo"))
        validator.validate_tags(Path("/repo/example/plugin.toml"), tags)
        return validator.errors

    def test_accepts_every_allowed_tag(self) -> None:
        self.assertEqual(self.validate_tags(sorted(validate_plugins.ALLOWED_TAGS)), [])

    def test_rejects_unknown_tag(self) -> None:
        self.assertEqual(
            self.validate_tags(["utility", "unknown"]),
            [
                "example/plugin.toml: root: "
                "tags[1] 'unknown' is not an allowed tag"
            ],
        )

    def test_rejects_wrong_case(self) -> None:
        self.assertNotEqual(self.validate_tags(["Utility"]), [])

    def test_retains_string_list_validation(self) -> None:
        errors = self.validate_tags(["utility", "utility", ""])
        self.assertTrue(any("duplicate 'utility'" in error for error in errors))
        self.assertTrue(any("tags[2] must be a non-empty string" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
