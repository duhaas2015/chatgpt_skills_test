#!/usr/bin/env python3
"""Validate the cross-platform marketplace demonstration."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
AGENT_PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    raise ValueError(message)


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"Missing required file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(value, dict):
        fail(f"Expected a JSON object in {path.relative_to(ROOT)}")
    return value


def frontmatter(skill_file: Path) -> dict[str, str]:
    text = skill_file.read_text(encoding="utf-8")
    if "[TODO:" in text:
        fail(f"Unfinished placeholder in {skill_file.relative_to(ROOT)}")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail(f"Missing YAML frontmatter in {skill_file.relative_to(ROOT)}")
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail(f"Unclosed YAML frontmatter in {skill_file.relative_to(ROOT)}")

    values: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def validate_shared_manifests(plugin_name: str, plugin_dir: Path) -> str:
    manifests = {
        "Codex": load_json(plugin_dir / ".codex-plugin" / "plugin.json"),
        "Claude": load_json(plugin_dir / ".claude-plugin" / "plugin.json"),
        "Agent Plugins": load_json(plugin_dir / "plugin.json"),
    }

    for client, manifest in manifests.items():
        if manifest.get("name") != plugin_name:
            fail(f"{client} manifest name does not match {plugin_name!r}")
        for field in ("version", "description", "author"):
            if not manifest.get(field):
                fail(f"{client} manifest for {plugin_name!r} is missing {field!r}")

    versions = {manifest["version"] for manifest in manifests.values()}
    if len(versions) != 1:
        fail(f"Manifest versions differ for {plugin_name!r}: {sorted(versions)}")
    descriptions = {manifest["description"] for manifest in manifests.values()}
    if len(descriptions) != 1:
        fail(f"Manifest descriptions differ for {plugin_name!r}")
    if manifests["Agent Plugins"].get("$schema") != AGENT_PLUGIN_SCHEMA:
        fail(f"Portable manifest for {plugin_name!r} has the wrong $schema")
    if not manifests["Codex"].get("interface"):
        fail(f"Codex manifest for {plugin_name!r} needs interface metadata")

    return versions.pop()


def validate_skills(plugin_name: str, plugin_dir: Path) -> None:
    skill_files = sorted((plugin_dir / "skills").glob("*/SKILL.md"))
    if not skill_files:
        fail(f"Plugin {plugin_name!r} has no skills")
    for skill_file in skill_files:
        metadata = frontmatter(skill_file)
        skill_name = skill_file.parent.name
        if metadata.get("name") != skill_name or not NAME_RE.fullmatch(skill_name):
            fail(f"Skill name does not match folder: {skill_file.relative_to(ROOT)}")
        if not metadata.get("description"):
            fail(f"Skill description is empty: {skill_file.relative_to(ROOT)}")


def validate() -> None:
    codex = load_json(CODEX_MARKETPLACE)
    claude = load_json(CLAUDE_MARKETPLACE)
    if not codex.get("name") or not claude.get("name"):
        fail("Both marketplaces need non-empty names")
    if not claude.get("owner", {}).get("name"):
        fail("Claude marketplace needs owner.name")

    codex_entries = codex.get("plugins")
    claude_entries = claude.get("plugins")
    if not isinstance(codex_entries, list) or not codex_entries:
        fail("Codex marketplace needs at least one plugin")
    if not isinstance(claude_entries, list) or not claude_entries:
        fail("Claude marketplace needs at least one plugin")
    claude_by_name = {entry.get("name"): entry for entry in claude_entries}

    for entry in codex_entries:
        name = entry.get("name", "")
        if not NAME_RE.fullmatch(name):
            fail(f"Invalid plugin name: {name!r}")
        expected_path = f"./plugins/{name}"
        if entry.get("source") != {"source": "local", "path": expected_path}:
            fail(f"Codex plugin {name!r} must use source path {expected_path!r}")
        policy = entry.get("policy", {})
        if policy.get("installation") not in {
            "NOT_AVAILABLE",
            "AVAILABLE",
            "INSTALLED_BY_DEFAULT",
        }:
            fail(f"Codex plugin {name!r} has invalid installation policy")
        if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            fail(f"Codex plugin {name!r} has invalid authentication policy")
        if not entry.get("category"):
            fail(f"Codex plugin {name!r} needs a category")

        claude_entry = claude_by_name.get(name)
        if not claude_entry:
            fail(f"Claude marketplace is missing plugin {name!r}")
        if claude_entry.get("source") != expected_path:
            fail(f"Claude plugin {name!r} must use source path {expected_path!r}")

        plugin_dir = ROOT / "plugins" / name
        version = validate_shared_manifests(name, plugin_dir)
        if claude_entry.get("version") != version:
            fail(f"Claude marketplace version differs for plugin {name!r}")
        validate_skills(name, plugin_dir)

    extra_claude_plugins = set(claude_by_name) - {
        entry.get("name") for entry in codex_entries
    }
    if extra_claude_plugins:
        fail(f"Claude-only plugins are not demonstrated: {sorted(extra_claude_plugins)}")


if __name__ == "__main__":
    try:
        validate()
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
    print("Cross-platform marketplace validation passed.")
