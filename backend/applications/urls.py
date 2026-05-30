from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationDetailView,
    ApplicationSuggestionsView,
    AnalyticsDashboardView,
)

urlpatterns = [
    path('',                          ApplicationListCreateView.as_view(), name='application-list-create'),
    path('<int:pk>/',                 ApplicationDetailView.as_view(),     name='application-detail'),
    path('<int:pk>/suggestions/',     ApplicationSuggestionsView.as_view(), name='application-suggestions'),
    path('analytics/dashboard/',      AnalyticsDashboardView.as_view(),    name='analytics-dashboard'),
]