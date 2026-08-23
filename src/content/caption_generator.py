from __future__ import annotations

import hashlib
from datetime import datetime, timezone


HASHTAGS = {
    "kafka": ["#Kafka", "#Java", "#Microservices", "#Backend", "#SoftwareEngineering"],
    "redis": ["#Redis", "#Java", "#Backend", "#Caching", "#SoftwareEngineering"],
    "spring": ["#SpringBoot", "#Java", "#Microservices", "#Backend", "#SoftwareEngineering"],
    "java": ["#Java", "#Programming", "#Backend", "#SoftwareEngineering", "#Developers"],
    "aws": ["#AWS", "#Cloud", "#DevOps", "#Backend", "#SoftwareEngineering"],
    "mongodb": ["#MongoDB", "#NoSQL", "#Backend", "#Database", "#SoftwareEngineering"],
    "docker": ["#Docker", "#DevOps", "#Microservices", "#Backend", "#SoftwareEngineering"],
    "microservices": ["#Microservices", "#Java", "#Architecture", "#Backend", "#SoftwareEngineering"],
    "sql": ["#SQL", "#Database", "#Backend", "#Programming", "#SoftwareEngineering"],
    "security": ["#Security", "#Java", "#Backend", "#WebDevelopment", "#SoftwareEngineering"],
    "production": ["#ProductionEngineering", "#DevOps", "#Observability", "#Backend", "#SoftwareEngineering"],
    "generic": ["#Tech", "#Programming", "#Backend", "#SoftwareEngineering", "#Developers"],
}


INSTAGRAM_HOOKS = [
    "Most developers know {topic}. Fewer understand what actually happens under the hood.",
    "{topic} looks simple on the surface — the real engineering is in the details.",
    "Let's break down {topic} in a way you can actually remember.",
    "One concept that can make backend interviews much easier: {topic}.",
    "If you work with backend systems, {topic} is worth understanding properly.",
    "Here's the visual breakdown of {topic} — from core idea to production impact.",
]

LINKEDIN_HOOKS = [
    "A quick visual breakdown of {topic} and the engineering ideas behind it.",
    "{topic} is one of those concepts that becomes much clearer when you see the flow.",
    "Sharing a practical breakdown of {topic} for backend and system-design discussions.",
    "Here's how I think about {topic} when designing or debugging production systems.",
    "{topic}: the core idea, the flow, and the trade-offs that matter in practice.",
]

BRIDGES = [
    "The important part is understanding the flow, not memorizing definitions.",
    "The interesting part is how these pieces work together in a real system.",
    "This is where the theory starts connecting to production engineering.",
    "Once the flow is clear, the implementation details become much easier to reason about.",
]

INSTAGRAM_CTAS = [
    "Save this for your next interview-prep session.",
    "Save it, revisit it, and share it with a developer who is learning this topic.",
    "Worth bookmarking if you are preparing for backend or system-design interviews.",
    "Keep this as a quick reference for your next debugging or design discussion.",
]

LINKEDIN_CTAS = [
    "What would you add to this breakdown?",
    "Which part of this topic causes the most confusion in your experience?",
    "What would you explain differently to a junior engineer?",
    "Which related topic should be broken down next?",
]


def _choose(options: list[str], topic: str, salt: str, day: str | None = None) -> str:
    """
    Deterministic but dynamic selection.

    The same topic can produce a different caption on a different day,
    while a single run remains reproducible.
    """
    seed = f"{topic.casefold()}|{salt}|{day or ''}".encode("utf-8")
    digest = hashlib.sha256(seed).hexdigest()
    index = int(digest[:8], 16) % len(options)
    return options[index]


def _clean(value: str) -> str:
    return " ".join((value or "").strip().split())


def _topic_points(content: dict, max_items: int = 4) -> list[str]:
    """
    Support both the new `key_ideas` structure and the legacy
    `key_concepts` structure.
    """
    ideas = content.get("key_concepts") or content.get("key_ideas") or []

    points = []

    for item in ideas[:max_items]:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            title = _clean(str(item[0]))
            description = _clean(str(item[1]))

            if title and description:
                points.append(f"{title}: {description}")
            elif title:
                points.append(title)
        else:
            value = _clean(str(item))
            if value:
                points.append(value)

    return points


def _hashtags(category: str, topic: str) -> str:
    base = list(HASHTAGS.get(category, HASHTAGS["generic"]))

    # Add one topic-derived tag when it is safe and useful.
    words = [
        word.strip(".,:;()[]{}")
        for word in topic.split()
        if word.strip(".,:;()[]{}")
    ]

    if words:
        candidate = "".join(words[:3])
        if len(candidate) <= 24 and candidate.isalnum():
            dynamic_tag = f"#{candidate}"
            if dynamic_tag.casefold() not in {x.casefold() for x in base}:
                base[-1] = dynamic_tag

    return " ".join(base[:5])


def generate_captions(content: dict) -> dict[str, str]:
    """
    Generate topic-specific captions without requiring a paid AI API.

    Caption variation comes from:
      - topic
      - category
      - overview
      - key concepts
      - daily date
      - varied hooks and CTAs
    """
    topic = _clean(str(content.get("title", "Tech Topic")))
    category = _clean(str(content.get("category", "generic"))).casefold()
    overview = _clean(str(content.get("overview", "")))
    points = _topic_points(content)

    today = datetime.now(timezone.utc).date().isoformat()

    hook_ig = _choose(INSTAGRAM_HOOKS, topic, "instagram-hook", today).format(topic=topic)
    hook_li = _choose(LINKEDIN_HOOKS, topic, "linkedin-hook", today).format(topic=topic)

    bridge = _choose(BRIDGES, topic, "bridge", today)

    cta_ig = _choose(INSTAGRAM_CTAS, topic, "instagram-cta", today)
    cta_li = _choose(LINKEDIN_CTAS, topic, "linkedin-cta", today)

    tags = _hashtags(category, topic)

    # Keep Instagram concise enough for a Reel caption while still
    # teaching something useful.
    ig_lines = [hook_ig, ""]

    if overview:
        ig_lines.extend([overview, ""])

    if points:
        ig_lines.append("Key takeaways:")
        ig_lines.extend(f"• {point}" for point in points[:3])
        ig_lines.append("")

    ig_lines.extend([
        bridge,
        "",
        cta_ig,
        "",
        tags,
    ])

    instagram = "\n".join(ig_lines)

    li_lines = [
        hook_li,
        "",
    ]

    if overview:
        li_lines.extend([overview, ""])

    if points:
        li_lines.append("What matters in practice:")
        li_lines.extend(f"• {point}" for point in points[:4])
        li_lines.append("")

    # Use content beyond the headline so LinkedIn is not just a copy
    # of the Instagram caption.
    li_lines.extend([
        bridge,
        "",
        cta_li,
        "",
        tags,
    ])

    linkedin = "\n".join(li_lines)

    return {
        "instagram": instagram,
        "linkedin": linkedin,
    }
