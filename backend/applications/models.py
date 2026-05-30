from django.db import models
from django.conf import settings


class Application(models.Model):

    class Status(models.TextChoices):
        APPLIED    = 'applied',    'Applied'
        INTERVIEW  = 'interview',  'Interview'
        OFFER      = 'offer',      'Offer'
        REJECTED   = 'rejected',   'Rejected'
        WISHLIST   = 'wishlist',   'Wishlist'

    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    company      = models.CharField(max_length=150)
    role         = models.CharField(max_length=150)
    jd_text      = models.TextField(blank=True)
    jd_url       = models.URLField(blank=True)
    status       = models.CharField(max_length=20, choices=Status.choices, default=Status.WISHLIST)
    salary       = models.CharField(max_length=50, blank=True)
    location     = models.CharField(max_length=100, blank=True)
    notes        = models.TextField(blank=True)
    fit_score    = models.FloatField(null=True, blank=True)
    applied_at   = models.DateField(null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.role} at {self.company} ({self.user.email})"
    
class MLResult(models.Model):
    application    = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='ml_result')
    fit_score      = models.FloatField(null=True, blank=True)
    interview_prob = models.FloatField(null=True, blank=True)
    skill_gaps     = models.JSONField(default=list)
    shap_values    = models.JSONField(default=dict)
    suggestions    = models.JSONField(default=list)   # ← add this
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ML Result for {self.application}"