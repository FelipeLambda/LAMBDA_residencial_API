from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from Base.views import UsuariosPagination
from .email import send_password_changed_notification, send_password_reset_email, send_welcome_email
from .serializers import UsuarioSerializer
from .token_serializers import CustomTokenObtainPairSerializer

Usuario = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    
    # Vista que devuelve access + refresh token
    serializer_class = CustomTokenObtainPairSerializer


class UsuarioRegisterAPIView(APIView):
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        # Enviar email de bienvenida
        send_welcome_email(user)

        data = UsuarioSerializer(user).data
        data.pop('password', None)
        return Response(data, status=status.HTTP_201_CREATED)


class UsuarioListAPIView(generics.ListAPIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    pagination_class = UsuariosPagination

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        # asegurar que password no esté en la salida
        if isinstance(response.data, dict) and 'results' in response.data:
            for item in response.data['results']:
                item.pop('password', None)
        elif isinstance(response.data, list):
            for item in response.data:
                item.pop('password', None)
        return response


class UsuarioDetailAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Usuario, pk=pk)

    def get(self, request, pk):
        usuario = self.get_object(pk)
        if request.user != usuario and not request.user.is_staff and not request.user.is_superuser:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UsuarioSerializer(usuario)
        data = serializer.data
        data.pop('password', None)
        return Response(data)

    def put(self, request, pk):
        usuario = self.get_object(pk)
        if request.user != usuario and not request.user.is_staff and not request.user.is_superuser:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = UsuarioSerializer(usuario, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UsuarioSerializer(user).data
        data.pop('password', None)
        return Response(data)


class UsuarioMeAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        data = serializer.data
        data.pop('password', None)
        return Response(data)

    def put(self, request):
        serializer = UsuarioSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UsuarioSerializer(user).data
        data.pop('password', None)
        return Response(data)


class UsuarioLogoutAPIView(APIView):
    
    # Logout mediante blacklisting del refresh token.
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        refresh_token = request.data.get('refresh', None)
        if not refresh_token:
            return Response({"detail": "Se requiere el refresh token."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return Response({"detail": "Token inválido o ya revocado."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Sesión finalizada correctamente."}, status=status.HTTP_200_OK)


class PasswordResetRequestAPIView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        correo = request.data.get('correo')
        if not correo:
            return Response({"detail": "Se requiere correo."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            # No revelar la existencia de la cuenta: responder igual 
            return Response({"detail": "Si el correo existe, se enviaron instrucciones."}, status=status.HTTP_200_OK)

        user.create_reset_token(hours_valid=2)
        email_sent = send_password_reset_email(user, user.reset_password_token)

        if settings.DEBUG:
            return Response({
                "detail": "Token generado (DEBUG: se muestra el token).",
                "reset_token": user.reset_password_token,
                "expires_at": user.reset_password_token_expires_at,
                "email_sent": email_sent
            }, status=status.HTTP_200_OK)

        # confirmamos que se procesó la solicitud
        if email_sent:
            return Response({"detail": "Si el correo existe, se enviaron instrucciones."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "Si el correo existe, se enviaron instrucciones."}, status=status.HTTP_200_OK)


class PasswordResetConfirmAPIView(APIView):

    permission_classes = [permissions.AllowAny]
    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('password')

        if not token or not new_password:
            return Response({"detail": "Se requiere token y nueva contraseña."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Usuario.objects.get(reset_password_token=token)
        except Usuario.DoesNotExist:
            return Response({"detail": "Token inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if not user.reset_token_valid():
            return Response({"detail": "Token expirado."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.reset_password_token = None
        user.reset_password_token_expires_at = None
        user.save(update_fields=['password', 'reset_password_token', 'reset_password_token_expires_at'])
        send_password_changed_notification(user)

        return Response({"detail": "Contraseña actualizada correctamente."}, status=status.HTTP_200_OK)