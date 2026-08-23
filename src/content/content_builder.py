from __future__ import annotations

import os

from src.content.topic_parser import detect_category


def _fallback_content(topic: str, category: str) -> dict:
    """
    Emergency fallback so one Gemini/API failure does not stop the
    entire daily pipeline. The normal production path should use Gemini.
    """
    return {
        "title": topic,
        "category": category,
        "tagline": "Practical • Visual • Production-Focused • Scalable",
        "overview": f"A visual breakdown of {topic}, including its core flow, trade-offs and production considerations.",
        "key_ideas": [
            {
                "title": "Core concept",
                "description": f"The main idea behind {topic}.",
            },
            {
                "title": "Flow",
                "description": "Follow how data or requests move through the system.",
            },
            {
                "title": "Trade-offs",
                "description": "Understand the design choices and constraints.",
            },
            {
                "title": "Production",
                "description": "Connect the concept to real-world engineering.",
            },
        ],
        "key_concepts": [
            ("Core concept", f"The main idea behind {topic}."),
            ("Flow", "Follow how data or requests move through the system."),
            ("Trade-offs", "Understand the design choices and constraints."),
            ("Production", "Connect the concept to real-world engineering."),
        ],
        "architecture": {
            "type": "generic",
            "title": "How it works",
            "nodes": [
                {"label": "Input", "sub": ""},
                {"label": "Process", "sub": ""},
                {"label": "Output", "sub": ""},
            ],
            "connections": ["Input -> Process", "Process -> Output"],
        },
        "example_title": "Concept Flow",
        "example_rows": [
            ["Input", "Process"],
            ["Process", "Output"],
        ],
        "failure_title": "What can go wrong?",
        "failure_before": [["System", "Healthy"]],
        "failure_after": [["System", "Degraded"]],
        "scenarios": [],
        "best_practices": [
            "Keep responsibilities explicit.",
            "Monitor important metrics.",
            "Handle failures deliberately.",
            "Protect configuration and credentials.",
        ],
        "use_cases": ["Backend Systems", "APIs", "Microservices", "Data Processing"],
        "diagram": "",
    }


def _normalize_gemini_content(data: dict, topic: str, category: str) -> dict:
    """
    Normalize Gemini's JSON into the fields expected by the existing
    infographic/caption code while keeping legacy key_concepts support.
    """
    key_ideas = data.get("key_ideas") or []

    normalized_ideas = []
    for item in key_ideas[:4]:
        if isinstance(item, dict):
            normalized_ideas.append({
                "title": str(item.get("title", "")).strip(),
                "description": str(item.get("description", "")).strip(),
            })
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            normalized_ideas.append({
                "title": str(item[0]).strip(),
                "description": str(item[1]).strip(),
            })

    normalized_ideas = [
        x for x in normalized_ideas
        if x["title"] and x["description"]
    ]

    legacy_concepts = [
        (x["title"], x["description"])
        for x in normalized_ideas
    ]

    architecture = data.get("architecture") or {}

    return {
        "title": topic,
        "category": category,
        "tagline": str(data.get("tagline", "")).strip(),
        "overview": str(data.get("overview", "")).strip(),
        "key_ideas": normalized_ideas,
        "key_concepts": legacy_concepts,
        "architecture": {
            "type": str(architecture.get("type", "generic")).strip(),
            "title": str(architecture.get("title", "How it works")).strip(),
            "nodes": architecture.get("nodes", [])[:6],
            "connections": architecture.get("connections", [])[:8],
        },
        "example_title": str(
            data.get("example_title", "Concept Flow")
        ).strip(),
        "example_rows": data.get("example_rows", [])[:4],
        "failure_title": str(
            data.get("failure_title", "What can go wrong?")
        ).strip(),
        "failure_before": data.get("failure_before", [])[:4],
        "failure_after": data.get("failure_after", [])[:4],
        "scenarios": data.get("scenarios", [])[:3],
        "best_practices": data.get("best_practices", [])[:4],
        "use_cases": data.get("use_cases", [])[:4],
        "diagram": "",
    }


def build_content(item: dict) -> dict:
    topic = str(item.get("topic", "")).strip()
    if not topic:
        raise ValueError("Topic cannot be empty.")

    category = (
        str(item.get("category") or detect_category(topic))
        .strip()
        .casefold()
    )

    # Gemini is enabled by default only when an API key exists.
    # Set GEMINI_ENABLED=false to turn it off explicitly.
    enabled = (
        os.getenv("GEMINI_ENABLED", "true").strip().casefold()
        != "false"
    )
    api_key_exists = bool(os.getenv("GEMINI_API_KEY", "").strip())

    if enabled and api_key_exists:
        try:
            from src.content.gemini_content import generate_topic_content

            generated = generate_topic_content(
                topic=topic,
                category=category,
            )

            content = _normalize_gemini_content(
                generated,
                topic,
                category,
            )

            # If the Word file contains richer manual fields, let those
            # override the model only where explicitly supplied.
            if item.get("overview"):
                content["overview"] = str(item["overview"]).strip()

            if item.get("best_practices"):
                content["best_practices"] = item["best_practices"][:4]

            if item.get("use_cases"):
                content["use_cases"] = item["use_cases"][:4]

            return content

        except Exception as exc:
            # Keep the scheduled workflow alive if Gemini has a transient
            # quota/network/model issue.
            print(f"[GEMINI WARNING] Falling back for '{topic}': {exc}")

    fallback = _fallback_content(topic, category)

    if item.get("overview"):
        fallback["overview"] = str(item["overview"]).strip()

    if item.get("best_practices"):
        fallback["best_practices"] = item["best_practices"][:4]

    if item.get("use_cases"):
        fallback["use_cases"] = item["use_cases"][:4]

    return fallback
