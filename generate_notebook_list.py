import os
import yaml
from jinja2 import Template

# Directory where notebooks are stored
NOTEBOOKS_DIR = "notebooks"

# Scan for notebooks
notebooks = []
for filename in sorted(os.listdir(NOTEBOOKS_DIR)):
    if filename.endswith(".ipynb"):
        notebooks.append({
            "name": filename.replace(".ipynb", "").replace("_", " ").title(),
            "path": f"{NOTEBOOKS_DIR}/{filename}"
        })

# Load Jinja2 template
with open("notebooks_template.md", "r") as f:
    template_content = f.read()
template = Template(template_content)

# Render the template with notebook data
rendered_content = template.render(notebooks=notebooks)

# Save as `notebooks.md`
with open("notebooks.md", "w") as f:
    f.write(rendered_content)

print(f"✅ Processed {len(notebooks)} notebooks and updated `notebooks.md`.")
