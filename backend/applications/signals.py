from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application


@receiver(post_save, sender=Application)
def score_application(sender, instance, **kwargs):
    """
    Auto-runs after every Application save.
    If JD text exists and user has a resume, calculate fit score.
    """
    # Avoid infinite loop — disconnect signal temporarily
    post_save.disconnect(score_application, sender=Application)

    try:
        # Only score if JD text is provided
        if not instance.jd_text:
            return

        # Check if user has an uploaded resume
        resume = getattr(instance.user, 'resume', None)
        if not resume or not resume.raw_text:
            return

        # Import here to avoid circular imports
        from resumes.scorer import score_resume_jd, get_skill_gaps

        # Calculate fit score
        score = score_resume_jd(resume.raw_text, instance.jd_text)

        # Calculate skill gaps and store in ml_results
        gaps = get_skill_gaps(resume.skills, instance.jd_text)

        # Save score back to application
        Application.objects.filter(pk=instance.pk).update(fit_score=score)

        # Save skill gaps to MLResult
        from .models import MLResult
        MLResult.objects.update_or_create(
            application=instance,
            defaults={
                'fit_score':  score,
                'skill_gaps': gaps,
            }
        )

    finally:
        # Always reconnect signal
        post_save.connect(score_application, sender=Application)