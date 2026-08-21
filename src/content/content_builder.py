from __future__ import annotations

from src.content.topic_parser import detect_category


# Rich, visual-first content presets.
# IMPORTANT:
# We intentionally return BOTH `key_concepts` and `key_ideas`
# for backward compatibility with older renderer code paths.
PRESETS = {
    "kafka": {
        "tagline": "PARALLEL • SCALABLE • EVENT-DRIVEN",
        "overview_prefix": "Kafka consumer groups let multiple consumers work together to process topic partitions in parallel.",
        "architecture": {
            "type": "kafka_consumer_group",
            "label": "HOW IT WORKS",
        },
        "key_ideas": [
            ("PARTITIONS", "Each partition is consumed by one consumer in a group."),
            ("GROUP", "Consumers with the same group.id share the workload."),
            ("OFFSETS", "Kafka tracks the position of each consumer."),
            ("REBALANCE", "Assignments change when members join or leave."),
        ],
        "example_title": "PARTITION ASSIGNMENT",
        "example_rows": [
            ("P0", "Consumer 1"),
            ("P1", "Consumer 2"),
            ("P2", "Consumer 3"),
        ],
        "failure_title": "WHAT HAPPENS IF A CONSUMER FAILS?",
        "failure_before": [
            ("P0", "C1"),
            ("P1", "C2"),
            ("P2", "C3"),
        ],
        "failure_after": [
            ("P0", "C1"),
            ("P1", "C3"),
            ("P2", "C3"),
        ],
        "best_practices": [
            "Keep consumers <= partitions for useful parallelism.",
            "Monitor consumer lag and rebalance events.",
            "Make processing idempotent where possible.",
            "Commit offsets after successful processing.",
        ],
        "use_cases": [
            "Real-time Analytics",
            "Log Aggregation",
            "Stream Processing",
            "Event Notifications",
        ],
    },
    "java": {
        "tagline": "JVM • PERFORMANCE • CONCURRENCY • RUNTIME",
        "overview_prefix": "Java internals explain how source code becomes bytecode, executes inside the JVM and interacts with memory and threads.",
        "architecture": {
            "type": "java_runtime",
            "label": "RUNTIME FLOW",
        },
        "key_ideas": [
            ("BYTECODE", "Java source is compiled into JVM bytecode."),
            ("JIT", "Hot code is optimized at runtime."),
            ("HEAP", "Objects live in managed JVM memory."),
            ("THREADS", "Execution is coordinated by JVM threads."),
        ],
        "example_title": "JAVA EXECUTION FLOW",
        "example_rows": [
            ("SOURCE", "javac"),
            ("BYTECODE", "JVM"),
            ("JIT", "Optimized Code"),
        ],
        "failure_title": "WHEN PERFORMANCE DROPS",
        "failure_before": [
            ("CPU", "Normal"),
            ("GC", "Normal"),
            ("Threads", "Normal"),
        ],
        "failure_after": [
            ("CPU", "High"),
            ("GC", "High"),
            ("Threads", "Blocked"),
        ],
        "best_practices": [
            "Profile before optimizing.",
            "Control thread pools and queue sizes.",
            "Watch GC and allocation pressure.",
            "Prefer clear, measurable performance changes.",
        ],
        "use_cases": [
            "Backend APIs",
            "Microservices",
            "Batch Processing",
            "Messaging",
        ],
    },
    "spring": {
        "tagline": "BOOTSTRAP • BEANS • REQUESTS • SECURITY",
        "overview_prefix": "Spring turns Java application configuration into managed beans, request pipelines and production-ready services.",
        "architecture": {
            "type": "spring_request",
            "label": "REQUEST FLOW",
        },
        "key_ideas": [
            ("CONTEXT", "ApplicationContext manages application components."),
            ("BEANS", "Beans are created and wired by the container."),
            ("REQUEST", "Spring MVC routes HTTP requests to controllers."),
            ("SECURITY", "Filters and authentication protect endpoints."),
        ],
        "example_title": "SPRING REQUEST PATH",
        "example_rows": [
            ("CLIENT", "REQUEST"),
            ("FILTER", "SECURITY"),
            ("CONTROLLER", "SERVICE"),
            ("REPO", "DATABASE"),
        ],
        "failure_title": "COMMON PRODUCTION HOTSPOTS",
        "failure_before": [
            ("DB", "Healthy"),
            ("POOL", "Healthy"),
            ("CPU", "Normal"),
        ],
        "failure_after": [
            ("DB", "Slow"),
            ("POOL", "Exhausted"),
            ("CPU", "High"),
        ],
        "best_practices": [
            "Keep controllers thin and services focused.",
            "Define transaction boundaries deliberately.",
            "Externalize configuration.",
            "Expose only required actuator endpoints.",
        ],
        "use_cases": [
            "REST APIs",
            "Microservices",
            "Enterprise Services",
            "Batch Jobs",
        ],
    },
    "aws": {
        "tagline": "SCALABLE • MANAGED • SECURE • GLOBAL",
        "overview_prefix": "AWS architecture combines managed services, networking, compute, storage and observability into scalable application paths.",
        "architecture": {
            "type": "aws_flow",
            "label": "CLOUD FLOW",
        },
        "key_ideas": [
            ("EDGE", "Requests can enter through managed routing services."),
            ("COMPUTE", "Lambda, ECS or EKS can run workloads."),
            ("DATA", "RDS, DynamoDB or S3 handle persistence."),
            ("IAM", "Policies control access to resources."),
        ],
        "example_title": "REQUEST PATH",
        "example_rows": [
            ("CLIENT", "ROUTE"),
            ("API", "COMPUTE"),
            ("DATA", "STORAGE"),
        ],
        "failure_title": "DESIGNING FOR FAILURE",
        "failure_before": [
            ("AZ-1", "Healthy"),
            ("AZ-2", "Healthy"),
            ("DB", "Healthy"),
        ],
        "failure_after": [
            ("AZ-1", "Down"),
            ("AZ-2", "Serving"),
            ("DB", "Failover"),
        ],
        "best_practices": [
            "Use least-privilege IAM.",
            "Design for multiple availability zones where needed.",
            "Monitor cost and service health.",
            "Keep resource configuration reproducible.",
        ],
        "use_cases": [
            "Web Applications",
            "Serverless",
            "Microservices",
            "Data Platforms",
        ],
    },
    "redis": {
        "tagline": "FAST • IN-MEMORY • LOW-LATENCY • FLEXIBLE",
        "overview_prefix": "Redis keeps hot data in memory so applications can serve frequently requested information with very low latency.",
        "architecture": {
            "type": "redis_cache",
            "label": "CACHE FLOW",
        },
        "key_ideas": [
            ("CACHE HIT", "Return hot data directly from Redis."),
            ("MISS", "Read the source and repopulate the cache."),
            ("TTL", "Expire temporary entries automatically."),
            ("EVICTION", "Remove old entries when memory is constrained."),
        ],
        "example_title": "CACHE-ASIDE",
        "example_rows": [
            ("REQUEST", "LOOKUP"),
            ("REDIS", "HIT / MISS"),
            ("DB", "FALLBACK"),
        ],
        "failure_title": "WHEN CACHE IS UNAVAILABLE",
        "failure_before": [
            ("API", "Fast"),
            ("REDIS", "Healthy"),
            ("DB", "Normal"),
        ],
        "failure_after": [
            ("API", "Slower"),
            ("REDIS", "Down"),
            ("DB", "Hot"),
        ],
        "best_practices": [
            "Choose TTLs deliberately.",
            "Prevent cache stampedes.",
            "Use consistent key naming.",
            "Monitor memory and hit ratio.",
        ],
        "use_cases": [
            "API Caching",
            "Sessions",
            "Rate Limiting",
            "Counters",
        ],
    },
    "sql": {
        "tagline": "RELATIONAL • CONSISTENT • QUERYABLE • TRANSACTIONAL",
        "overview_prefix": "SQL databases combine tables, indexes and transactions to provide predictable relational data access.",
        "architecture": {
            "type": "sql_query",
            "label": "QUERY FLOW",
        },
        "key_ideas": [
            ("INDEX", "Indexes reduce the work needed to locate rows."),
            ("JOIN", "Queries combine data across related tables."),
            ("TXN", "Transactions protect consistency."),
            ("PLAN", "The optimizer selects an execution strategy."),
        ],
        "example_title": "DATABASE ACCESS",
        "example_rows": [
            ("QUERY", "PARSE"),
            ("INDEX", "LOOKUP"),
            ("TABLE", "ROWS"),
        ],
        "failure_title": "SLOW QUERY SIGNALS",
        "failure_before": [
            ("CPU", "Normal"),
            ("IO", "Normal"),
            ("LOCK", "Low"),
        ],
        "failure_after": [
            ("CPU", "High"),
            ("IO", "High"),
            ("LOCK", "High"),
        ],
        "best_practices": [
            "Index from real query patterns.",
            "Inspect execution plans.",
            "Keep transactions focused.",
            "Select only required columns.",
        ],
        "use_cases": [
            "Payments",
            "Order Systems",
            "ERP",
            "Reporting",
        ],
    },
    "docker": {
        "tagline": "PORTABLE • REPEATABLE • ISOLATED • DEVOPS",
        "overview_prefix": "Docker packages an application with its dependencies so development and deployment environments stay consistent.",
        "architecture": {
            "type": "docker_container",
            "label": "CONTAINER FLOW",
        },
        "key_ideas": [
            ("IMAGE", "A reproducible package of application layers."),
            ("CONTAINER", "A running isolated instance of an image."),
            ("NETWORK", "Containers communicate through virtual networks."),
            ("VOLUME", "Persistent data lives outside the container layer."),
        ],
        "example_title": "BUILD → RUN",
        "example_rows": [
            ("CODE", "DOCKERFILE"),
            ("IMAGE", "CONTAINER"),
            ("APP", "PORT"),
        ],
        "failure_title": "COMMON CONTAINER ISSUES",
        "failure_before": [
            ("IMAGE", "OK"),
            ("PORT", "OK"),
            ("VOLUME", "OK"),
        ],
        "failure_after": [
            ("IMAGE", "OLD"),
            ("PORT", "MISMATCH"),
            ("VOLUME", "MISSING"),
        ],
        "best_practices": [
            "Keep images small and deterministic.",
            "Do not bake secrets into images.",
            "Pin important versions.",
            "Keep container responsibilities focused.",
        ],
        "use_cases": [
            "Local Development",
            "CI/CD",
            "Testing",
            "Microservices",
        ],
    },
    "production": {
        "tagline": "DIAGNOSE • MEASURE • RECOVER • PREVENT",
        "overview_prefix": "Production engineering turns runtime signals into a repeatable process for finding and fixing performance and reliability problems.",
        "architecture": {
            "type": "observability",
            "label": "INVESTIGATION FLOW",
        },
        "key_ideas": [
            ("SIGNAL", "Start with metrics, logs and traces."),
            ("SCOPE", "Reduce the issue to one component or path."),
            ("CAUSE", "Validate the likely bottleneck with evidence."),
            ("FIX", "Apply and measure the change."),
        ],
        "example_title": "INCIDENT LOOP",
        "example_rows": [
            ("ALERT", "DETECT"),
            ("TRACE", "ISOLATE"),
            ("FIX", "VERIFY"),
        ],
        "failure_title": "FROM SYMPTOM TO ROOT CAUSE",
        "failure_before": [
            ("CPU", "High"),
            ("LATENCY", "High"),
            ("ERRORS", "Low"),
        ],
        "failure_after": [
            ("CPU", "Normal"),
            ("LATENCY", "Normal"),
            ("ERRORS", "Normal"),
        ],
        "best_practices": [
            "Keep dashboards focused on user impact.",
            "Use traces to connect service dependencies.",
            "Capture repeatable incident evidence.",
            "Measure recovery after every change.",
        ],
        "use_cases": [
            "Performance Debugging",
            "Incident Response",
            "Observability",
            "Capacity Planning",
        ],
    },
}


GENERIC = {
    "tagline": "PRACTICAL • VISUAL • PRODUCTION-FOCUSED • SCALABLE",
    "overview_prefix": (
        "A visual explanation of the concept, its architecture, "
        "common behavior and production considerations."
    ),
    "architecture": {
        "type": "generic",
        "label": "HOW IT WORKS",
    },
    "key_ideas": [
        ("CORE", "Understand the main concept."),
        ("FLOW", "Follow the request or data path."),
        ("TRADE-OFF", "Know the important design choice."),
        ("OPS", "Connect the concept to production."),
    ],
    "example_title": "CONCEPT FLOW",
    "example_rows": [
        ("INPUT", "PROCESS"),
        ("PROCESS", "OUTPUT"),
    ],
    "failure_title": "WHAT CAN GO WRONG?",
    "failure_before": [
        ("INPUT", "OK"),
        ("PROCESS", "OK"),
        ("OUTPUT", "OK"),
    ],
    "failure_after": [
        ("INPUT", "OK"),
        ("PROCESS", "DEGRADED"),
        ("OUTPUT", "SLOW"),
    ],
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
}


def _copy_preset(preset: dict) -> dict:
    """Shallow copy mutable preset containers so callers can safely modify them."""
    copied = dict(preset)
    for key in (
        "key_ideas",
        "key_concepts",
        "best_practices",
        "use_cases",
        "example_rows",
        "failure_before",
        "failure_after",
    ):
        if isinstance(preset.get(key), list):
            copied[key] = list(preset[key])
    if isinstance(preset.get("architecture"), dict):
        copied["architecture"] = dict(preset["architecture"])
    return copied


def build_content(item: dict) -> dict:
    """
    Build a backwards-compatible content model.

    Important compatibility guarantees:
      - key_ideas is available to the new infographic renderer.
      - key_concepts is also available to older code paths.
      - scenarios is always present.
      - best_practices and use_cases are always present.
    """
    topic = str(item.get("topic", "")).strip()
    if not topic:
        raise ValueError("Topic cannot be empty.")

    category = item.get("category") or detect_category(topic)
    preset = _copy_preset(PRESETS.get(category, GENERIC))

    # Use rich fields from the Word parser when available.
    overview = str(item.get("overview") or preset["overview_prefix"]).strip()

    raw_key_concepts = item.get("key_concepts") or item.get("key_ideas")
    if raw_key_concepts:
        if all(isinstance(value, (list, tuple)) and len(value) >= 2 for value in raw_key_concepts):
            key_ideas = [(str(pair[0]), str(pair[1])) for pair in raw_key_concepts[:4]]
        else:
            key_ideas = [
                (str(value).upper()[:24], str(value))
                for value in raw_key_concepts[:4]
            ]
    else:
        key_ideas = list(preset["key_ideas"])[:4]

    # Normalize both names so no renderer can fail on a missing key.
    key_concepts = list(key_ideas)

    best_practices = list(
        item.get("best_practices") or preset.get("best_practices") or []
    )[:4]

    use_cases = list(
        item.get("use_cases") or preset.get("use_cases") or []
    )[:4]

    # Existing code may expect scenarios even when the new design uses
    # failure_before/failure_after.
    scenarios = list(item.get("scenarios") or [])

    return {
        "title": topic,
        "category": category,
        "tagline": preset.get("tagline", ""),
        "overview": overview,
        "architecture": dict(preset.get("architecture", {})),
        "key_ideas": key_ideas,
        "key_concepts": key_concepts,  # backward compatibility
        "example_title": preset.get("example_title", "CONCEPT FLOW"),
        "example_rows": list(preset.get("example_rows") or []),
        "failure_title": preset.get("failure_title", "WHAT CAN GO WRONG?"),
        "failure_before": list(preset.get("failure_before") or []),
        "failure_after": list(preset.get("failure_after") or []),
        "scenarios": scenarios,
        "best_practices": best_practices,
        "use_cases": use_cases,
        "diagram": item.get("diagram", ""),
    }
