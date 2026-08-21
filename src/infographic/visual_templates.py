from __future__ import annotations

# Template metadata keeps visual rules centralized.
# generator.py/drawing.py consume these values instead of scattering
# category-specific decisions across the rendering code.

TEMPLATE_MAP = {
    "kafka": "kafka_consumer_group",
    "java": "java_runtime",
    "spring": "spring_request",
    "aws": "aws_flow",
    "redis": "redis_cache",
    "sql": "sql_query",
    "docker": "docker_container",
    "production": "observability",
}

DEFAULT_TEMPLATE = "generic"


def template_for(category: str) -> str:
    return TEMPLATE_MAP.get(category, DEFAULT_TEMPLATE)


def palette_for(template_name: str) -> dict[str, tuple[int, int, int]]:
    palettes = {
        "kafka_consumer_group": {
            "primary": (168, 79, 255),
            "secondary": (53, 176, 255),
            "accent": (67, 235, 218),
        },
        "java_runtime": {
            "primary": (154, 77, 255),
            "secondary": (55, 154, 255),
            "accent": (96, 229, 157),
        },
        "spring_request": {
            "primary": (220, 45, 100),
            "secondary": (75, 176, 255),
            "accent": (78, 229, 179),
        },
        "aws_flow": {
            "primary": (255, 149, 48),
            "secondary": (80, 150, 255),
            "accent": (94, 227, 179),
        },
        "redis_cache": {
            "primary": (246, 76, 104),
            "secondary": (105, 77, 255),
            "accent": (71, 221, 214),
        },
        "sql_query": {
            "primary": (68, 151, 255),
            "secondary": (161, 78, 255),
            "accent": (89, 226, 170),
        },
        "docker_container": {
            "primary": (68, 176, 255),
            "secondary": (83, 116, 255),
            "accent": (86, 230, 206),
        },
        "observability": {
            "primary": (255, 174, 63),
            "secondary": (126, 78, 255),
            "accent": (76, 224, 186),
        },
        "generic": {
            "primary": (161, 78, 255),
            "secondary": (61, 164, 255),
            "accent": (81, 225, 215),
        },
    }
    return palettes.get(template_name, palettes["generic"])
