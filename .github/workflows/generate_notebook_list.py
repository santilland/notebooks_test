import os
import json
import nbformat
import yaml
import subprocess
from urllib.parse import urlparse
import pathlib

ROOT_DIR = os.path.abspath(".")
OUTPUT_FILE = "notebooks.json"
NOTEBOOK_DIR = "notebooks"
SUBMODULE_ROOT = "external_notebooks"
JHUB_INSTANCE = "dashboard.test1.hub-int.eox.at"
IGNORE_FOLDERS = ["venv", ".git", ".github", "_build", "_data", "dist"]
DEF_ORG = "santilland"
DEF_REPO = "notebooks_test"


def parse_gitmodules():
    """Parse .gitmodules to map paths to remote info."""
    gitmodules_path = os.path.join(ROOT_DIR, ".gitmodules")
    if not os.path.exists(gitmodules_path):
        return {}

    submodules = {}
    current = {}

    with open(gitmodules_path, "r") as f:
        for line in f:
            line = line.strip()
            if line.startswith("[submodule"):
                if current:
                    submodules[current["path"]] = current["url"]
                current = {}
            elif "=" in line:
                key, value = [x.strip() for x in line.split("=", 1)]
                current[key] = value
        if current:
            submodules[current["path"]] = current["url"]

    # Convert to path → { org, repo }
    result = {}
    for path, url in submodules.items():
        if url.endswith(".git"):
            url = url[:-4]
        if url.startswith("git@"):
            url = url.replace(":", "/").replace("git@", "https://")
        parsed = urlparse(url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2:
            norm_path = os.path.normpath(path)
            result[norm_path] = {
                "org": parts[0],
                "repo": parts[1],
                "url": url
            }

    return result

def get_git_remote_info(repo_path):
    try:
        print(repo_path)
        url = subprocess.check_output(
            ["git", "-C", repo_path, "config", "--get", "remote.origin.url"],
            text=True
        ).strip()
        print(url)
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
    submodules = parse_gitmodules()

    # --- Local notebooks
    local_path = os.path.join(ROOT_DIR, NOTEBOOK_DIR)
    for dirpath, _, filenames in os.walk(local_path):
        if any(ignored in dirpath for ignored in IGNORE_FOLDERS):
            continue
        for file in filenames:
            if file.endswith(".ipynb"):
                # print(f"Processing {file} in {dirpath}")
                abs_path = os.path.join(dirpath, file)
                rel_path = os.path.relpath(abs_path, ROOT_DIR).replace("\\", "/")
                meta = extract_frontmatter(abs_path)
                catalog.append({
                    "title": meta.get("title", os.path.splitext(file)[0]),
                    "description": meta.get("description", ""),
                    "metadata": meta,
                    "link": rel_path.replace(".ipynb", ""),
                    "org": DEF_ORG,
                    "repo": DEF_REPO,
                    "source": "local",
                    "path": rel_path,
                    "gitpuller": f"https://{JHUB_INSTANCE}/hub/user-redirect/git-pull?repo={git_url}&urlpath={rel_path}&branch=main",
                })

    # --- Submodule notebooks
    submodules_root = os.path.join(ROOT_DIR, SUBMODULE_ROOT)
    for group in os.listdir(submodules_root):
        group_path = os.path.join(submodules_root, group)
        if not os.path.isdir(group_path):
            continue

        for repo in os.listdir(group_path):
            sub_path = os.path.join(group_path, repo)
            if not os.path.isdir(sub_path):
                continue

            sub_rel = os.path.relpath(sub_path, ROOT_DIR)
            git_info = submodules.get(os.path.normpath(sub_rel), {"org": None, "repo": None})
            git_url = git_info["url"]

            for dirpath, _, filenames in os.walk(sub_path):
                for file in filenames:
                    if file.endswith(".ipynb"):
                        abs_path = os.path.join(dirpath, file)
                        rel_path = os.path.relpath(abs_path, ROOT_DIR).replace("\\", "/")
                        p = pathlib.Path(rel_path)
                        repo_path = pathlib.Path(*p.parts[3:])
                        meta = extract_frontmatter(abs_path)
                        catalog.append({
                            "title": meta.get("title", os.path.splitext(file)[0]),
                            "description": meta.get("description", ""),
                            "metadata": meta,
                            "link": rel_path.replace(".ipynb", ""),
                            "org": git_info["org"],
                            "repo": git_info["repo"],
                            "source": "submodule",
                            "path": rel_path,
                            "gitpuller": f"https://{JHUB_INSTANCE}/hub/user-redirect/git-pull?repo={git_url}&urlpath={repo_path}&branch=main",
                        })

    return catalog

if __name__ == "__main__":
    notebooks = collect_notebooks()
    with open(OUTPUT_FILE, "w") as f:
        json.dump(notebooks, f, indent=2)
    print(f"✅ Catalog saved to {OUTPUT_FILE}")
