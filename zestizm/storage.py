from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

# Secure storage for purchased files
secure_storage = FileSystemStorage(
    location=os.path.join(settings.MEDIA_ROOT, "secure"),
    base_url=os.path.join(settings.MEDIA_URL, "secure/"),
)

# Public storage for previews, images, etc.
public_storage = FileSystemStorage(
    location=os.path.join(settings.MEDIA_ROOT, "public"),
    base_url=os.path.join(settings.MEDIA_URL, "public/"),
)
