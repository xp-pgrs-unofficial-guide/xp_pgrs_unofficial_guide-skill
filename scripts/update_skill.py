"""
update_skill.py
---------------
Checks if there is a newer version of xp_pgrs_unofficial_guide-skill available
on GitHub. If a newer version is found, it downloads the latest source ZIP
and updates the local files (SKILL.md, scripts, etc.), without touching the
cache directory or the xp_pgrs_unofficial_guide LaTeX source.
"""

import os
import re
import shutil
import sys
import tempfile
import urllib.request
import urllib.error
import zipfile

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILL_ROOT = os.path.dirname(SCRIPT_DIR)
SKILL_MD_PATH = os.path.join(SKILL_ROOT, "SKILL.md")

REPO = "xp-pgrs-unofficial-guide/xp_pgrs_unofficial_guide-skill"
RAW_SKILL_MD_URL = f"https://raw.githubusercontent.com/{REPO}/main/SKILL.md"
ZIP_URL = f"https://github.com/{REPO}/archive/refs/heads/main.zip"


def parse_version(v_str: str) -> tuple:
    """Safely parse a version string into a comparable tuple."""
    v_str = re.sub(r'^[^\d]+', '', v_str)
    parts = []
    for part in v_str.split("."):
        try:
            parts.append(int(part))
        except ValueError:
            parts.append(0)
    return tuple(parts)


def get_local_version() -> str:
    """Read local version from SKILL.md frontmatter."""
    if not os.path.isfile(SKILL_MD_PATH):
        return "0.0.0"
    
    with open(SKILL_MD_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    match = re.search(r'^\s*version:\s*"?([\d\.]+)"?', content, re.MULTILINE)
    if match:
        return match.group(1)
    return "0.0.0"


def get_remote_version() -> str | None:
    """Fetch remote SKILL.md and extract its version."""
    try:
        req = urllib.request.Request(RAW_SKILL_MD_URL, headers={'Cache-Control': 'no-cache'})
        with urllib.request.urlopen(req, timeout=10) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'^\s*version:\s*"?([\d\.]+)"?', content, re.MULTILINE)
            if match:
                return match.group(1)
            return "0.0.0"
    except urllib.error.URLError as e:
        print(f"[update_skill] Network error extracting remote version: {e}")
        return None


def download_and_extract_update() -> bool:
    """Download main.zip from GitHub, extract and overwrite skill files."""
    print(f"[update_skill] Downloading latest update from {ZIP_URL}...")
    try:
        req = urllib.request.Request(ZIP_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            zip_data = response.read()
    except Exception as e:
        print(f"[update_skill] Failed to download update zip: {e}")
        return False
    
    with tempfile.TemporaryDirectory() as tmpdir:
        zip_path = os.path.join(tmpdir, "main.zip")
        with open(zip_path, "wb") as f:
            f.write(zip_data)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(tmpdir)
        
        # Determine the name of the top-level repo directory in the zip
        extracted_dirs = [d for d in os.listdir(tmpdir) if os.path.isdir(os.path.join(tmpdir, d))]
        repo_dir_name = None
        for d in extracted_dirs:
            if "xp_pgrs_unofficial_guide" in d:
                repo_dir_name = d
                break
        
        if not repo_dir_name:
            print("[update_skill] Error: Could not find repo folder in extracted zip.")
            return False
            
        src_dir = os.path.join(tmpdir, repo_dir_name)
        
        print("[update_skill] Applying updates...")
        for root, dirs, files in os.walk(src_dir):
            rel_path = os.path.relpath(root, src_dir)
            
            # The root path has rel_path as '.'
            if rel_path == '.':
                target_dir = SKILL_ROOT
            else:
                target_dir = os.path.join(SKILL_ROOT, rel_path)
                
            if not os.path.exists(target_dir):
                os.makedirs(target_dir, exist_ok=True)
                
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(target_dir, file)
                shutil.copy2(src_file, dst_file)
                
        print("[update_skill] Update applied successfully.")
        return True


def main() -> int:
    print("[update_skill] Checking for skill updates...")
    
    local_version = get_local_version()
    remote_version = get_remote_version()
    
    if not remote_version:
        print("[update_skill] Could not check remote version. Aborting update.")
        return 1
        
    print(f"[update_skill] Local version : {local_version}")
    print(f"[update_skill] Remote version: {remote_version}")
    
    if parse_version(remote_version) > parse_version(local_version):
        print("[update_skill] A new version is available! Starting update...")
        success = download_and_extract_update()
        if not success:
            return 1
        print("[update_skill] Skill codebase updated successfully.")
        return 0
    else:
        print("[update_skill] The skill is up-to-date.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
