from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import MaintenanceRequest
from .serializers import MaintenanceRequestSerializer

class MaintenanceListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = MaintenanceRequest.objects.all()
        if not request.user.has_perm('Maintenance.view_maintenance_all'):
            qs = qs.filter(solicitado_por=request.user)
        serializer = MaintenanceRequestSerializer(qs, many=True)
        return Response(serializer.data)
    # Cualquiera autenticado puede crear su propia solicitud de mantenimiento
    def post(self, request):
        serializer = MaintenanceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req = serializer.save(solicitado_por=request.user)
        return Response(MaintenanceRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class MaintenanceDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        if not request.user.has_perm('Maintenance.view_maintenance_all') and req.solicitado_por != request.user:
            return Response({'detail': 'No tienes permiso para ver esta solicitud.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(MaintenanceRequestSerializer(req).data)

    def put(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        if not request.user.has_perm('Maintenance.assign_maintenance'):
            return Response({'detail': 'No tienes permiso para modificar este recurso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MaintenanceRequestSerializer(req, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MaintenanceCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        if not request.user.has_perm('Maintenance.complete_maintenance'):
            return Response({'detail': 'No tiene permiso para marcar el mantenimiento como completado.'},
                            status=status.HTTP_403_FORBIDDEN)
        costo_final = request.data.get('costo_final', None)
        req.mark_completed(costo_final=costo_final)
        return Response({'detail': 'Mantenimiento marcado como completado.'}, status=status.HTTP_200_OK)