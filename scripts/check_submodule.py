"""
check_submodule.py  (v2 — clone-if-missing)
--------------------------------------------
Ensures the xp_pgrs_unofficial_guide source directory is present locally.

If the directory is absent or empty, clones it from GitHub as a shallow clone:

    git clone --depth=1 <SOURCE_URL> xp_pgrs_unofficial_guide/

If the directory is already present, reports OK and exits immediately.
The existing local version is left as-is — no automatic pull is performed.

To update the guide to the latest version, run manually from the skill root:

    git -C xp_pgrs_unofficial_guide pull

After pulling, check_version.py will detect the version change and the agent
will rebuild the index automatically on next activation.

Exit codes:
    0  — source is present (or was cloned successfully)
    1  — source is missing and could not be cloned
"""

import os
import subprocess
import sys

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
SOURCE_DIR = os.path.join(SKILL_ROOT, "xp_pgrs_unofficial_guide")
SENTINEL_FILE = os.path.join(SOURCE_DIR, "xp_pgrs_unofficial_guide.tex")

SOURCE_URL = "https://github.com/xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide"


def source_is_present() -> bool:
    """Return True if the guide source sentinel file exists."""
    return os.path.isfile(SENTINEL_FILE)


def clone_source() -> bool:
    """
    Attempt to clone the guide source with a shallow clone.
    Returns True on success, False on failure.
    """
    print(f"[check_submodule] Source not found. Cloning from:\n  {SOURCE_URL}")
    try:
        result = subprocess.run(
            ["git", "clone", "--depth=1", SOURCE_URL, SOURCE_DIR],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print("[check_submodule] Clone successful.")
            if result.stdout.strip():
                print(result.stdout.strip())
            return True
        else:
            print("[check_submodule] ERROR: git clone failed.")
            if result.stderr.strip():
                print(result.stderr.strip())
            if result.stdout.strip():
                print(result.stdout.strip())
            return False
    except FileNotFoundError:
        print(
            "[check_submodule] ERROR: 'git' command not found.\n"
            "Please install Git and ensure it is on your PATH, then run:\n\n"
            f"    git clone --depth=1 {SOURCE_URL}\n\n"
            f"from the skill root directory:\n    {SKILL_ROOT}"
        )
        return False


def main() -> int:
    if source_is_present():
        print(f"[check_submodule] OK — guide source present at:\n  {SOURCE_DIR}")
        return 0

    success = clone_source()
    if success and source_is_present():
        return 0

    print(
        "\n[check_submodule] FAILED — could not obtain the guide source.\n"
        "Please clone it manually from the skill root directory:\n\n"
        f"    git clone --depth=1 {SOURCE_URL}\n\n"
        f"Skill root: {SKILL_ROOT}"
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
