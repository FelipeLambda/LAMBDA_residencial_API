from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from Base.views import MantenimientoPagination
from LAMBDA_residencial_API.decorators import permission_required
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer

class MaintenanceListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    pagination_class = MantenimientoPagination

    def get_queryset(self):
        # Filtrar solicitudes según permisos
        if self.request.user.has_perm('Mantenimiento.view_maintenance_all'):
            # Admin puede ver todas las solicitudes
            return MaintenanceRequest.objects.all()
        else:
            # Usuario normal solo ve sus propias solicitudes
            return MaintenanceRequest.objects.filter(solicitado_por=self.request.user)

    def perform_create(self, serializer):
        serializer.save(solicitado_por=self.request.user)


class MaintenanceDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

        # Permitir acceso si es quien solicitó o tiene permiso para ver todas
        if maintenance.solicitado_por != request.user and not request.user.has_perm('Mantenimiento.view_maintenance_all'):
            return Response({'detail': 'No tiene permiso para ver esta solicitud.'},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(MaintenanceRequestSerializer(maintenance).data)

    @permission_required('Mantenimiento.assign_maintenance')
    def put(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)
        serializer = MaintenanceRequestSerializer(maintenance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MaintenanceCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @permission_required('Mantenimiento.complete_maintenance')
    def post(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)
        costo_final = request.data.get('costo_final', None)
        maintenance.mark_completed(costo_final=costo_final)
        return Response({'detail': 'Mantenimiento marcado como completado.'}, status=status.HTTP_200_OK)