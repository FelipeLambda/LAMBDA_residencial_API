from django.urls import path
from .views import (
    UsuarioRegisterAPIView,
    UsuarioListAPIView,
    UsuarioDetailAPIView,
    CustomTokenObtainPairView,
    UsuarioMeAPIView,
    UsuarioLogoutAPIView,
    PasswordResetRequestAPIView,
    PasswordResetConfirmAPIView,
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UsuarioRegisterAPIView.as_view(), name='user-register'),
    path('', UsuarioListAPIView.as_view(), name='user-list'),           
    path('me/', UsuarioMeAPIView.as_view(), name='user-me'),
    path('<int:pk>/', UsuarioDetailAPIView.as_view(), name='user-detail'), 
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', UsuarioLogoutAPIView.as_view(), name='user-logout'),
    path('password-reset/', PasswordResetRequestAPIView.as_view(), name='password-reset'),
    path('password-reset/confirm/', PasswordResetConfirmAPIView.as_view(), name='password-reset-confirm'),
]