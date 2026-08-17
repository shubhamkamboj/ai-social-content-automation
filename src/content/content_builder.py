from __future__ import annotations

PRESETS = {
    "kafka": {
        "tagline": "Efficient • Scalable • Fault-Tolerant • Event-Driven",
        "overview": "Kafka uses topics and partitions to distribute records. A consumer group allows multiple consumers to work together and share the load while Kafka tracks offsets and rebalances assignments.",
        "key_concepts": [
            "Partition-based parallelism",
            "Consumer group coordination",
            "Offset tracking",
            "Rebalancing",
            "Scalable & fault-tolerant processing",
        ],
        "diagram_title": "HOW IT WORKS",
        "diagram": "producer_topic_consumers",
        "scenarios": [
            ("New consumer joins", "Partitions are redistributed", "Short pause", "Scale out group"),
            ("Consumer leaves", "Partitions are reassigned", "Short pause", "Instance failure"),
            ("Rebalance triggered", "Assignments recalculated", "Temporary interruption", "Config/failure"),
            ("Group scaling", "Load balanced across consumers", "Higher throughput", "Add consumers"),
            ("Fault tolerance", "Consumers recover ownership", "Reliable processing", "Auto recovery"),
        ],
        "best_practices": [
            "Commit offsets after successful processing",
            "Monitor consumer lag and rebalance events",
            "Use enough partitions for required parallelism",
            "Keep handlers idempotent and fast",
        ],
        "use_cases": ["Real-time Analytics", "Log Aggregation", "Stream Processing", "Event Notifications", "Microservices Integration"],
    },
    "redis": {
        "tagline": "Fast • In-Memory • Low-Latency • Flexible",
        "overview": "Redis is an in-memory data platform used for caching, sessions, counters, rate limiting and fast lookups. TTL and eviction policies help control memory.",
        "key_concepts": ["Key-value model", "Low-latency reads", "TTL & expiration", "Eviction policies", "Caching patterns"],
        "diagram_title": "CACHE FLOW",
        "diagram": "request_cache_db",
        "scenarios": [
            ("Cache hit", "Value returned from Redis", "Lowest latency", "Hot data"),
            ("Cache miss", "Read source then set cache", "Higher latency", "Cold data"),
            ("TTL expiry", "Entry becomes invalid", "Refresh required", "Temporary data"),
            ("Eviction", "Old keys removed", "Memory protected", "High pressure"),
        ],
        "best_practices": [
            "Choose TTLs deliberately",
            "Prevent cache stampedes",
            "Use namespaced keys",
            "Monitor memory and hit ratio",
        ],
        "use_cases": ["API Caching", "Sessions", "Rate Limiting", "Counters", "Leaderboards"],
    },
    "spring": {
        "tagline": "Production-Ready • Modular • Observable • Java",
        "overview": "Spring Boot simplifies production Java services with dependency injection, auto-configuration, starters and operational features.",
        "key_concepts": ["Dependency injection", "Auto-configuration", "REST APIs", "Transactions", "Actuator & observability"],
        "diagram_title": "REQUEST FLOW",
        "diagram": "client_controller_service_repo",
        "scenarios": [
            ("HTTP request", "Controller receives request", "Validation", "API call"),
            ("Service call", "Business logic executes", "Transaction rules", "Use case"),
            ("Repository", "Persistence is performed", "DB interaction", "CRUD"),
            ("Actuator", "Operational metrics exposed", "Observability", "Monitoring"),
        ],
        "best_practices": [
            "Keep controllers thin",
            "Define transaction boundaries clearly",
            "Use configuration properties",
            "Expose only required actuator endpoints",
        ],
        "use_cases": ["REST APIs", "Microservices", "Batch Jobs", "Integration Services", "Enterprise Backends"],
    },
    "java": {
        "tagline": "Strongly Typed • Concurrent • JVM-Based • Enterprise",
        "overview": "Java backend systems rely on the JVM, collections, concurrency and memory management to deliver predictable application behavior at scale.",
        "key_concepts": ["Collections", "JVM execution", "Concurrency", "Memory management", "Performance"],
        "diagram_title": "JAVA REQUEST FLOW",
        "diagram": "client_controller_service_repo",
        "scenarios": [
            ("Request", "Application receives input", "Validation", "REST call"),
            ("Service", "Business logic executes", "CPU work", "Use case"),
            ("JVM", "Bytecode is executed", "JIT/GC", "Runtime"),
            ("Database", "Data is persisted", "I/O", "Repository"),
        ],
        "best_practices": [
            "Prefer clear APIs and immutable data where practical",
            "Measure before optimizing",
            "Control thread pools",
            "Monitor memory and GC behavior",
        ],
        "use_cases": ["Backend APIs", "Microservices", "Batch Processing", "Messaging", "Enterprise Applications"],
    },
    "aws": {
        "tagline": "Scalable • Secure • Managed • Global",
        "overview": "AWS provides managed building blocks for application hosting, storage, networking, databases, identity and observability.",
        "key_concepts": ["Managed services", "Elastic scaling", "IAM & security", "Networking", "Cost & observability"],
        "diagram_title": "CLOUD FLOW",
        "diagram": "user_cloud_service_db",
        "scenarios": [
            ("Traffic spike", "Compute scales out", "More capacity", "Auto scaling"),
            ("Object upload", "Storage receives object", "Durable persistence", "S3"),
            ("API request", "Request crosses network", "Policy + routing", "VPC"),
            ("Failure", "Traffic moves to healthy path", "High availability", "Multi-AZ"),
        ],
        "best_practices": [
            "Apply least privilege IAM",
            "Use multiple availability zones where needed",
            "Tag resources for cost visibility",
            "Monitor health and spend",
        ],
        "use_cases": ["Web Applications", "Data Platforms", "Serverless", "Microservices", "Global Delivery"],
    },
    "mongodb": {
        "tagline": "Document-Oriented • Flexible • Indexed • Scalable",
        "overview": "MongoDB stores document-oriented data and supports flexible schemas, indexes and aggregation pipelines for application workloads.",
        "key_concepts": ["Document model", "Indexes", "Aggregation", "Flexible schema", "Horizontal scaling"],
        "diagram_title": "DOCUMENT FLOW",
        "diagram": "api_document_index",
        "scenarios": [
            ("Insert", "Document written", "Fast write", "New entity"),
            ("Find", "Index locates matching documents", "Low read latency", "Lookup"),
            ("Aggregate", "Pipeline transforms data", "CPU work", "Reporting"),
            ("Scale", "Data distributed", "More capacity", "Sharding"),
        ],
        "best_practices": [
            "Design indexes from query patterns",
            "Avoid unbounded document growth",
            "Measure aggregation performance",
            "Use schema rules where useful",
        ],
        "use_cases": ["Product Catalogs", "Content", "Event Data", "Profiles", "Real-Time Applications"],
    },
    "docker": {
        "tagline": "Portable • Repeatable • Isolated • DevOps",
        "overview": "Docker packages applications and dependencies into containers, making environments more repeatable across development, testing and deployment.",
        "key_concepts": ["Images", "Containers", "Networks", "Volumes", "Repeatable deployments"],
        "diagram_title": "CONTAINER FLOW",
        "diagram": "code_image_container",
        "scenarios": [
            ("Build", "Dockerfile creates image", "Repeatability", "CI pipeline"),
            ("Run", "Image becomes container", "Isolation", "App runtime"),
            ("Network", "Container communicates", "Connectivity", "Service call"),
            ("Volume", "Persistent data mounted", "State retention", "Database"),
        ],
        "best_practices": [
            "Use small, deterministic images",
            "Pin important versions",
            "Do not bake secrets into images",
            "Keep containers focused",
        ],
        "use_cases": ["Local Development", "CI/CD", "Microservices", "Testing", "Cloud Deployment"],
    },
    "microservices": {
        "tagline": "Independent • Resilient • Observable • Scalable",
        "overview": "Microservices split a large application into independently deployable services with explicit boundaries, communication contracts and operational ownership.",
        "key_concepts": ["Service boundaries", "API communication", "Resilience", "Observability", "Independent deployment"],
        "diagram_title": "SERVICE FLOW",
        "diagram": "gateway_services",
        "scenarios": [
            ("Request", "Gateway routes traffic", "Routing", "API call"),
            ("Service call", "Service processes request", "Latency", "Business flow"),
            ("Failure", "Circuit breaker isolates fault", "Graceful degradation", "Dependency down"),
            ("Deploy", "One service changes", "Reduced blast radius", "Independent release"),
        ],
        "best_practices": [
            "Design boundaries around business capabilities",
            "Use timeouts and resilience patterns",
            "Centralize observability",
            "Keep contracts explicit",
        ],
        "use_cases": ["E-Commerce", "Payments", "Enterprise Platforms", "Event-Driven Systems", "Large Backends"],
    },
    "sql": {
        "tagline": "Relational • Consistent • Queryable • Transactional",
        "overview": "SQL databases organize data into tables and relationships. Query design, indexes and transaction behavior directly affect correctness and performance.",
        "key_concepts": ["Tables & relations", "Indexes", "Joins", "Transactions", "Query performance"],
        "diagram_title": "QUERY FLOW",
        "diagram": "api_sql_query_db",
        "scenarios": [
            ("Query", "SQL statement parsed", "Planning", "SELECT"),
            ("Index", "Matching rows located", "Fast lookup", "B-Tree"),
            ("Transaction", "Changes committed atomically", "Consistency", "UPDATE"),
            ("Join", "Tables combined", "CPU/I/O", "Relational query"),
        ],
        "best_practices": [
            "Index real query patterns",
            "Keep transactions focused",
            "Inspect execution plans",
            "Select only required columns",
        ],
        "use_cases": ["Order Systems", "Payments", "Reporting", "ERP", "Transactional Backends"],
    },
    "security": {
        "tagline": "Identity • Least Privilege • Secure by Design",
        "overview": "Modern application security combines identity, authentication, authorization and secure token handling across clients and services.",
        "key_concepts": ["Authentication", "Authorization", "Tokens", "Least privilege", "Secure APIs"],
        "diagram_title": "AUTH FLOW",
        "diagram": "client_auth_api",
        "scenarios": [
            ("Login", "Identity is verified", "Authentication", "Credentials"),
            ("Token", "Access token issued", "Session", "JWT/OAuth"),
            ("API call", "Token is validated", "Authorization", "Protected API"),
            ("Failure", "Request is rejected", "Security", "401/403"),
        ],
        "best_practices": [
            "Never store plaintext passwords",
            "Use short-lived access tokens where appropriate",
            "Apply least privilege",
            "Validate token audience and issuer",
        ],
        "use_cases": ["Web Apps", "Mobile Apps", "APIs", "Microservices", "Enterprise Identity"],
    },
}

GENERIC = {
    "tagline": "Practical • Visual • Production-Focused • Scalable",
    "overview": "A practical visual breakdown covering the purpose, architecture, important concepts and production considerations for this technology.",
    "key_concepts": ["Core concept", "Architecture", "Main components", "Common use case", "Production consideration"],
    "diagram_title": "HOW IT WORKS",
    "diagram": "generic_flow",
    "scenarios": [
        ("Input", "System receives request", "Validation", "Client"),
        ("Process", "Core component handles flow", "Execution", "Service"),
        ("Storage", "Data is persisted", "Durability", "Database"),
        ("Scale", "Additional capacity is added", "Throughput", "Production"),
    ],
    "best_practices": ["Define clear boundaries", "Monitor important metrics", "Handle failures explicitly", "Keep configuration secure"],
    "use_cases": ["Backend Systems", "APIs", "Microservices", "Data Processing", "Enterprise Applications"],
}


def build_content(item: dict) -> dict:
    category = item.get("category") or "generic"
    base = dict(PRESETS.get(category, GENERIC))

    for key in ["overview", "key_concepts", "scenarios", "best_practices", "use_cases", "diagram"]:
        value = item.get(key)
        if value:
            base[key] = value

    base["title"] = item["topic"]
    base["category"] = category
    return base
