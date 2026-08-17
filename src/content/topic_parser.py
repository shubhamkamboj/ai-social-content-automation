from __future__ import annotations

from pathlib import Path
from docx import Document

CATEGORIES = {
    "kafka": ["kafka", "consumer group", "producer", "partition", "offset", "rebalance"],
    "redis": ["redis", "cache", "caching", "ttl", "eviction"],
    "spring": ["spring boot", "spring ", "transactional", "spring security", "spring cloud", "actuator"],
    "java": ["java", "jvm", "hashmap", "garbage collection", "concurrency", "thread", "stream"],
    "aws": ["aws", "s3", "ec2", "cloudfront", "route53", "lambda", "vpc", "iam"],
    "mongodb": ["mongodb", "mongo", "nosql", "aggregation", "document database"],
    "docker": ["docker", "container", "docker compose", "image"],
    "microservices": ["microservice", "circuit breaker", "saga", "cqrs", "service discovery", "distributed system"],
    "sql": ["sql", "mysql", "sql server", "database", "index", "join", "transaction"],
    "security": ["jwt", "oauth", "authentication", "authorization", "security", "token"],
}

def clean(value: str) -> str:
    return " ".join((value or "").strip().split())


def detect_category(topic: str) -> str:
    text = topic.casefold()
    for category, words in CATEGORIES.items():
        if any(word in text for word in words):
            return category
    return "generic"


def split_multi(value: str) -> list[str]:
    return [clean(x) for x in value.split(";") if clean(x)]


def read_topics(path: str) -> list[dict]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"Topics file not found: {file_path}")

    doc = Document(file_path)
    result: list[dict] = []

    # Simple one-topic-per-paragraph mode.
    for paragraph in doc.paragraphs:
        topic = clean(paragraph.text)
        if topic:
            result.append({
                "topic": topic,
                "category": detect_category(topic),
                "overview": "",
                "key_concepts": [],
                "diagram": "",
                "scenarios": [],
                "best_practices": [],
                "use_cases": [],
            })

    # Optional rich table mode.
    for table in doc.tables:
        if not table.rows:
            continue
        headers = [clean(c.text).casefold() for c in table.rows[0].cells]
        if "topic" not in headers:
            continue

        index = {name: i for i, name in enumerate(headers)}
        for row in table.rows[1:]:
            cells = [clean(c.text) for c in row.cells]
            topic = cells[index["topic"]] if index["topic"] < len(cells) else ""
            if not topic:
                continue

            category = (
                cells[index["category"]]
                if "category" in index and index["category"] < len(cells)
                else detect_category(topic)
            )
            result.append({
                "topic": topic,
                "category": category.casefold() or detect_category(topic),
                "overview": cells[index["overview"]] if "overview" in index else "",
                "key_concepts": split_multi(cells[index["key concepts"]]) if "key concepts" in index else [],
                "diagram": cells[index["diagram"]] if "diagram" in index else "",
                "scenarios": split_multi(cells[index["scenarios"]]) if "scenarios" in index else [],
                "best_practices": split_multi(cells[index["best practices"]]) if "best practices" in index else [],
                "use_cases": split_multi(cells[index["use cases"]]) if "use cases" in index else [],
            })

    # Remove duplicate topics preserving first appearance.
    seen = set()
    unique = []
    for item in result:
        key = item["topic"].casefold()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    return unique
