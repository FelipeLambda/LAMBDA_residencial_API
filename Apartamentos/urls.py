from django.urls import path
from .views import ApartamentoListCreateAPIView, ApartamentoDetailAPIView

urlpatterns = [
    path('', ApartamentoListCreateAPIView.as_view(), name='apartamento-list-create'),
    path('<int:pk>/', ApartamentoDetailAPIView.as_view(), name='apartamento-detail'),
]