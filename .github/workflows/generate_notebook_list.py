import os
import json

# Directory where notebooks are stored
NOTEBOOKS_DIR = "notebooks"

# Scan for notebooks
notebooks = []
for filename in sorted(os.listdir(NOTEBOOKS_DIR)):
    organization = "eurodatacube"
    repository = "notebooks"
    jupyterhub_instance = "dashboard.test1.hub-int.eox.at"
    # TODO: look if we are in a submodule folder and adapt settings accordingly
    gh_url = f"https://github.com/{organization}/{repository}"
    no_extension = filename.replace(".ipynb", "")
    if filename.endswith(".ipynb"):
        notebooks.append({
            "name": no_extension.replace("_", " ").title(),
            "path": f"{NOTEBOOKS_DIR}/{filename}",
            "href": f"{NOTEBOOKS_DIR}/{no_extension}.html",
            "gitpuller": f"https://{jupyterhub_instance}/hub/user-redirect/git-pull?repo={gh_url}&urlpath={NOTEBOOKS_DIR}/{filename}&branch=master",
        })

# Save as `notebooks.md`
with open("_data/notebooks.json", "w") as f:
    json.dump({"notebooks": notebooks}, f, indent=2)

print(f"✅ Processed {len(notebooks)} notebooks and updated `notebooks.json`.")
