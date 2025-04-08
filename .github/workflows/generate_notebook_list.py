import os
import json
import nbformat
import yaml
import subprocess
from urllib.parse import urlparse

ROOT_DIR = os.path.abspath(".")
OUTPUT_FILE = "notebooks.json"
NOTEBOOK_DIR = "notebooks"
SUBMODULE_DIR = "external_notebooks"
JHUB_INSTANCE = "dashboard.test1.hub-int.eox.at"
IGNORE_FOLDERS = ["venv", ".git", ".github", "_build", "_data", "dist"]
DEF_ORG = "santilland"
DEF_REPO = "notebooks_test"

def get_git_remote_info(repo_path):
    try:
        url = subprocess.check_output(
            ["git", "-C", repo_path, "config", "--get", "remote.origin.url"],
            text=True
        ).strip()
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            return {"org": parts[0], "repo": parts[1], "url": url}
    except Exception as e:
        print(f"[warn] Could not get git remote info from {repo_path}: {e}")
    return {"org": DEF_ORG, "repo": DEF_REPO, "url": url}

def extract_frontmatter(notebook_path):
    try:
        nb = nbformat.read(notebook_path, as_version=4)
        if nb.cells and nb.cells[0].cell_type == 'markdown':
            content = nb.cells[0].source
            if content.strip().startswith('---'):
                block = content.split('---')[1]
                return yaml.safe_load(block)
    except Exception as e:
        print(f"[warn] Failed to extract frontmatter from {notebook_path}: {e}")
    return {}

def collect_notebooks():
    catalog = []
    git_url = get_git_remote_info(ROOT_DIR)["url"]
    # --- Local notebooks
    local_path = os.path.join(ROOT_DIR, NOTEBOOK_DIR)
    for dirpath, _, filenames in os.walk(local_path):
        if any(ignored in dirpath for ignored in IGNORE_FOLDERS):
            continue
        for file in filenames:
            if file.endswith(".ipynb"):
                print(f"Processing {file} in {dirpath}")
                abs_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(abs_path, ROOT_DIR).replace("\\", "/")
                meta = extract_frontmatter(abs_path)
                catalog.append({
                    "title": meta.get("title", os.path.splitext(file)[0]),
                    "description": meta.get("description", ""),
                    "link": rel_path,
                    "org": DEF_ORG,
                    "repo": DEF_REPO,
                    "source": "local",
                    "path": rel_path,
                    "gitpuller": f"https://{JHUB_INSTANCE}/hub/user-redirect/git-pull?repo={git_url}&urlpath={rel_path}&branch=master",
                })

    # --- Submodule notebooks
    submodules_root = os.path.join(ROOT_DIR, SUBMODULE_DIR)
    for submodule_name in os.listdir(submodules_root):
        submodule_path = os.path.join(submodules_root, submodule_name)
        if not os.path.isdir(submodule_path):
            continue

        git_info = get_git_remote_info(submodule_path)
        git_url = git_info["url"]

        for dirpath, _, filenames in os.walk(submodule_path):
            if any(ignored in dirpath for ignored in IGNORE_FOLDERS):
                continue
            print(f"Processing {file} in {dirpath}")
            for file in filenames:
                if file.endswith(".ipynb"):
                    abs_path = os.path.join(dirpath, file)
                    rel_path = os.path.relpath(abs_path, ROOT_DIR).replace("\\", "/")
                    meta = extract_frontmatter(abs_path)
                    catalog.append({
                        "title": meta.get("title", os.path.splitext(file)[0]),
                        "description": meta.get("description", ""),
                        "link": rel_path,
                        "org": git_info["org"],
                        "repo": git_info["repo"],
                        "source": "submodule",
                        "path": rel_path,
                        "gitpuller": f"https://{JHUB_INSTANCE}/hub/user-redirect/git-pull?repo={git_url}&urlpath={rel_path}&branch=master",
                    })

    return catalog

if __name__ == "__main__":
    notebooks = collect_notebooks()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(notebooks, f, indent=2)
    print(f"✅ Catalog saved to {OUTPUT_FILE}")
