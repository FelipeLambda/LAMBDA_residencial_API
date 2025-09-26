from django.urls import path
from .views import PaymentListCreateAPIView, PaymentDetailAPIView, PaymentMarkPaidAPIView

urlpatterns = [
    path('', PaymentListCreateAPIView.as_view(), name='payment-list-create'),
    path('<int:pk>/', PaymentDetailAPIView.as_view(), name='payment-detail'),
    path('<int:pk>/mark-paid/', PaymentMarkPaidAPIView.as_view(), name='payment-mark-paid'),
]