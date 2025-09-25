from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Apartamento
from .serializers import ApartamentoSerializer

Usuario = get_user_model()

class ApartamentoListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Apartamento.objects.filter(is_active=True)
        # Admin puede ver todo
        if not request.user.is_staff:
            qs = qs.filter(propietario=request.user)
        serializer = ApartamentoSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        
        # Solo admin crea apartamentos
        if not request.user.is_staff:
            return Response({'detail': 'Solo administradores pueden crear apartamentos.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ApartamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ApartamentoDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        apt = get_object_or_404(Apartamento, pk=pk, is_active=True)
        if not request.user.is_staff and apt.propietario != request.user:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ApartamentoSerializer(apt)
        return Response(serializer.data)

    def put(self, request, pk):
        apt = get_object_or_404(Apartamento, pk=pk)
        if not request.user.is_staff:
            return Response({'detail': 'Solo administradores pueden editar apartamentos.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ApartamentoSerializer(apt, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        apt = get_object_or_404(Apartamento, pk=pk)
        if not request.user.is_staff:
            return Response({'detail': 'Solo administradores pueden eliminar apartamentos.'}, status=status.HTTP_403_FORBIDDEN)
        apt.is_active = False
        apt.save(update_fields=['is_active'])
        return Response({'detail': 'Apartamento desactivado.'}, status=status.HTTP_200_OK)