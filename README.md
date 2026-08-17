# AI Social Content Automation

₹0-first automation project for publishing technical infographic content from `topics/topics.docx`.

## Flow
1. Read all topics from Word.
2. Maintain status in `state.json`.
3. Pick next 4 `PENDING` topics.
4. Generate 1080x1800 PNG infographics with Pillow.
5. Generate deterministic captions/hashtags without a paid AI API.
6. Publish through official-platform adapter boundaries when configured.
7. Update state with status and URLs.
8. Run from GitHub Actions every morning at 06:15 IST.

## Safety
- Default is `DRY_RUN=true`.
- No passwords are stored.
- Tokens belong in GitHub Secrets.
- Platform adapter calls are intentionally stubbed until official API permissions are configured.

## Local run
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python src/main.py
```

Put one topic per paragraph in `topics/topics.docx`.

Status values: `PENDING`, `PROCESSING`, `GENERATED`, `PUBLISHED`, `FAILED`.
