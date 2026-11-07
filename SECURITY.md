# Reporting security issues

Do not post credentials or exploitable security details in public issues. Use the repository's private vulnerability reporting feature if the maintainer has enabled it. If unavailable, open a minimal issue asking for a private reporting channel without exposing details.

API keys are entered through Home Assistant configuration. The dashboard JavaScript contains no credentials. Files installed under Home Assistant's `www` directory are publicly served; never put credentials in that directory.
