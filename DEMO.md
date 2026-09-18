# Five-minute cross-platform demo

The point of this repository is packaging, not the behavior of the example skill. Every client below ultimately loads the same file:

```text
plugins/example-skills/skills/hello-marketplace/SKILL.md
```

## Codex

Register this checkout and install its example plugin:

```bash
codex plugin marketplace add .
codex plugin add example-skills@personal
```

Start a new Codex task and enter:

```text
Use $hello-marketplace to demonstrate the shared skill.
```

## Claude Code

From Claude Code, register this checkout and install the plugin:

```text
/plugin marketplace add .
/plugin install example-skills@github-skills-test
```

Invoke the namespaced skill:

```text
/example-skills:hello-marketplace
```

## VS Code with GitHub Copilot

Enable Agent Plugins with the `chat.plugins.enabled` setting. For a local demonstration, add the absolute plugin directory to your user settings:

```json
{
  "chat.plugins.enabled": true,
  "chat.pluginLocations": {
    "/absolute/path/to/chatgpt_skills_test/plugins/example-skills": true
  }
}
```

Reload VS Code, open Chat, and select `hello-marketplace` from **Configure Skills** or the `/` menu.

After publishing this repository on GitHub, you can instead add the marketplace to VS Code settings:

```json
{
  "chat.plugins.enabled": true,
  "chat.plugins.marketplaces": [
    "YOUR_GITHUB_USERNAME/chatgpt_skills_test"
  ]
}
```

Then find `example-skills` in the Extensions view using `@agentPlugins` and install it.

## Expected result

Each client should produce a response beginning with:

```text
Shared marketplace skill loaded successfully.
```

The invocation syntax and manifests differ, but the loaded skill file is identical.
