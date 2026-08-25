import json
import re
from pathlib import Path


ROOT = Path(__file__).parents[1]
INSTALL_COMMAND = (
    'python3.11 -m pip install '
    '"git+https://github.com/jasoncaston/two-body-verify.git@v0.1.1"'
)


def test_marketplace_and_plugin_names_are_exact_and_stable():
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
    assert marketplace["name"] == "two-body-verify"
    assert marketplace["plugins"][0]["name"] == "two-body-verify"
    assert marketplace["plugins"][0]["source"] == "./"
    assert plugin["name"] == "two-body-verify"
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", plugin["name"])
    assert marketplace["plugins"][0]["version"] == "0.1.1"
    assert plugin["version"] == "0.1.1"


def test_plugin_skill_stays_verification_only():
    skill = (ROOT / "skills" / "verify-claims" / "SKILL.md").read_text(encoding="utf-8")
    assert "Run `two-body-verify" in skill
    assert "Do not edit the project." in skill
    assert "lesson" not in skill.lower()
    assert "curriculum" not in skill.lower()


def test_plugin_surfaces_name_the_package_prerequisite():
    skill = (ROOT / "skills" / "verify-claims" / "SKILL.md").read_text(encoding="utf-8")
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

    assert INSTALL_COMMAND in skill
    assert "command -v two-body-verify" in skill
    assert "ERROR: two-body-verify is not installed or not on PATH." in skill
    assert "requires the two-body-verify Python package installed and on PATH" in plugin[
        "description"
    ]
