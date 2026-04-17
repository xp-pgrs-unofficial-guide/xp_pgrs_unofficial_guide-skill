---
name: xp-pgrs-unofficial-guide
description: >
  Access the XP PGRS Unofficial Guide (西浦博士生非官方攻略), a community-written
  handbook for PhD students at Xi'an Jiaotong-Liverpool University (XJTLU).
  Covers essential resources, welfare benefits, the APR process, meeting records,
  admin procedures, university facilities, and more.
  Activate this skill when the user asks about XJTLU PhD student affairs,
  regulations, welfare, or procedures.
compatibility:
  requires-bins:
    - python
metadata:
  author: xp-pgrs-unofficial-guide
  version: "1.0.0"
  language: zh-CN
  source: https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide
  license: see xp_pgrs_unofficial_guide/LICENSE
---

# XP PGRS Unofficial Guide — Skill Instructions

This skill gives you access to the **西浦博士生非官方攻略** (XP PGRS Unofficial
Guide), a community-maintained handbook for PhD students at XJTLU. The guide is
written in LaTeX and indexed for fast, low-token navigation.

> **Language note:** The guide is written in Simplified Chinese. Answer the user
> in their preferred language (default: match the language they used to ask).

---

## Step 1 — Locate the Skill Root

The skill root is the directory that contains this `SKILL.md` file. All relative
paths in these instructions are resolved from the skill root.

```
<skill-root>/
├── SKILL.md
├── cache/
│   └── guide_index.json          ← structural index (generated, fast to load)
├── scripts/
│   ├── check_submodule.py        ← ensures guide source is present
│   ├── check_version.py          ← compares cache vs. local git HEAD
│   └── build_index.py            ← (re)generates the index from LaTeX source
└── xp_pgrs_unofficial_guide/     ← guide source (LaTeX, cloned locally)
    ├── xp_pgrs_unofficial_guide.tex
    ├── chapters/
    ├── author-folder/
    └── figure/
```

---

## Step 2 — Ensure the Guide Source Is Present

Run:
```
python scripts/check_submodule.py
```

- Exits **0**: source is present. Proceed to Step 3.
- Exits **1**: source is missing and could not be cloned automatically.
  - Try cloning the guide yourself:
    ```
    git clone --depth=1 https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide xp_pgrs_unofficial_guide
    ```
  - If that also fails, report both error messages to the user and ask them to
    resolve the issue (e.g. install Git, check network) before retrying.
  - Do **not** proceed to Step 3 until the source is confirmed present.

---

## Step 3 — Version Gate (cache-first)

Run:
```
python scripts/check_version.py
```

The script prints `FRESH` or `STALE` on the first line of its output.

**If `FRESH` (exit 0):**
Read `cache/guide_index.json`. Proceed directly to Step 5 — no LaTeX parsing
required.

**If `STALE` (exit 1):**
The local guide source has been updated since the last index build, or the cache
does not exist yet. Rebuild the index:
```
python scripts/build_index.py
```
Then read the freshly written `cache/guide_index.json` and proceed to Step 5.

---

## Step 4 — Understanding the Index

`cache/guide_index.json` is a compact structural map of the guide. **Load it
once and use it as your navigation reference for the rest of the conversation.**

### Structure

```json
{
  "schema_version": 1,
  "guide_version": "<git-sha>",
  "generated_at": "...",
  "source_url": "...",
  "chapters": [
    {
      "title": "这些必须得做，不然毕不了业",
      "chapter_file": "chapters/must-do.tex",
      "label": "must-do",
      "contents": [
        { "type": "input",  "path": "author-folder/Kai.Wu/APR.tex",      "section_title": "APR" },
        { "type": "inline", "section_title": "其他福利" }
      ]
    }
  ]
}
```

### Content types

Each item in `contents` is in **source order** and is one of:

| Type | Meaning | How to read the content |
|---|---|---|
| `"input"` | Content fragment in a separate file | Open `xp_pgrs_unofficial_guide/<path>` |
| `"inline"` | Content written directly in the chapter file | Open `xp_pgrs_unofficial_guide/<chapter_file>` |

Paths are relative to `xp_pgrs_unofficial_guide/` (the guide source root).

---

## Step 5 — Answer the User's Query

Use the index as a navigation map. **Do not read files you don't need.**

### For a broad overview request
Summarise the chapter list from the index (titles only). Do not open any
chapter or fragment files.

### For a specific question
1. Scan `chapters[].title` and `contents[].section_title` in the index to
   identify the most likely chapter(s) and section(s).
2. Open only the matching fragment file(s) (`type: "input"`) or the chapter
   file itself (`type: "inline"`) to read the actual content.
3. Large chapters can be processed one content item at a time.

### For a keyword search
Scan section titles in the index first. If ambiguous, open candidate files one
at a time and search their text.

Always **cite the source**: chapter title + section title + file path
(e.g. `chapters/fuli.tex → author-folder/Kai.Wu/fund.tex §会议经费`).

---

## Step 6 — Handle Images

Images appear as `\includegraphics[...]{<path>}` inside a `figure` environment:

1. **Find the caption**: look for `\caption{...}` in the same
   `\begin{figure}...\end{figure}` block. Use the caption text as the primary
   image description.
2. **If you have vision capability**: additionally view the image file. The path
   inside `\includegraphics{...}` is relative to `xp_pgrs_unofficial_guide/`.
3. **If you do not have vision capability**: surface the caption text and
   inform the user: *"[图片：<caption text>]"*
4. **If there is no caption**: tell the user that an uncaptioned image exists
   which cannot be described, and give them the filename so they can view it.

---

## Updating the Guide

The guide source is **not** automatically updated — the user controls their own
version. If the user asks for the latest content, run:

```
git -C xp_pgrs_unofficial_guide pull
```

After pulling, `check_version.py` will report `STALE` on the next run, and
`build_index.py` will rebuild the index automatically.

---

## Rules

1. **Never modify** any file inside `xp_pgrs_unofficial_guide/`. Read-only.
2. If the guide source cannot be obtained (Step 2 fails), **stop and report both
   error messages** to the user — do not proceed.
3. **Always cite** chapter title, section title, and file path.
4. **Match the user's language** in your answer (Chinese or English) unless they
   specify otherwise.
5. **Do not fabricate** guide content. If a topic is not covered, say so.
6. For large chapters, read **one content item at a time** to stay within
   context limits. Summarise each item before moving to the next.
