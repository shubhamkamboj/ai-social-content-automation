from pathlib import Path
from src.config import Config
from src.content.caption_generator import generate_caption
from src.content.topic_parser import detect_category,read_topics
from src.infographic.generator import generate_infographic
from src.platforms.instagram import InstagramPublisher
from src.platforms.linkedin import LinkedInPublisher
from src.state_manager import StateManager

def main():
    c=Config(); state=StateManager(c.state_file); topics=read_topics(c.topics_file)
    state.sync_topics(topics); selected=state.next_pending(c.post_limit)
    print(f"Found {len(topics)} topics; selected {len(selected)}.")
    ig=InstagramPublisher(c.instagram_access_token,c.instagram_account_id)
    li=LinkedInPublisher(c.linkedin_access_token,c.linkedin_author_id)
    for item in selected:
        tid=item["id"]; topic=item["topic"]
        try:
            state.mark(tid,"PROCESSING"); state.save(); cat=detect_category(topic); caps=generate_caption(topic,cat)
            output=Path(c.output_dir)/f"{tid}.png"; generate_infographic(topic,str(output))
            state.mark(tid,"GENERATED",image_path=str(output),error=None); state.save(); print(f"[GENERATED] {topic}")
            if c.dry_run: continue
            if not c.public_base_url: raise RuntimeError("PUBLIC_BASE_URL is required for publishing.")
            image_url=f"{c.public_base_url.rstrip('/')}/{output.name}"
            if c.instagram_enabled:
                r=ig.publish(image_url,caps["instagram"])
                if not r.success: raise RuntimeError(r.message)
                state.data["topics"][tid]["instagram_url"]=r.url
            if c.linkedin_enabled:
                r=li.publish(image_url,caps["linkedin"])
                if not r.success: raise RuntimeError(r.message)
                state.data["topics"][tid]["linkedin_url"]=r.url
            state.mark(tid,"PUBLISHED",error=None); state.save(); print(f"[PUBLISHED] {topic}")
        except Exception as e:
            print(f"[FAILED] {topic}: {e}"); state.mark(tid,"FAILED",error=str(e)); state.save()
    state.set_last_run(); state.save()
if __name__=="__main__": main()
