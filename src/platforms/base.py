from dataclasses import dataclass
@dataclass
class PublishResult:
    success: bool
    url: str|None=None
    message: str=""
class PlatformPublisher:
    name="base"
    def publish(self,image_url,caption): raise NotImplementedError
