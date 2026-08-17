HASHTAGS={
"kafka":["#Kafka","#Java","#Microservices","#Backend","#SoftwareEngineering"],
"redis":["#Redis","#Java","#Backend","#Caching","#SoftwareEngineering"],
"spring":["#SpringBoot","#Java","#Microservices","#Backend","#SoftwareEngineering"],
"java":["#Java","#Programming","#Backend","#SoftwareEngineering","#Developers"],
"aws":["#AWS","#Cloud","#DevOps","#Backend","#SoftwareEngineering"],
"mongodb":["#MongoDB","#NoSQL","#Backend","#Database","#SoftwareEngineering"],
"docker":["#Docker","#DevOps","#Microservices","#Backend","#SoftwareEngineering"],
"microservices":["#Microservices","#Java","#Architecture","#Backend","#SoftwareEngineering"],
"sql":["#SQL","#Database","#Backend","#Programming","#SoftwareEngineering"],
"security":["#Security","#Java","#Backend","#WebDevelopment","#SoftwareEngineering"],
"generic":["#Tech","#Programming","#Backend","#SoftwareEngineering","#Developers"]}

def generate_caption(topic: str, category: str)->dict[str,str]:
    h=HASHTAGS.get(category,HASHTAGS["generic"])
    ig=f"{topic} explained 🚀\n\nA practical visual breakdown of {topic.lower()} — focusing on core concepts, architecture and real-world usage.\n\nSave this for interview prep and daily learning.\n\n"+" ".join(h)
    li=f"{topic} — practical breakdown 🚀\n\nToday’s cheat sheet covers the fundamentals of {topic.lower()}, with emphasis on how it fits into modern backend and distributed systems.\n\nKey takeaways:\n• Core concept\n• Architecture / flow\n• Common use case\n• Important implementation point\n\nWhich topic should be covered next?\n\n"+" ".join(h)
    return {"instagram":ig,"linkedin":li,"hashtags":" ".join(h)}
