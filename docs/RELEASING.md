# Publish on GitHub

## Prepare your repository identity

Create an empty public GitHub repository named `ha-mbta-departures`. Do not initialize extra files. Enable Issues, add a description and topics such as `home-assistant`, `hacs`, `mbta` and `transit`.

In the extracted repository root, run:

```bash
python scripts/configure_repository.py YOUR_GITHUB_USERNAME
```

This sets the documentation/issue URLs and code owner in manifest.json. The placeholder is intentional: the release package does not assume a GitHub account name. If you use a different repository name, pass `--repo your-repository-name`.

## Upload

From the extracted project root:

```bash
git init
git add .
git commit -m "Initial MBTA Departures release"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/ha-mbta-departures.git
git push -u origin main
```

Or upload the extracted contents using GitHub's upload UI, including `.github` workflows. The repository root must contain `custom_components`, README.md and LICENSE directly.

## Validate and release

1. Check the Actions tab and resolve failures; remote hassfest has not been run by this package generator.
2. Verify installation, departures, alerts, dashboard and restart behavior in Home Assistant.
3. Update manifest version and CHANGELOG.md for subsequent releases.
4. Create a GitHub release with tag `v0.1.0`, title `MBTA Departures 0.1.0`, and release notes from RELEASE_NOTES.md. A tag alone is not a GitHub release.
5. Consider a pre-release while testing on more Home Assistant versions.
6. Users can download GitHub's automatically generated source ZIP. Alternatively run `python scripts/build_release.py` and attach the resulting ZIP from `dist/`.

The source ZIP is a repository package, not an integration-only HACS zip-release asset. `hacs.json` deliberately does not enable zip_release.

## HACS

This repository supports the Integration custom-repository category. The frontend is a manual extra step. Default HACS listing requires additional current HACS requirements, branding and HACS validation; no default-listing approval is claimed.
