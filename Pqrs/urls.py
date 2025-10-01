from django.urls import path
from .views import (
    PqrsListCreateAPIView,
    PqrsDetailAPIView,
    PQRSAttachmentUploadAPIView,
    PQRSAttachmentDeleteAPIView
)

urlpatterns = [
    path('', PqrsListCreateAPIView.as_view(), name='pqrs-list-create'),
    path('<int:pk>/', PqrsDetailAPIView.as_view(), name='pqrs-detail'),
    path('<int:pqrs_id>/attachments/', PQRSAttachmentUploadAPIView.as_view(), name='pqrs-attachments'),
    path('<int:pqrs_id>/attachments/<int:attachment_id>/', PQRSAttachmentDeleteAPIView.as_view(), name='pqrs-attachment-delete'),
]