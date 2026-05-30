from rest_framework import generics, permissions
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.views import APIView
from .models import Application, MLResult
from .serializers import ApplicationSerializer


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