from django.urls import path
from .views import PqrsListCreateAPIView, PqrsDetailAPIView

urlpatterns = [
    path('', PqrsListCreateAPIView.as_view(), name='pqrs-list-create'),
    path('<int:pk>/', PqrsDetailAPIView.as_view(), name='pqrs-detail'),
]