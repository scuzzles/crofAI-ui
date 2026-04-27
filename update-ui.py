import urllib.request
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
UI3_DIR = os.path.join(BASE, "templates", "ui3")
GH_API = "https://api.github.com/repos/scuzzles/crofAI-ui/contents"
GH_RAW = "https://raw.githubusercontent.com/scuzzles/crofAI-ui/main"

PROTECTED = {"signin.html", "signup.html"}

os.makedirs(UI3_DIR, exist_ok=True)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "update-ui"})
    with urllib.request.urlopen(req) as r:
        return r.read()


def files_in_gh_dir(path):
    data = json.loads(fetch(f"{GH_API}/{path}"))
    return [i["name"] for i in data if i["type"] == "file"]


IGNORE = {"update-ui.py", "README.md", ".gitignore"}
GH_FILES = {f for f in files_in_gh_dir(".") if f not in IGNORE}


def update_file(name):
    url = f"{GH_RAW}/{name}"
    content = fetch(url)
    local_path = os.path.join(UI3_DIR, name)
    with open(local_path, "wb") as f:
        f.write(content)
    print(f"  UPDATED {name}")


def update_title_only(name):
    url = f"{GH_RAW}/{name}"
    gh_content = fetch(url).decode()
    gh_title = re.search(r"<title>(.*?)</title>", gh_content)
    local_path = os.path.join(UI3_DIR, name)
    with open(local_path, "r") as f:
        local_content = f.read()
    local_title = re.search(r"<title>(.*?)</title>", local_content)
    if gh_title and local_title and gh_title.group(0) != local_title.group(0):
        local_content = local_content.replace(local_title.group(0), gh_title.group(0))
        with open(local_path, "w") as f:
            f.write(local_content)
        print(f"  TITLE-FIXED {name}")


print(f"Fetching file list from GitHub ({len(GH_FILES)} files)...")

local_extra = set()
for f in os.listdir(UI3_DIR):
    if f.endswith(".html") and f not in GH_FILES and f not in PROTECTED:
        local_extra.add(f)
if local_extra:
    print(f"  Preserving local-only files: {', '.join(sorted(local_extra))}")

for name in sorted(GH_FILES):
    if name in PROTECTED:
        update_title_only(name)
    elif name.endswith((".html", ".css", ".js")):
        update_file(name)

print("\nDone.")
