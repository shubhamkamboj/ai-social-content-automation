from __future__ import annotations
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path

def utc_now(): return datetime.now(timezone.utc).isoformat()
class StateManager:
    def __init__(self,path): self.path=Path(path); self.data=self._load()
    def _load(self):
        if not self.path.exists(): return {"version":1,"topics":{},"last_run":None}
        return json.loads(self.path.read_text(encoding="utf-8"))
    def save(self):
        self.path.parent.mkdir(parents=True,exist_ok=True); tmp=self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data,indent=2,ensure_ascii=False),encoding="utf-8"); tmp.replace(self.path)
    @staticmethod
    def topic_id(topic): return hashlib.sha256(topic.strip().casefold().encode()).hexdigest()[:16]
    def sync_topics(self,topics):
        for topic in topics:
            tid=self.topic_id(topic)
            self.data["topics"].setdefault(tid,{"id":tid,"topic":topic,"status":"PENDING","attempts":0,"created_at":utc_now(),"updated_at":utc_now(),"instagram_url":None,"linkedin_url":None,"image_path":None,"error":None})
    def next_pending(self,limit):
        vals=sorted(self.data["topics"].values(),key=lambda x:(x.get("created_at",""),x.get("topic","").casefold()))
        return [x for x in vals if x.get("status")=="PENDING"][:limit]
    def mark(self,tid,status,**extra):
        item=self.data["topics"][tid]; item["status"]=status; item["updated_at"]=utc_now(); item.update(extra)
        if status=="PROCESSING": item["attempts"]=int(item.get("attempts",0))+1
    def set_last_run(self): self.data["last_run"]=utc_now()
