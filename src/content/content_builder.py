from __future__ import annotations

import os
from src.content.topic_parser import detect_category


def _fallback_content(topic: str, category: str) -> dict:
    return {
        "title": topic,
        "category": category,
        "tagline": f"A practical breakdown of {topic}.",
        "overview": f"Understand the core idea, flow, trade-offs and production impact of {topic}.",
        "key_ideas": [
            {"title":"Core idea","description":f"The central concept behind {topic}."},
            {"title":"How it works","description":"The main execution or data flow."},
            {"title":"Trade-offs","description":"The important design choices and constraints."},
            {"title":"Production","description":"What matters when using it in real systems."},
        ],
        "key_concepts": [
            ("Core idea",f"The central concept behind {topic}."),
            ("How it works","The main execution or data flow."),
            ("Trade-offs","The important design choices and constraints."),
            ("Production","What matters when using it in real systems."),
        ],
        "architecture":{
            "type":"linear_flow",
            "label":f"{topic} Flow",
            "title":f"{topic} Flow",
            "nodes":[
                {"label":"Input","sub":""},
                {"label":"Process","sub":""},
                {"label":"Output","sub":""},
            ],
            "connections":["Input -> Process","Process -> Output"],
        },
        "example_title":"Example",
        "example_rows":[["Input","Process"],["Process","Output"]],
        "failure_title":"Failure / Impact",
        "failure_before":[["Normal","Healthy"]],
        "failure_after":[["Issue","Degraded"]],
        "scenarios":[],
        "best_practices":["Keep responsibilities clear.","Monitor important signals.","Handle failures deliberately.","Document key trade-offs."],
        "use_cases":["Backend Systems","APIs","Microservices","Data Processing"],
        "diagram":"",
    }


def _s(v, default=""):
    return str(v).strip() if v is not None else default


def _ideas(raw):
    out=[]
    for item in (raw or [])[:4]:
        if isinstance(item,dict):
            title=_s(item.get("title") or item.get("label"))
            desc=_s(item.get("description") or item.get("desc"))
        elif isinstance(item,(list,tuple)) and len(item)>=2:
            title=_s(item[0]); desc=_s(item[1])
        else:
            title=_s(item); desc=""
        if title:
            out.append({"title":title,"description":desc})
    return out


def _nodes(raw):
    out=[]
    for item in (raw or [])[:6]:
        if isinstance(item,dict):
            label=_s(item.get("label") or item.get("title") or item.get("name"))
            sub=_s(item.get("sub") or item.get("description") or item.get("details"))
        else:
            label=_s(item); sub=""
        if label:
            out.append({"label":label,"sub":sub})
    return out


def _rows(raw, limit=4):
    out=[]
    for row in (raw or [])[:limit]:
        if isinstance(row,(list,tuple)):
            vals=[_s(x) for x in row[:2]]
            if vals:
                vals += [""]*(2-len(vals))
                out.append(vals[:2])
        elif isinstance(row,dict):
            a=_s(row.get("label") or row.get("from") or row.get("left"))
            b=_s(row.get("value") or row.get("to") or row.get("right"))
            if a: out.append([a,b])
        else:
            v=_s(row)
            if v: out.append([v,""])
    return out


def _arch(raw, topic):
    raw=raw if isinstance(raw,dict) else {}
    # Crucial: accept Gemini's title OR label, then always expose both.
    label=_s(raw.get("label") or raw.get("title") or raw.get("name") or f"{topic} Flow")
    title=_s(raw.get("title") or raw.get("label") or raw.get("name") or label)
    typ=_s(raw.get("type") or raw.get("template") or "linear_flow")

    return {
        "type":typ,
        "label":label,
        "title":title,
        "nodes":_nodes(raw.get("nodes") or raw.get("flow") or raw.get("steps")),
        "connections":[_s(x) for x in (raw.get("connections") or raw.get("edges") or raw.get("links") or [])[:8] if _s(x)],
    }


def _normalize(data, topic, category):
    if not isinstance(data,dict):
        raise ValueError("Gemini content must be an object")

    ideas=_ideas(data.get("key_ideas") or data.get("key_concepts"))
    arch=_arch(data.get("architecture") or data.get("diagram"), topic)

    if len(arch["nodes"]) < 2:
        raise ValueError(f"Gemini returned insufficient architecture nodes for '{topic}'")

    # Reject generic placeholder content instead of posting it.
    bad = {"title","description","input","process","output","impact"}
    if any(
        _s(i.get("title")).casefold() in bad or _s(i.get("description")).casefold() == "description"
        for i in ideas
    ):
        raise ValueError(f"Gemini returned placeholder key ideas for '{topic}'")

    return {
        "title":topic,
        "category":category,
        "tagline":_s(data.get("tagline") or data.get("subtitle") or f"Practical breakdown of {topic}."),
        "overview":_s(data.get("overview") or data.get("summary") or f"Understand {topic}."),
        "key_ideas":ideas[:4],
        "key_concepts":[(i["title"],i["description"]) for i in ideas[:4]],
        "architecture":arch,
        "diagram_title":arch["label"],
        "example_title":_s(data.get("example_title") or data.get("exampleTitle") or "Example"),
        "example_rows":_rows(data.get("example_rows") or data.get("exampleRows")),
        "failure_title":_s(data.get("failure_title") or data.get("failureTitle") or "Failure / Impact"),
        "failure_before":_rows(data.get("failure_before") or data.get("failureBefore"),3),
        "failure_after":_rows(data.get("failure_after") or data.get("failureAfter"),3),
        "scenarios":data.get("scenarios") or [],
        "best_practices":[_s(x) for x in (data.get("best_practices") or [])[:4] if _s(x)],
        "use_cases":[_s(x) for x in (data.get("use_cases") or [])[:4] if _s(x)],
        "diagram":"",
    }


def build_content(item: dict) -> dict:
    topic=_s(item.get("topic"))
    if not topic:
        raise ValueError("Topic cannot be empty")

    category=_s(item.get("category") or detect_category(topic)).casefold()
    enabled=os.getenv("GEMINI_ENABLED","true").strip().casefold() != "false"
    has_key=bool(os.getenv("GEMINI_API_KEY","").strip())

    if enabled and has_key:
        from src.content.gemini_content import generate_topic_content
        try:
            generated=generate_topic_content(topic,category)
            content=_normalize(generated,topic,category)
            if item.get("overview"): content["overview"]=_s(item["overview"])
            if item.get("best_practices"): content["best_practices"]=item["best_practices"][:4]
            if item.get("use_cases"): content["use_cases"]=item["use_cases"][:4]
            return content
        except Exception as exc:
            # Do NOT silently create generic placeholder content.
            # Let the topic fail and be retried rather than publishing bad content.
            raise RuntimeError(f"Topic-specific Gemini content failed for '{topic}': {exc}") from exc

    return _fallback_content(topic,category)
