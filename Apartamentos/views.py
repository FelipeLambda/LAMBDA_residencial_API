from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from Base.views import ApartamentosPagination
from LAMBDA_residencial_API.decorators import permission_required
from .models import Apartamento
from .serializers import ApartamentoSerializer

Usuario = get_user_model()

class ApartamentoListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = ApartamentoSerializer
    pagination_class = ApartamentosPagination
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filtrar apartamentos según permisos
        if self.request.user.has_perm('Apartamentos.manage_apartamentos'):
            # Admin puede ver todos los apartamentos
            return Apartamento.objects.filter(is_active=True)
        else:
            # Usuario normal solo ve sus propios apartamentos
            return Apartamento.objects.filter(propietario=self.request.user, is_active=True)

    @permission_required('Apartamentos.manage_apartamentos')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ApartamentoDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Apartamento, pk=pk, is_active=True)

    def get(self, request, pk):
        apartment = self.get_object(pk)

        # Permitir acceso si es propietario o tiene permiso de gestión
        if apartment.propietario != request.user and not request.user.has_perm('Apartamentos.manage_apartamentos'):
            return Response({'detail': 'No tiene permiso para ver este apartamento.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = ApartamentoSerializer(apartment)
        return Response(serializer.data)

    @permission_required('Apartamentos.manage_apartamentos')
    def put(self, request, pk):
        apartment = get_object_or_404(Apartamento, pk=pk)
        serializer = ApartamentoSerializer(apartment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @permission_required('Apartamentos.manage_apartamentos')
    def delete(self, request, pk):
        apartment = get_object_or_404(Apartamento, pk=pk)
        apartment.is_active = False
        apartment.save(update_fields=['is_active'])
        return Response({'detail': 'Apartamento desactivado.'}, status=status.HTTP_200_OK)