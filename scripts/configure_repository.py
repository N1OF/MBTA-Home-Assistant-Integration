"""Set public repository identity before publishing."""
import argparse
import json
import re
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("username")
p.add_argument("--repo", default="ha-mbta-departures")
a = p.parse_args()
if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", a.username):
    p.error("Invalid GitHub username")
if not re.fullmatch(r"[A-Za-z0-9_.-]+", a.repo):
    p.error("Invalid repository name")
path = Path(__file__).resolve().parents[1] / "custom_components/mbta_departures/manifest.json"
data = json.loads(path.read_text())
base = f"https://github.com/{a.username}/{a.repo}"
data.update(documentation=base, issue_tracker=base + "/issues", codeowners=["@" + a.username])
path.write_text(json.dumps(data, indent=2) + "\n")
print("Configured repository URLs and code owner:", base)
