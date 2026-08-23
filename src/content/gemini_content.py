from __future__ import annotations

import json
import os
from typing import List

from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class KeyIdea(BaseModel):
    title: str = Field(description="Short concept label, max 28 characters.")
    description: str = Field(description="One concise explanation.")


class FlowNode(BaseModel):
    label: str = Field(description="Short node label.")
    sub: str = Field(default="", description="Optional short supporting label.")


class Architecture(BaseModel):
    type: str = Field(
        description=(
            "Visual type identifier. Use one of: "
            "linear_flow, branching_flow, pipeline, "
            "request_response, cache_flow, queue_flow, "
            "layered_architecture, lifecycle, comparison, "
            "kafka_consumer_group, generic."
        )
    )
    title: str
    nodes: List[FlowNode] = Field(default_factory=list)
    connections: List[str] = Field(
        default_factory=list,
        description="Connections written as source -> target using exact node labels."
    )


class Scenario(BaseModel):
    title: str
    before: str = ""
    after: str = ""
    impact: str = ""


class GeminiTopicContent(BaseModel):
    title: str
    category: str
    tagline: str
    overview: str
    key_ideas: List[KeyIdea]
    architecture: Architecture
    example_title: str
    example_rows: List[List[str]]
    failure_title: str
    failure_before: List[List[str]]
    failure_after: List[List[str]]
    scenarios: List[Scenario]
    best_practices: List[str]
    use_cases: List[str]


SYSTEM_PROMPT = """
You are the content architect for a premium software-engineering infographic.

Generate UNIQUE, technically accurate content for the supplied topic.

Rules:
1. The topic is the single subject. Never return generic or category-wide content.
2. Every section must be specifically about the exact topic.
3. The architecture is the HERO visual. It must explain the actual mechanism/lifecycle of the topic.
4. Never use generic nodes such as Input, Process, Output, Impact unless the exact topic truly requires them.
5. Prefer 4 key ideas, 4-6 architecture nodes, 3-4 best practices and 3-4 use cases.
6. Keep each string concise enough to fit an infographic.
7. Use correct industry terminology and concrete topic-specific labels.
8. Do not invent product behavior.
9. Do not write ALL CAPS titles. Use normal title style.
10. For JVM GC topics, show actual heap/GC concepts such as regions, young/mixed collections, marking, remembered sets, evacuation or pause phases as applicable.
11. For AWS topics, show actual service-specific flow, not a generic client/API/compute/data pipeline.
12. For Kafka topics, show brokers/topics/partitions/consumers/offsets/rebalancing as applicable.
13. Return only data matching the schema.

Examples:
- VPC -> VPC, subnets, route tables, IGW/NAT, security boundaries.
- ElastiCache -> cache hit/miss, Redis/Memcached, application, database, TTL.
- API Gateway -> client, gateway, auth/throttle/routing, backend integration.
- Lambda -> event, invocation, runtime, execution environment, logs/scaling.
- Kafka Consumer Group -> topic, partitions, consumers, assignments, rebalance.
- G1 GC -> heap regions, young/mixed collections, concurrent phases, pause.
"""


def _client() -> genai.Client:
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not configured."
        )

    return genai.Client(api_key=api_key)


def generate_topic_content(
    topic: str,
    category: str = "",
    model: str | None = None,
) -> dict:
    topic = topic.strip()
    category = category.strip()

    if not topic:
        raise ValueError("Topic is required.")

    selected_model = (
        model
        or os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
    ).strip()

    prompt = f"""
Topic: {topic}
Known category: {category or "unknown"}

Generate the complete premium infographic content for this exact topic.

The final visual is a technical educational infographic, so prioritize:
- one strong architecture/flow visual
- concise explanations
- interview-relevant takeaways
- production relevance
"""

    client = _client()

    response = client.models.generate_content(
        model=selected_model,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=SYSTEM_PROMPT),
                    types.Part.from_text(text=prompt),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=GeminiTopicContent,
            temperature=0.8,
        ),
    )

    raw = (response.text or "").strip()
    if not raw:
        raise RuntimeError("Gemini returned an empty response.")

    try:
        payload = json.loads(raw)
        content = GeminiTopicContent.model_validate(payload)
    except Exception as exc:
        raise RuntimeError(
            f"Gemini returned invalid structured content: {exc}"
        ) from exc

    result = content.model_dump()

    # Keep the parser's category when available.
    if category:
        result["category"] = category

    # Keep every list bounded for infographic layout safety.
    result["key_ideas"] = result["key_ideas"][:4]
    result["best_practices"] = result["best_practices"][:4]
    result["use_cases"] = result["use_cases"][:4]
    result["scenarios"] = result["scenarios"][:3]
    result["architecture"]["nodes"] = result["architecture"]["nodes"][:6]
    result["architecture"]["connections"] = result["architecture"]["connections"][:8]

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        raise SystemExit("Usage: python -m src.content.gemini_content \"Topic\"")

    result = generate_topic_content(sys.argv[1])
    print(json.dumps(result, indent=2, ensure_ascii=False))
