from src.platforms.base import PlatformPublisher,PublishResult
class LinkedInPublisher(PlatformPublisher):
    name="linkedin"
    def __init__(self,access_token,author_id): self.access_token=access_token; self.author_id=author_id
    def publish(self,image_url,caption):
        if not self.access_token or not self.author_id: return PublishResult(False,message="LinkedIn credentials are not configured.")
        return PublishResult(False,message="LinkedIn adapter stub: configure current official API call and permissions here.")
