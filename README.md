# XP PGRS Unofficial Guide Agent Skill

这是一个专为大语言模型 Agent（如基于 OpenClaw 协议的个人助理）设计的技能（Skill）。它允许 Agent 高效、准确地访问和检索[西浦博士生非官方攻略](https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide)（XP PGRS Unofficial Guide）。

## 🌟 核心特性

- **零干预兼容**：完全不需要修改原始的 LaTeX 项目代码，保持原书用于生成 PDF 的工作流不受影响。
- **Cache-first（缓存优先）架构**：告别每次对话都让 Agent 重新阅读和解析复杂的 LaTeX 源码带来的高额 Token 消耗。本技能会在本地生成一份极其轻量级的结构索引。
- **精确定位**：通过分析源项目的 `\include` 和 `\input` 结构，Agent 只会在需要回答特定问题时，精准读取极小部分的切片内容。
- **动态更新**：自动检测源码版本，当探测到本地 LaTeX 源码更新后，会提示 Agent 重新构建索引。

## 🏗️ 架构组成

```text
xp_pgrs_unofficial_guide-skill/
├── SKILL.md                       ← 技能入口文档（包含 YAML frontmatter 和 Agent 操作指南）
├── cache/
│   └── guide_index.json           ← 自动生成的指南结构化缓存索引（极小，Token 友好）
├── scripts/
│   ├── check_submodule.py         ← 环境初始化：负责将原始指南项目克隆到本地
│   ├── check_version.py           ← 版本网关：对比本地 cache 索引与源码 Git HEAD
│   └── build_index.py             ← 解析引擎：将三层 LaTeX 源码解析并提浓缩为 JSON 索引
└── xp_pgrs_unofficial_guide/      ← [不直接提交] 运行时动态 Clone 的原始指南代码库
```

### Agent 的工作流

1. **载入技能**：Agent 被触发并在后台读取 `SKILL.md`。
2. **源码检查**：Agent 运行 `check_submodule.py` 确保原始项目的存在。
3. **极速验证**：Agent 运行 `check_version.py`。
   - 如果返回 `FRESH`，意味着索引最新，Agent 直接加载轻量的 `cache/guide_index.json`。
   - 如果返回 `STALE`，Agent 调用 `build_index.py` 重建索引并加载新索引。
4. **按图索骥**：Agent 使用载入的结构索引来判断用户的问题位于哪个章节及对应的 `author-folder` 碎片文件中。
5. **精准打击**：Agent 打开并阅读这个碎片文件，为用户输出带有精确引用的回答。

## 🚀 安装与使用

由于这是一个标准的 Agent Skill 目录，你只需要将这整个文件夹挂载或放置到你的 Agent（如 OpenClaw）的 `skills` 目录之中即可。

Agent 会依靠 `SKILL.md` 顶部的 `description` 字段自动判断何时应当调用本技能。

**前置依赖**：运行环境中必须带有 `python`（纯 Python3 支持，无第三方库依赖）和 `git`。

## 🔄 手动更新指南数据

由于本技能将项目的拉取控制权交给了用户自身，Agent 默认使用你目前拉下来的内容进行回复。如果你想更新手册到社区的最新版本，只需要进入本技能根目录对应的文件夹执行普通的 git 更新命令：

```bash
git -C xp_pgrs_unofficial_guide pull
```

在随后的下一次对话中，Agent 的 `check_version.py` 例行检查会立刻发现变动（返回 `STALE`），并自动启动无缝的索引重组。
