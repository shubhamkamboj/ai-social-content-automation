# AI Social Content Automation

Free-first automation for technical social posts.

## What it does

Every morning GitHub Actions can:

1. Read all topics from `topics/topics.docx`.
2. Pick the next 4 topics that are not fully published.
3. Generate premium dark/neon 1080x1800 technical infographics with Python + Pillow.
4. Generate Instagram and LinkedIn captions without a paid AI API.
5. Make generated images available from the public GitHub repository.
6. Publish through official Instagram Graph API and LinkedIn REST APIs when enabled.
7. Record platform status, URLs, attempts and errors in `state.json`.
8. Commit the updated state back to GitHub.

## Design

The default poster intentionally does NOT contain an "AUTO-GENERATED" footer.

It uses:
- dark near-black background
- blue/purple neon accents
- rounded cards
- overview card
- key concepts
- how-it-works diagram
- scenario table
- best practices
- use cases
- 9:15 portrait ratio (1080x1800)

## Zero-cost mode

The project itself has no paid AI dependency:
- Python
- Pillow
- python-docx
- requests
- GitHub Actions
- GitHub repository

Image generation is deterministic/template-based rather than generative AI.

Platform APIs may require eligible accounts, app permissions, and access tokens. Keep those credentials in GitHub Actions Secrets, never in source files.

## Word file

The easiest format is one topic per paragraph:

```text
Java HashMap Internal Working
Spring Boot @Transactional
Kafka Consumer Group
Redis Caching
AWS Route 53
MongoDB Indexing
Docker Networking
Microservices Circuit Breaker
```

A richer optional format is also supported through a Word table with headers:

```text
Topic | Category | Overview | Key Concepts | Diagram | Scenarios | Best Practices | Use Cases
```

Multiple key concepts / scenarios / practices / use cases can be separated with `;`.

## Local test

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

python -m src.main --dry-run
```

This generates up to 4 images without publishing.

## GitHub Actions

The workflow supports:
- manual run
- daily scheduled run at 06:15 IST
- dry-run mode
- real publishing mode

GitHub Actions supports scheduled workflows with cron, and timezone-aware schedules are supported by the workflow syntax. See the official GitHub documentation.

## Required GitHub Variables

For the first dry-run, no platform credentials are required.

Later:

### Variables

```text
DRY_RUN=false
INSTAGRAM_ENABLED=true
LINKEDIN_ENABLED=true
LINKEDIN_VERSION=202606
INSTAGRAM_GRAPH_BASE_URL=https://graph.facebook.com/vXX.X
PUBLIC_BASE_URL=<your raw GitHub generated folder URL>
```

For `INSTAGRAM_GRAPH_BASE_URL`, use the current version/endpoint supported by your Meta app.

### Secrets

```text
INSTAGRAM_ACCESS_TOKEN
INSTAGRAM_ACCOUNT_ID
LINKEDIN_ACCESS_TOKEN
LINKEDIN_AUTHOR_URN
```

Do NOT use Instagram or LinkedIn passwords.

## Instagram flow

The adapter uses the official media-container flow:
1. Create media container with public image URL + caption.
2. Publish the media container.
3. Read permalink when available.

The image URL must be publicly reachable.

## LinkedIn flow

The adapter follows the current Images API + Posts API pattern:
1. Initialize image upload.
2. Upload image bytes to the returned upload URL.
3. Receive an image URN.
4. Create an organic image post with the image URN.

Current LinkedIn documentation requires a version header and Restli protocol header. Permission depends on member vs organization posting.

## State tracking

Each topic has:

```text
PENDING
PROCESSING
GENERATED
PUBLISHED
FAILED
```

and platform-level state:

```text
instagram.status
instagram.url
linkedin.status
linkedin.url
```

A topic is considered fully published only when all enabled platforms are published.

## Important repository-size note

This prototype stores generated images in Git because social platforms need publicly reachable media. For a long-running account, move the public-media layer to a free/static hosting strategy that fits your usage and periodically prune old generated assets.

## `state.json` example

`state.json` is the persistent tracking file used by the automation. It records which topics have been processed and the publishing status for each platform.

Example:

```json

{
  "version": 3,
  "topics": {},
  "last_run": null,
  "updated_at": null
}


```

### Topic status lifecycle

```text
PENDING
   ↓
PROCESSING
   ↓
GENERATED
   ↓
PUBLISHED
```

If something fails:

```text
PROCESSING / GENERATED
        ↓
      FAILED
```

Platform status is tracked separately so Instagram and LinkedIn can be published independently.

The real `state.json` file is generated and updated by the workflow. The example above is documentation only.
