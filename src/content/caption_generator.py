from __future__ import annotations

HASHTAGS = {
    "kafka": ["#Kafka", "#Java", "#Microservices", "#Backend", "#SoftwareEngineering"],
    "redis": ["#Redis", "#Java", "#Backend", "#Caching", "#SoftwareEngineering"],
    "spring": ["#SpringBoot", "#Java", "#Microservices", "#Backend", "#SoftwareEngineering"],
    "java": ["#Java", "#Programming", "#Backend", "#SoftwareEngineering", "#Developers"],
    "aws": ["#AWS", "#Cloud", "#DevOps", "#Backend", "#SoftwareEngineering"],
    "mongodb": ["#MongoDB", "#NoSQL", "#Backend", "#Database", "#SoftwareEngineering"],
    "docker": ["#Docker", "#DevOps", "#Microservices", "#Backend", "#SoftwareEngineering"],
    "microservices": ["#Microservices", "#Java", "#Architecture", "#Backend", "#SoftwareEngineering"],
    "sql": ["#SQL", "#Database", "#Backend", "#Programming", "#SoftwareEngineering"],
    "security": ["#Security", "#Java", "#Backend", "#WebDevelopment", "#SoftwareEngineering"],
    "generic": ["#Tech", "#Programming", "#Backend", "#SoftwareEngineering", "#Developers"],
}

def generate_captions(content: dict) -> dict[str, str]:
    tags = HASHTAGS.get(content["category"], HASHTAGS["generic"])
    tag_string = " ".join(tags)

    instagram = (
        f"{content['title']} 🚀\n\n"
        f"{content['overview']}\n\n"
        f"Save this cheat sheet for your interview prep and daily learning.\n\n"
        f"{tag_string}"
    )

    linkedin = (
        f"{content['title']} — practical breakdown 🚀\n\n"
        f"{content['overview']}\n\n"
        "Key takeaways:\n" +
        "".join(f"• {x}\n" for x in content["key_concepts"][:5]) +
        f"\nSave this for your next system design / backend discussion.\n\n{tag_string}"
    )

    return {"instagram": instagram, "linkedin": linkedin}
