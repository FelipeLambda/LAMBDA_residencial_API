from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer
from Usuarios.permissions import MaintenanceOwnerOrManager

class MaintenanceListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filtrar solicitudes según permisos
        if request.user.has_perm('Mantenimiento.view_maintenance_all'):
            # Admin puede ver todas las solicitudes
            qs = MaintenanceRequest.objects.all()
        else:
            # Usuario normal solo ve sus propias solicitudes
            qs = MaintenanceRequest.objects.filter(solicitado_por=request.user)

        serializer = MaintenanceRequestSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaintenanceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req = serializer.save(solicitado_por=request.user)
        return Response(MaintenanceRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class MaintenanceDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, MaintenanceOwnerOrManager]

    def get(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)
        self.check_object_permissions(request, maintenance)
        return Response(MaintenanceRequestSerializer(maintenance).data)

    def put(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

        # Solo admin puede asignar/modificar mantenimientos
        if not request.user.has_perm('Mantenimiento.assign_maintenance'):
            return Response({'detail': 'No tienes permiso para modificar este recurso.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = MaintenanceRequestSerializer(maintenance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MaintenanceCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

        # Solo admin puede completar mantenimientos
        if not request.user.has_perm('Mantenimiento.complete_maintenance'):
            return Response({'detail': 'No tienes permiso para completar este mantenimiento.'},
                            status=status.HTTP_403_FORBIDDEN)

        costo_final = request.data.get('costo_final', None)
        maintenance.mark_completed(costo_final=costo_final)
        return Response({'detail': 'Mantenimiento marcado como completado.'}, status=status.HTTP_200_OK)