from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from src.content.topic_parser import detect_category
from src.infographic.templates import render_topic_card
FONT_CANDIDATES=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf","/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf","C:/Windows/Fonts/arialbd.ttf","C:/Windows/Fonts/arial.ttf"]
def load_font(size,bold=False):
    for c in FONT_CANDIDATES:
        try: return ImageFont.truetype(c,size=size)
        except OSError: pass
    return ImageFont.load_default()

def content_for(topic,cat):
    presets={
    "kafka":("Kafka uses topics and partitions to distribute records. Consumer groups let multiple consumers share work while Kafka tracks offsets and rebalances assignments.",["Partition-based parallelism","Consumer group coordination","Offset tracking","Rebalancing","Scalable event processing"]),
    "redis":("Redis is an in-memory data store commonly used for caching, sessions, counters and fast lookups. TTL and eviction policies help control memory.",["Low-latency reads","Key-value model","TTL and expiration","Eviction strategies","Caching patterns"]),
    "spring":("Spring Boot simplifies production Java services through dependency injection, configuration, starters and operational features.",["Dependency injection","Auto-configuration","Actuator","REST APIs","Production-ready services"]),
    "java":("Java backend systems rely on the JVM, collections, concurrency and memory management to deliver predictable application behavior at scale.",["Collections","JVM execution","Concurrency","Memory management","Performance"]),
    "aws":("AWS provides managed building blocks for application hosting, storage, networking, databases and observability.",["Managed infrastructure","Scalable services","IAM and security","Networking","Cloud operations"]),
    "mongodb":("MongoDB stores JSON-like documents and supports flexible schemas, indexes and aggregation pipelines for application workloads.",["Document model","Indexes","Aggregation","Flexible schema","Horizontal scaling"]),
    "docker":("Docker packages an application and its dependencies into containers so environments become more repeatable across development and deployment.",["Images","Containers","Networks","Volumes","Repeatable deployments"]),
    "microservices":("Microservices split a large application into independently deployable services with explicit boundaries, communication contracts and operational ownership.",["Service boundaries","API communication","Resilience","Observability","Independent deployment"]),
    "sql":("SQL databases organize data into tables and relationships. Query design, indexes and transaction behavior directly affect correctness and performance.",["Tables and relations","Indexes","Joins","Transactions","Query performance"]),
    "security":("Modern application security combines identity, authentication, authorization and secure token handling across clients and services.",["Authentication","Authorization","Tokens","Least privilege","Secure APIs"])}
    return presets.get(cat,(f"{topic} can be understood through its purpose, architecture, key components and common production use cases.",["Core concept","Architecture","Main components","Common use case","Production consideration"]))

def generate_infographic(topic,output_path):
    cat=detect_category(topic); summary,points=content_for(topic,cat)
    img=Image.new("RGB",(1080,1800),"white"); draw=ImageDraw.Draw(img)
    fonts=(load_font(72,True),load_font(24,True),load_font(34,True),load_font(28,False))
    render_topic_card(draw,topic,cat,summary,points,fonts)
    out=Path(output_path); out.parent.mkdir(parents=True,exist_ok=True); img.save(out,"PNG",optimize=True); return str(out)
