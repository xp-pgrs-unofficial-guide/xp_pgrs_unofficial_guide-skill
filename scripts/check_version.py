"""
check_version.py
----------------
Compares the guide version recorded in cache/guide_index.json with the
current local git HEAD of xp_pgrs_unofficial_guide/.

Prints one of:
    FRESH  — cache version matches local HEAD; no rebuild needed
    STALE  — cache is missing or behind local HEAD; run build_index.py

Exit codes:
    0  — FRESH
    1  — STALE
"""

import json
import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(SKILL_ROOT, "xp_pgrs_unofficial_guide")
CACHE_FILE = os.path.join(SKILL_ROOT, "cache", "guide_index.json")


def get_local_sha() -> str | None:
    """Return the current git HEAD SHA of the source directory, or None."""
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
    return None


def get_cached_version() -> str | None:
    """Read guide_version from cache/guide_index.json, or None if missing/corrupt."""
    if not os.path.isfile(CACHE_FILE):
        return None
    try:
        with open(CACHE_FILE, encoding="utf-8") as f:
            data = json.load(f)
        return data.get("guide_version")
    except Exception:
        return None


def main() -> int:
    local_sha = get_local_sha()
    cached_version = get_cached_version()

    if not local_sha:
        print("STALE")
        print("[check_version] Could not read local git HEAD.")
        print("[check_version] Is xp_pgrs_unofficial_guide/ a valid git repository?")
        print("[check_version] Run: python scripts/check_submodule.py")
        return 1

    if not cached_version:
        print("STALE")
        print("[check_version] No cache found — index has not been built yet.")
        print("[check_version] Run: python scripts/build_index.py")
        return 1

    if local_sha == cached_version:
        print("FRESH")
        print(f"[check_version] Cache is up to date (HEAD: {local_sha[:8]})")
        return 0

    print("STALE")
    print(f"[check_version] Cache version : {cached_version[:8]}")
    print(f"[check_version] Current HEAD  : {local_sha[:8]}")
    print("[check_version] Run: python scripts/build_index.py")
    return 1


if __name__ == "__main__":
    sys.exit(main())
