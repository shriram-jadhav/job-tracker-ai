from rest_framework import generics, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from .models import Application, MLResult
from .serializers import ApplicationSerializer

from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from collections import Counter


class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status']
    search_fields      = ['company', 'role']
    ordering_fields    = ['created_at', 'applied_at', 'fit_score']

    def get_queryset(self):
        # Users only see THEIR OWN applications — critical security rule
        return Application.objects.filter(user=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)

class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields   = ['status']
    search_fields      = ['company', 'role']
    ordering_fields    = ['created_at', 'applied_at', 'fit_score']

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class ApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class ApplicationSuggestionsView(APIView):
    """Returns improvement suggestions for a specific application."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            application = Application.objects.get(pk=pk, user=request.user)
        except Application.DoesNotExist:
            return Response({'error': 'Application not found'}, status=404)

        try:
            ml_result = application.ml_result
            return Response({
                'application_id': pk,
                'company':        application.company,
                'role':           application.role,
                'fit_score':      ml_result.fit_score,
                'interview_prob': ml_result.interview_prob,
                'suggestions':    ml_result.suggestions,
                'skill_gaps':     ml_result.skill_gaps,
                'shap_values':    ml_result.shap_values,
            })
        except MLResult.DoesNotExist:
            return Response({'error': 'No ML results yet. Make sure resume is uploaded and JD text is provided.'}, status=404)


class AnalyticsDashboardView(APIView):
    """
    Single endpoint returning all data needed for the dashboard.
    Aggregates application stats, scores, skill gaps, and activity.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user         = request.user
        applications = Application.objects.filter(user=user)
        total        = applications.count()

        if total == 0:
            return Response({'message': 'No applications yet.'})

        # ── 1. Status breakdown ───────────────────────────────
        by_status = dict(
            applications.values_list('status')
                        .annotate(count=Count('status'))
                        .values_list('status', 'count')
        )
        # Ensure all statuses present even if 0
        for status in ['applied', 'interview', 'offer', 'rejected', 'wishlist']:
            by_status.setdefault(status, 0)

        # ── 2. Average fit score ──────────────────────────────
        avg_score = applications.aggregate(
            avg=Avg('fit_score')
        )['avg']
        avg_score = round(avg_score, 2) if avg_score else 0.0

        # ── 3. Top skill gaps across all applications ─────────
        all_gaps = []
        for app in applications.prefetch_related('ml_result'):
            try:
                all_gaps.extend(app.ml_result.skill_gaps)
            except MLResult.DoesNotExist:
                pass

        top_skill_gaps = [
            {'skill': skill, 'count': count}
            for skill, count in Counter(all_gaps).most_common(8)
        ]

        # ── 4. Weekly activity (last 8 weeks) ─────────────────
        today      = timezone.now().date()
        week_start = today - timedelta(weeks=8)
        weekly     = []

        for i in range(8):
            week_begin = week_start + timedelta(weeks=i)
            week_end   = week_begin + timedelta(days=6)
            count      = applications.filter(
                applied_at__range=[week_begin, week_end]
            ).count()
            weekly.append({
                'week':  week_begin.strftime('%b %d'),
                'count': count
            })

        # ── 5. Score trend (latest 10 applications) ───────────
        score_trend = []
        recent = applications.filter(
            fit_score__isnull=False
        ).order_by('created_at')[:10]

        for app in recent:
            score_trend.append({
                'company':   app.company,
                'role':      app.role,
                'fit_score': app.fit_score,
                'status':    app.status,
            })

        # ── 6. Interview conversion rate ──────────────────────
        interviewed = by_status.get('interview', 0) + by_status.get('offer', 0)
        conversion  = round((interviewed / total) * 100, 1) if total > 0 else 0.0

        # ── 7. Average interview probability ──────────────────
        probs = []
        for app in applications.prefetch_related('ml_result'):
            try:
                if app.ml_result.interview_prob is not None:
                    probs.append(app.ml_result.interview_prob)
            except MLResult.DoesNotExist:
                pass
        avg_prob = round(sum(probs) / len(probs), 4) if probs else None

        return Response({
            'total_applications':     total,
            'by_status':              by_status,
            'average_fit_score':      avg_score,
            'average_interview_prob': avg_prob,
            'conversion_rate':        conversion,
            'top_skill_gaps':         top_skill_gaps,
            'weekly_activity':        weekly,
            'score_trend':            score_trend,
        })