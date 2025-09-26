from django.urls import path
from .views import (
    MaintenanceListCreateAPIView,
    MaintenanceDetailAPIView,
    MaintenanceCompleteAPIView,
)

urlpatterns = [
    path('', MaintenanceListCreateAPIView.as_view(), name='maintenance-list-create'),
    path('<int:pk>/', MaintenanceDetailAPIView.as_view(), name='maintenance-detail'),
    path('<int:pk>/complete/', MaintenanceCompleteAPIView.as_view(), name='maintenance-complete'),
]