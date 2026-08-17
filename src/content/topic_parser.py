from pathlib import Path
from docx import Document

def normalize_topic(topic: str) -> str:
    return " ".join(topic.strip().split())

def read_topics(path: str) -> list[str]:
    p = Path(path)
    if not p.exists(): raise FileNotFoundError(f"Topics file not found: {p}")
    doc = Document(p); out=[]; seen=set()
    for para in doc.paragraphs:
        t=normalize_topic(para.text)
        if t and t.casefold() not in seen:
            seen.add(t.casefold()); out.append(t)
    return out

def detect_category(topic: str) -> str:
    t=topic.casefold()
    rules={
        "kafka":["kafka","consumer group","producer","partition","offset"],
        "redis":["redis","cache","caching","ttl","eviction"],
        "spring":["spring boot","spring ","transactional","spring security","spring cloud"],
        "java":["java","jvm","hashmap","garbage collection","concurrency","thread"],
        "aws":["aws","s3","ec2","cloudfront","route53","lambda","vpc"],
        "mongodb":["mongodb","mongo","nosql","aggregation"],
        "docker":["docker","container","docker compose"],
        "microservices":["microservice","circuit breaker","saga","cqrs","service discovery"],
        "sql":["sql","mysql","sql server","database","index","join"],
        "security":["jwt","oauth","authentication","authorization","security"],
    }
    for cat, keys in rules.items():
        if any(k in t for k in keys): return cat
    return "generic"
