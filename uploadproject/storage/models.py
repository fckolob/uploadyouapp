from django.db import models
from django.contrib.auth.models import User
import uuid
import hashlib

def upload_path(instance, filename):
    ext = filename.split('.')[-1] if '.' in filename else ''
    return f"uploads/{uuid.uuid4()}.{ext}"

class UserFile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_path)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, default='')
    checksum = models.CharField(max_length=64, default='')

    def __str__(self):
        return self.original_name

class DownloadLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(UserFile, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)

