from __future__ import annotations

import os

from src.content.topic_parser import detect_category


def _fallback_content(topic: str, category: str) -> dict:
    return {
        "title": topic,
        "category": category,
        "tagline": "Practical • Visual • Production-Focused • Scalable",
        "overview": (
            f"A visual breakdown of {topic}, including its core flow, "
            "trade-offs and production considerations."
        ),
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
            "label": "How It Works",
            "title": "How It Works",
            "nodes": [
                {"label": "Input", "sub": ""},
                {"label": "Process", "sub": ""},
                {"label": "Output", "sub": ""},
            ],
            "connections": [
                "Input -> Process",
                "Process -> Output",
            ],
        },
        "example_title": "Concept Flow",
        "example_rows": [
            ["Input", "Process"],
            ["Process", "Output"],
        ],
        "failure_title": "What Can Go Wrong?",
        "failure_before": [["System", "Healthy"]],
        "failure_after": [["System", "Degraded"]],
        "scenarios": [],
        "best_practices": [
            "Keep responsibilities explicit.",
            "Monitor important metrics.",
            "Handle failures deliberately.",
            "Protect configuration and credentials.",
        ],
        "use_cases": [
            "Backend Systems",
            "APIs",
            "Microservices",
            "Data Processing",
        ],
        "diagram": "",
    }


def _string(value, default="") -> str:
    if value is None:
        return default
    return str(value).strip()


def _normalize_key_ideas(raw) -> list[dict]:
    result = []

    for item in (raw or [])[:4]:
        if isinstance(item, dict):
            title = _string(item.get("title") or item.get("label"))
            description = _string(
                item.get("description")
                or item.get("desc")
                or item.get("details")
            )
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            title = _string(item[0])
            description = _string(item[1])
        else:
            title = _string(item)
            description = ""

        if title:
            result.append(
                {
                    "title": title,
                    "description": description,
                }
            )

    return result


def _normalize_nodes(raw) -> list[dict]:
    nodes = []

    for item in (raw or [])[:6]:
        if isinstance(item, dict):
            label = _string(
                item.get("label")
                or item.get("title")
                or item.get("name")
            )
            sub = _string(
                item.get("sub")
                or item.get("description")
                or item.get("details")
            )
        else:
            label = _string(item)
            sub = ""

        if label:
            nodes.append(
                {
                    "label": label,
                    "sub": sub,
                }
            )

    return nodes


def _normalize_rows(raw, max_rows=4) -> list[list[str]]:
    rows = []

    for row in (raw or [])[:max_rows]:
        if isinstance(row, (list, tuple)):
            values = [_string(x) for x in row[:2]]
            if values and any(values):
                if len(values) == 1:
                    values.append("")
                rows.append(values)
        elif isinstance(row, dict):
            left = _string(row.get("label") or row.get("left") or row.get("from"))
            right = _string(row.get("value") or row.get("right") or row.get("to"))
            if left:
                rows.append([left, right])
        else:
            value = _string(row)
            if value:
                rows.append([value, ""])

    return rows


def _normalize_architecture(raw) -> dict:
    """
    Accept all known Gemini variants and always produce the renderer contract.

    Supported Gemini forms:
      {type, label, nodes, connections}
      {type, title, nodes, connections}
      {type, name, nodes, connections}
    """
    raw = raw if isinstance(raw, dict) else {}

    architecture_type = _string(
        raw.get("type")
        or raw.get("template")
        or "generic"
    )

    label = _string(
        raw.get("label")
        or raw.get("title")
        or raw.get("name")
        or "How It Works"
    )

    title = _string(
        raw.get("title")
        or raw.get("label")
        or raw.get("name")
        or label
    )

    nodes = _normalize_nodes(
        raw.get("nodes")
        or raw.get("flow")
        or raw.get("steps")
    )

    connections = []
    for value in (
        raw.get("connections")
        or raw.get("edges")
        or raw.get("links")
        or []
    )[:8]:
        if isinstance(value, str):
            text = value.strip()
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            text = f"{_string(value[0])} -> {_string(value[1])}"
        elif isinstance(value, dict):
            source = _string(
                value.get("source")
                or value.get("from")
            )
            target = _string(
                value.get("target")
                or value.get("to")
            )
            text = f"{source} -> {target}" if source and target else ""
        else:
            text = ""

        if text:
            connections.append(text)

    return {
        "type": architecture_type,
        "label": label,
        "title": title,
        "nodes": nodes,
        "connections": connections,
    }


def _normalize_gemini_content(
    data: dict,
    topic: str,
    category: str,
) -> dict:
    if not isinstance(data, dict):
        raise ValueError("Gemini content must be a JSON object.")

    key_ideas = _normalize_key_ideas(
        data.get("key_ideas")
        or data.get("key_concepts")
    )

    architecture = _normalize_architecture(
        data.get("architecture")
        or data.get("diagram")
        or {}
    )

    best_practices = [
        _string(x)
        for x in (data.get("best_practices") or data.get("bestPractices") or [])[:4]
        if _string(x)
    ]

    use_cases = [
        _string(x)
        for x in (data.get("use_cases") or data.get("useCases") or [])[:4]
        if _string(x)
    ]

    scenarios = data.get("scenarios") or []
    normalized_scenarios = []

    for scenario in scenarios[:3]:
        if isinstance(scenario, dict):
            normalized_scenarios.append(
                {
                    "title": _string(scenario.get("title")),
                    "before": _string(scenario.get("before")),
                    "after": _string(scenario.get("after")),
                    "impact": _string(scenario.get("impact")),
                }
            )

    # IMPORTANT:
    # Legacy code expects key_concepts as tuples.
    legacy_key_concepts = [
        (item["title"], item["description"])
        for item in key_ideas
    ]

    # Some existing renderers read architecture["label"] directly.
    # Always provide it even if Gemini returned only architecture["title"].
    return {
        "title": topic,
        "category": category,
        "tagline": _string(
            data.get("tagline")
            or data.get("subtitle")
            or "Practical • Visual • Production-Focused"
        ),
        "overview": _string(
            data.get("overview")
            or data.get("summary")
            or f"A practical breakdown of {topic}."
        ),
        "key_ideas": key_ideas,
        "key_concepts": legacy_key_concepts,
        "architecture": architecture,
        "example_title": _string(
            data.get("example_title")
            or data.get("exampleTitle")
            or "Concept Flow"
        ),
        "example_rows": _normalize_rows(
            data.get("example_rows")
            or data.get("exampleRows")
        ),
        "failure_title": _string(
            data.get("failure_title")
            or data.get("failureTitle")
            or "What Can Go Wrong?"
        ),
        "failure_before": _normalize_rows(
            data.get("failure_before")
            or data.get("failureBefore"),
            max_rows=3,
        ),
        "failure_after": _normalize_rows(
            data.get("failure_after")
            or data.get("failureAfter"),
            max_rows=3,
        ),
        "scenarios": normalized_scenarios,
        "best_practices": best_practices,
        "use_cases": use_cases,
        "diagram": "",
    }


def build_content(item: dict) -> dict:
    topic = _string(item.get("topic"))
    if not topic:
        raise ValueError("Topic cannot be empty.")

    category = _string(
        item.get("category") or detect_category(topic)
    ).casefold()

    enabled = (
        os.getenv("GEMINI_ENABLED", "true").strip().casefold()
        != "false"
    )
    api_key_exists = bool(
        os.getenv("GEMINI_API_KEY", "").strip()
    )

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

            # Explicit content supplied by the Word source still wins.
            if item.get("overview"):
                content["overview"] = _string(item["overview"])

            if item.get("best_practices"):
                content["best_practices"] = item["best_practices"][:4]

            if item.get("use_cases"):
                content["use_cases"] = item["use_cases"][:4]

            return content

        except Exception as exc:
            print(
                f"[GEMINI WARNING] Falling back for '{topic}': {exc}"
            )

    fallback = _fallback_content(topic, category)

    if item.get("overview"):
        fallback["overview"] = _string(item["overview"])

    if item.get("best_practices"):
        fallback["best_practices"] = item["best_practices"][:4]

    if item.get("use_cases"):
        fallback["use_cases"] = item["use_cases"][:4]

    return fallback
