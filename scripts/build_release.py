"""Build a clean source release ZIP."""
import json
from pathlib import Path
import zipfile
root = Path(__file__).resolve().parents[1]
version = json.loads((root / "custom_components/mbta_departures/manifest.json").read_text())["version"]
out = root / "dist" / f"ha-mbta-departures-{version}.zip"
out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if path.is_file() and not set(relative.parts).intersection({".git", "dist", "__pycache__", ".venv", ".pytest_cache"}) and path.suffix not in {".pyc", ".zip"}:
            archive.write(path, Path("ha-mbta-departures") / relative)
print(out)
