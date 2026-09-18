# Cross-platform agent skills marketplace example

This repository demonstrates how one canonical `SKILL.md` can be distributed to Codex, Claude Code, and compatible IDE agents from the same GitHub repository. The example skill is intentionally trivial; the useful part is the packaging.

## What is shared

There is exactly one implementation of the example skill:

```text
plugins/example-skills/skills/hello-marketplace/SKILL.md
```

Its scripts, references, and assets would also live inside that same skill directory. Platform adapters contain metadata only.

## Repository layout

```text
.
├── .agents/plugins/marketplace.json          # Codex catalog
├── .claude-plugin/marketplace.json           # Claude/IDE catalog
├── plugins/example-skills/
│   ├── plugin.json                           # Agent Plugins 1.0
│   ├── .codex-plugin/plugin.json             # Codex adapter
│   ├── .claude-plugin/plugin.json            # Claude adapter
│   └── skills/hello-marketplace/
│       ├── SKILL.md                          # canonical shared skill
│       └── agents/openai.yaml                # optional Codex UI metadata
├── scripts/validate_marketplace.py
└── DEMO.md
```

## Supported demonstration paths

| Client | Discovery adapter | Invocation |
| --- | --- | --- |
| Codex | `.agents/plugins/marketplace.json` and `.codex-plugin/plugin.json` | `$hello-marketplace` |
| Claude Code | `.claude-plugin/marketplace.json` and `.claude-plugin/plugin.json` | `/example-skills:hello-marketplace` |
| VS Code / GitHub Copilot | Agent Plugins `plugin.json`, or the Claude marketplace | `/hello-marketplace` or Configure Skills |

See [DEMO.md](DEMO.md) for local and GitHub-hosted walkthroughs.

## Validate the repository

```bash
python3 scripts/validate_marketplace.py
```

The validator checks that:

- Both marketplace catalogs reference the same plugin directory.
- Codex, Claude, and Agent Plugins manifests have matching names and versions.
- Every skill directory contains valid shared `name` and `description` frontmatter.
- No scaffold placeholders remain.

GitHub Actions runs the same validation on pushes and pull requests. Pull requests also run the SkillHawk security scan as an independent check.

## Add another shared skill

Add another directory below `plugins/example-skills/skills/`:

```text
plugins/example-skills/skills/my-skill/SKILL.md
```

Use only the portable frontmatter fields `name` and `description` unless you have verified that every target client accepts an additional field. Put platform-specific UI metadata in platform-specific sidecars rather than the canonical `SKILL.md`.

## Publish to GitHub

After accepting the local Xcode license if macOS Git requests it:

```bash
git add .
git commit -m "Add cross-platform skills marketplace demo"
gh repo create chatgpt_skills_test --source=. --public --push
```

Use `--private` instead of `--public` for a private demonstration.

## Scope

This demonstrates a shared skill across current Codex, Claude Code, and compatible Agent Plugins clients. Other IDE agents may need another thin discovery adapter, but they should not need a second copy of the skill logic.

## License

MIT
