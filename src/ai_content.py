from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from openai import OpenAI

from config import settings

BASE_STYLE = """
Create premium educational technology infographic content for a developer audience.
Visual direction: Apple/Microsoft/Linear/Stripe/Notion-inspired, clean enterprise design,
soft white or near-black premium background depending on the prompt, subtle gradients,
glassmorphism cards, thin borders, rounded corners, strong hierarchy, high readability,
minimal clutter, technically accurate terminology, professional typography, social-media ready.
Preferred canvas: portrait 9:15. Keep all critical text inside generous safe margins.
""".strip()


def build_prompts(topic: str) -> tuple[str, str, str]:
    image_prompt = f"""{BASE_STYLE}\n\nTopic: {topic}\n\nCreate a single polished infographic image. Do not add a social-media caption inside the image unless it is part of the infographic design. Prioritize technical accuracy and readable labels."""
    text_prompt = f"""Generate social media copy for this technical topic: {topic}.\n\nReturn ONLY valid JSON with keys: instagram_caption, linkedin_post, hashtags, alt_text.\nRules: Instagram caption <= 1,200 characters. LinkedIn post <= 1,500 characters. Provide exactly 5 hashtags without numbering. No markdown tables. Keep the content educational, accurate, and useful for Java/backend/cloud developers."""
    alt_prompt = f"Write concise accessible alt text for an educational infographic about: {topic}." 
    return image_prompt, text_prompt, alt_prompt


def generate_copy(topic: str) -> dict[str, Any]:
    api_key = __import__("os").getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for AI content generation")

    client = OpenAI(api_key=api_key)
    _, text_prompt, _ = build_prompts(topic)
    response = client.responses.create(
        model=settings.openai_model,
        input=text_prompt,
    )
    raw = response.output_text.strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Model returned invalid JSON: {raw[:500]}") from exc

    required = {"instagram_caption", "linkedin_post", "hashtags", "alt_text"}
    missing = required - data.keys()
    if missing:
        raise RuntimeError(f"AI response missing keys: {sorted(missing)}")
    return data


def generate_image(topic: str, output_file: str) -> None:
    api_key = __import__("os").getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for AI image generation")

    client = OpenAI(api_key=api_key)
    image_prompt, _, _ = build_prompts(topic)
    result = client.images.generate(
        model=settings.openai_image_model,
        prompt=image_prompt,
        size="1024x1536",
    )
    item = result.data[0]
    import base64
    import requests

    if getattr(item, "b64_json", None):
        raw = base64.b64decode(item.b64_json)
    elif getattr(item, "url", None):
        raw = requests.get(item.url, timeout=60).content
    else:
        raise RuntimeError("Image API returned no image payload")

    Path(output_file).write_bytes(raw)
