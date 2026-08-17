from src.platforms.base import PlatformPublisher,PublishResult
class InstagramPublisher(PlatformPublisher):
    name="instagram"
    def __init__(self,access_token,account_id): self.access_token=access_token; self.account_id=account_id
    def publish(self,image_url,caption):
        if not self.access_token or not self.account_id: return PublishResult(False,message="Instagram credentials are not configured.")
        return PublishResult(False,message="Instagram adapter stub: configure current official Graph API call and permissions here.")
