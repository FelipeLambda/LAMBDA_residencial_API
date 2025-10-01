from django.urls import path
from .views import (
    MaintenanceListCreateAPIView,
    MaintenanceDetailAPIView,
    MaintenanceCompleteAPIView,
    MaintenanceAttachmentUploadAPIView,
    MaintenanceAttachmentDeleteAPIView
)

urlpatterns = [
    path('', MaintenanceListCreateAPIView.as_view(), name='maintenance-list-create'),
    path('<int:pk>/', MaintenanceDetailAPIView.as_view(), name='maintenance-detail'),
    path('<int:pk>/complete/', MaintenanceCompleteAPIView.as_view(), name='maintenance-complete'),
    path('<int:maintenance_id>/attachments/', MaintenanceAttachmentUploadAPIView.as_view(), name='maintenance-attachments'),
    path('<int:maintenance_id>/attachments/<int:attachment_id>/', MaintenanceAttachmentDeleteAPIView.as_view(), name='maintenance-attachment-delete'),
]