from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Application


@receiver(post_save, sender=Application)
def score_application(sender, instance, **kwargs):
    post_save.disconnect(score_application, sender=Application)

    try:
        if not instance.jd_text:
            return

        resume = getattr(instance.user, 'resume', None)
        if not resume or not resume.raw_text:
            return

        from resumes.scorer import score_resume_jd, get_skill_gaps
        from resumes.predictor import predict_interview_probability
        from .models import MLResult

        # ── Fit score ─────────────────────────────────────────
        score = score_resume_jd(resume.raw_text, instance.jd_text)
        gaps  = get_skill_gaps(resume.skills, instance.jd_text)

        # ── Interview probability ─────────────────────────────
        skills_count     = len(resume.skills)
        skill_gaps_count = len(gaps)
        experience_yrs   = resume.experience_yrs

        prob, shap_summary = predict_interview_probability(
            fit_score        = score,
            experience_yrs   = experience_yrs,
            skills_count     = skills_count,
            skill_gaps_count = skill_gaps_count,
        )

        # ── Save everything ───────────────────────────────────
        Application.objects.filter(pk=instance.pk).update(fit_score=score)

        MLResult.objects.update_or_create(
            application=instance,
            defaults={
                'fit_score':      score,
                'skill_gaps':     gaps,
                'interview_prob': prob,
                'shap_values':    shap_summary,
            }
        )

    finally:
        post_save.connect(score_application, sender=Application)