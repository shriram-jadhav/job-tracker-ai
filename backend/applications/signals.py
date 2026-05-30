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
        from resumes.suggestions import generate_suggestions
        from .models import MLResult

        # ── Fit score + gaps ──────────────────────────────────
        score = score_resume_jd(resume.raw_text, instance.jd_text)
        gaps  = get_skill_gaps(resume.skills, instance.jd_text)

        # ── Interview probability + SHAP ──────────────────────
        prob, shap_summary = predict_interview_probability(
            fit_score        = score,
            experience_yrs   = resume.experience_yrs,
            skills_count     = len(resume.skills),
            skill_gaps_count = len(gaps),
        )

        # ── Suggestions ───────────────────────────────────────
        suggestions = generate_suggestions(
            resume_text = resume.raw_text,
            jd_text     = instance.jd_text,
            skill_gaps  = gaps,
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
                'suggestions':    suggestions,
            }
        )

    finally:
        post_save.connect(score_application, sender=Application)