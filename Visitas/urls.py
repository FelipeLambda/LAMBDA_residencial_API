from django.urls import path
from .views import VisitListCreateAPIView, VisitDetailAPIView, VisitAuthorizeAPIView

urlpatterns = [
    path('', VisitListCreateAPIView.as_view(), name='visit-list-create'),
    path('<int:pk>/', VisitDetailAPIView.as_view(), name='visit-detail'),
    path('<int:pk>/authorize/', VisitAuthorizeAPIView.as_view(), name='visit-authorize'),
]