from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Apartamento
from .serializers import ApartamentoSerializer
from Usuarios.permissions import (
    CanManageApartments,
    ApartmentOwnerOrManager
)

Usuario = get_user_model()

class ApartamentoListCreateAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanManageApartments()]
        return [permissions.IsAuthenticated()]

    def get(self, request):
        # Filtrar apartamentos según permisos
        if request.user.has_perm('Apartamentos.manage_apartamentos'):
            # Admin puede ver todos los apartamentos
            qs = Apartamento.objects.filter(is_active=True)
        else:
            # Usuario normal solo ve sus propios apartamentos
            qs = Apartamento.objects.filter(propietario=request.user, is_active=True)

        serializer = ApartamentoSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ApartamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ApartamentoDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, ApartmentOwnerOrManager]

    def get(self, request, pk):
        apartment = get_object_or_404(Apartamento, pk=pk, is_active=True)
        self.check_object_permissions(request, apartment)
        serializer = ApartamentoSerializer(apartment)
        return Response(serializer.data)

    def put(self, request, pk):
        apartment = get_object_or_404(Apartamento, pk=pk)

        # Solo admin puede editar apartamentos
        if not request.user.has_perm('Apartamentos.manage_apartamentos'):
            return Response({'detail': 'Solo administradores pueden editar apartamentos.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ApartamentoSerializer(apartment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        apartment = get_object_or_404(Apartamento, pk=pk)

        # Solo admin puede eliminar apartamentos
        if not request.user.has_perm('Apartamentos.manage_apartamentos'):
            return Response({'detail': 'Solo administradores pueden eliminar apartamentos.'},
                            status=status.HTTP_403_FORBIDDEN)

        apartment.is_active = False
        apartment.save(update_fields=['is_active'])
        return Response({'detail': 'Apartamento desactivado.'}, status=status.HTTP_200_OK)