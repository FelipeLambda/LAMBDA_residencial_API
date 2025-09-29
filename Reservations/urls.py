from django.urls import path
from .views import (
    CommonAreaListCreateAPIView,
    ReservationCreateAPIView,
    ReservationListAPIView,
    ReservationDetailAPIView,
    ReservationApproveAPIView,
)

urlpatterns = [
    path('areas/', CommonAreaListCreateAPIView.as_view(), name='areas-list-create'),
    path('', ReservationListAPIView.as_view(), name='reservation-list'),
    path('create/', ReservationCreateAPIView.as_view(), name='reservation-create'),
    path('<int:pk>/', ReservationDetailAPIView.as_view(), name='reservation-detail'),
    path('<int:pk>/approve/', ReservationApproveAPIView.as_view(), name='reservation-approve'),
]