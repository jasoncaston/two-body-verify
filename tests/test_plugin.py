import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_marketplace_and_plugin_names_are_exact_and_stable():
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert marketplace["name"] == "two-body-verify"
    assert marketplace["plugins"][0]["name"] == "two-body-verify"
    assert marketplace["plugins"][0]["source"] == "./"
    assert plugin["name"] == "two-body-verify"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", plugin["name"])


def test_plugin_skill_stays_verification_only():
    skill = (ROOT / "skills" / "verify-claims" / "SKILL.md").read_text(encoding="utf-8")
    assert "Run `two-body-verify" in skill
    assert "Do not edit the project." in skill
    assert "lesson" not in skill.lower()
    assert "curriculum" not in skill.lower()
