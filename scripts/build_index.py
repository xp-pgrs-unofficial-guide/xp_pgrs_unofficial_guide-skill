"""
build_index.py
--------------
Parses the xp_pgrs_unofficial_guide LaTeX project and writes a compact
structural index to cache/guide_index.json.

The index records:
  - Chapter titles, labels, and chapter file paths
  - The ordered content structure of each chapter:
      - "input" entries: path to a fragment file + its first \\section{} title
      - "inline" entries: \\section{} titles written directly in the chapter file

Full prose content is NOT stored — agents read individual .tex files on demand,
using the index purely as a navigation map.

Run this script any time the guide source is updated (check_version.py will
report STALE to signal that a rebuild is needed).
"""

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(SKILL_ROOT, "xp_pgrs_unofficial_guide")
ENTRY_POINT = os.path.join(SOURCE_DIR, "xp_pgrs_unofficial_guide.tex")
CACHE_DIR = os.path.join(SKILL_ROOT, "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "guide_index.json")

SOURCE_URL = "https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide"

# ---------------------------------------------------------------------------
# File reading
# ---------------------------------------------------------------------------


def read_file(path: str) -> list:
    """Read a file, trying UTF-8 first, then falling back to latin-1."""
    for enc in ("utf-8", "utf-8-sig", "latin-1"):
        try:
            with open(path, encoding=enc) as f:
                return f.readlines()
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    return []


# ---------------------------------------------------------------------------
# LaTeX helpers
# ---------------------------------------------------------------------------


def is_commented(line: str) -> bool:
    """Return True if the line is a LaTeX comment (starts with %)."""
    return line.strip().startswith("%")


def extract_command(line: str, command: str):
    """
    Extract the content of \\command{...} from a line.
    Returns the matched string, or None if not found.
    """
    m = re.search(r"\\" + re.escape(command) + r"\{([^}]+)\}", line)
    return m.group(1) if m else None


# ---------------------------------------------------------------------------
# Git version
# ---------------------------------------------------------------------------


def get_git_sha() -> str:
    """Return the current git HEAD SHA of SOURCE_DIR, or 'unknown'."""
    try:
        result = subprocess.run(
            ["git", "-C", SOURCE_DIR, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except FileNotFoundError:
        pass
    return "unknown"


# ---------------------------------------------------------------------------
# Entry-point parser
# ---------------------------------------------------------------------------


def parse_entry_point() -> list:
    """
    Parse xp_pgrs_unofficial_guide.tex and return the list of active chapter
    file paths (relative to SOURCE_DIR, with .tex added if missing).
    Skips \\include lines that are commented out with %.
    """
    chapters = []
    for line in read_file(ENTRY_POINT):
        if is_commented(line):
            continue
        m = re.search(r"\\include\{([^}]+)\}", line)
        if m:
            path = m.group(1)
            if not path.endswith(".tex"):
                path += ".tex"
            chapters.append(path)
    return chapters


# ---------------------------------------------------------------------------
# Fragment helper
# ---------------------------------------------------------------------------


def get_fragment_section_title(fragment_rel_path: str):
    """
    Return the first \\section{} title found in a fragment file
    (path relative to SOURCE_DIR), or None.
    """
    full_path = os.path.join(SOURCE_DIR, fragment_rel_path)
    for line in read_file(full_path):
        if is_commented(line):
            continue
        title = extract_command(line, "section")
        if title:
            return title
    return None


# ---------------------------------------------------------------------------
# Chapter parser
# ---------------------------------------------------------------------------


def parse_chapter(chapter_rel_path: str):
    """
    Parse a chapter file and return its structural descriptor dict:

        {
            "title":        str,            # from \\chapter{}
            "chapter_file": str,            # path relative to SOURCE_DIR
            "label":        str | None,     # from \\label{} (first after \\chapter)
            "contents": [
                {"type": "input",  "path": str, "section_title": str | None},
                {"type": "inline", "section_title": str},
                ...
            ]
        }

    "contents" is in source order, interleaving \\input fragment references
    with inline \\section headings written directly in the chapter file.
    """
    full_path = os.path.join(SOURCE_DIR, chapter_rel_path)
    lines = read_file(full_path)
    if not lines:
        print(f"  [WARN] Could not read: {chapter_rel_path}")
        return None

    chapter_title = None
    chapter_label = None
    contents = []
    # Inline \\section titles accumulated between consecutive \\input calls
    pending_inline_sections = []

    for line in lines:
        stripped = line.strip()
        if is_commented(stripped):
            continue

        # \\chapter{...} — capture title
        title = extract_command(stripped, "chapter")
        if title:
            chapter_title = title
            continue

        # \\label{...} — capture label (first one after \\chapter)
        if chapter_title and chapter_label is None:
            label_val = extract_command(stripped, "label")
            if label_val:
                chapter_label = label_val
                continue

        # \\input{...} — flush inline buffer then record the fragment
        m = re.search(r"\\input\{([^}]+)\}", stripped)
        if m:
            # Flush pending inline sections before this \input
            for sec in pending_inline_sections:
                contents.append({"type": "inline", "section_title": sec})
            pending_inline_sections = []

            inp_path = m.group(1)
            # Skip placeholder paths that don't resolve to real files
            # (e.g. example code in author-instruction.tex)
            if not os.path.isfile(os.path.join(SOURCE_DIR, inp_path)):
                continue
            section_title = get_fragment_section_title(inp_path)
            entry = {"type": "input", "path": inp_path}
            if section_title:
                entry["section_title"] = section_title
            contents.append(entry)
            continue

        # Inline \\section{...} — buffer it
        sec_title = extract_command(stripped, "section")
        if sec_title:
            pending_inline_sections.append(sec_title)

    # Flush any remaining inline sections at end of file
    for sec in pending_inline_sections:
        contents.append({"type": "inline", "section_title": sec})

    return {
        "title": chapter_title,
        "chapter_file": chapter_rel_path,
        "label": chapter_label,
        "contents": contents,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    print("[build_index] Starting guide index build ...")

    if not os.path.isfile(ENTRY_POINT):
        print(f"[build_index] ERROR: Entry point not found: {ENTRY_POINT}")
        print("[build_index] Run scripts/check_submodule.py first to obtain the guide source.")
        return 1

    guide_version = get_git_sha()
    sha_display = guide_version[:8] if guide_version != "unknown" else "unknown"
    print(f"[build_index] Guide version (git HEAD): {sha_display}")

    chapter_paths = parse_entry_point()
    print(f"[build_index] Found {len(chapter_paths)} active chapters.")

    chapters = []
    for path in chapter_paths:
        print(f"  Parsing: {path}")
        chapter = parse_chapter(path)
        if chapter:
            chapters.append(chapter)

    index = {
        "schema_version": 1,
        "guide_version": guide_version,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "chapters": chapters,
    }

    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    print(f"[build_index] Index written to: {CACHE_FILE}")
    print(f"[build_index] Done. {len(chapters)} chapters indexed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
