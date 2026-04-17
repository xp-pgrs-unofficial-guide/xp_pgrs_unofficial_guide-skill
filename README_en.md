# XP PGRS Unofficial Guide Agent Skill

English Version | [中文版](./README.md)

This is a Skill designed specifically for large language model (LLM) Agents (e.g., personal assistants based on the OpenClaw protocol). It allows the Agent to efficiently and accurately access and retrieve information from the [XP PGRS Unofficial Guide](https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide).

## 🌟 Core Features

- **Zero-Intervention Compatibility**: Requires absolutely no modification to the original LaTeX project code, preserving the original book's PDF generation workflow intact.
- **Cache-First Architecture**: Avoids the high token costs of making the Agent re-read and parse complex LaTeX source code during every conversation. This skill generates an extremely lightweight structural index locally.
- **Precision Targeting**: By analyzing the `\include` and `\input` structure of the source project, the Agent will only read minimal fragment contents exactly when needed to answer specific questions.
- **Dynamic Updates**: Automatically detects the source code version. When it detects an update in the local LaTeX source, it prompts the Agent to rebuild the index.

## 🏗️ Architecture

```text
xp_pgrs_unofficial_guide-skill/
├── SKILL.md                       ← Skill entry document (contains YAML frontmatter and Agent instructions)
├── cache/
│   └── guide_index.json           ← Auto-generated structural cache index (extremely small, token-friendly)
├── scripts/
│   ├── check_submodule.py         ← Environment init: handles cloning the original guide project locally
│   ├── check_version.py           ← Version gateway: compares local cache index with source Git HEAD
│   ├── update_skill.py            ← Skill auto-update: handles safely pulling and applying skill codebase updates
│   └── build_index.py             ← Parsing engine: parses multi-layered LaTeX source and condenses into a JSON index
└── xp_pgrs_unofficial_guide/      ← [Not directly committed] Dynamically cloned original guide codebase at runtime
```

### Agent Workflow

1. **Load Skill**: The Agent is triggered and reads `SKILL.md` in the background.
2. **Source Check**: The Agent runs `check_submodule.py` to ensure the original project is present.
3. **Lightning Verification**: The Agent runs `check_version.py`.
   - If it returns `FRESH`, it means the index is up-to-date, and the Agent directly loads the lightweight `cache/guide_index.json`.
   - If it returns `STALE`, the Agent calls `build_index.py` to rebuild the index and load the new one.
4. **Follow the Map**: The Agent uses the loaded structural index to determine which chapter and corresponding `author-folder` fragment file the user's question belongs to.
5. **Precision Reading**: The Agent opens and reads this fragment file to output an answer for the user with precise citations.

## 🚀 Installation & Usage

Since this is a standard Agent Skill directory, you only need to mount or place this entire folder into your Agent's (e.g., OpenClaw) `skills` directory.

The Agent will automatically decide when to invoke this skill based on the `description` field at the top of `SKILL.md`.

**Prerequisites**: The runtime environment must have `python` (pure Python 3 support, no third-party library dependencies) and `git`.

## 🔄 Manually Updating the Guide Source

Because this skill leaves control of pulling the project entirely to the user, the Agent defaults to using the content you currently have pulled locally to reply. If you want to update the handbook to the community's latest version, simply navigate strictly into the corresponding folder within this skill's root and execute a standard git pull command:

```bash
git -C xp_pgrs_unofficial_guide pull
```

In the subsequent conversation, the Agent's routine `check_version.py` check will immediately spot the changes (returning `STALE`) and automatically trigger a seamless index rebuild.

## 🤖 Skill Auto-Update

In addition to the underlying guide data, the "skill logic" used by the Agent for parsing (i.e., the Python scripts and codes within this repository) will also iteratively evolve. You can either directly ask the Agent to execute it for you, or manually run:

```bash
python scripts/update_skill.py
```

This tool will automatically compare versions against the remote and download updates. It is **absolutely safe** and will never overwrite your local `cache` index or `xp_pgrs_unofficial_guide` LaTeX source files.
