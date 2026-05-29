from django.db import models
from django.conf import settings


class Resume(models.Model):
    user            = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resume')
    file            = models.FileField(upload_to='resumes/')
    raw_text        = models.TextField(blank=True)
    skills          = models.JSONField(default=list)
    experience_yrs  = models.FloatField(null=True, blank=True)
    education       = models.JSONField(default=list)
    certifications  = models.JSONField(default=list)
    uploaded_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume of {self.user.email}"