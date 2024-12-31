from django.db import models
from users.models import CustomUser
import uuid
# Create your models here.
class StoreProfile(models.Model):
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='store_profile')
    logo = models.ImageField(upload_to='store_logos/', blank=True, null=True)
    address = models.TextField()
    instagram_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.user.email