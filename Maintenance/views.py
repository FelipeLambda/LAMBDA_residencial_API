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
        if not request.user.is_staff:
            qs = qs.filter(solicitado_por=request.user)
        serializer = MaintenanceRequestSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MaintenanceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        req = serializer.save(solicitado_por=request.user)
        return Response(MaintenanceRequestSerializer(req).data, status=status.HTTP_201_CREATED)


class MaintenanceDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        if not request.user.is_staff and req.solicitado_por != request.user:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(MaintenanceRequestSerializer(req).data)

    def put(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        # Solo admin puede cambiar estado/asignar
        if not request.user.is_staff:
            return Response({'detail': 'Solo administradores pueden modificar este recurso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = MaintenanceRequestSerializer(req, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class MaintenanceCompleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request, pk):
        req = get_object_or_404(MaintenanceRequest, pk=pk)
        costo_final = request.data.get('costo_final', None)
        req.mark_completed(costo_final=costo_final)
        return Response({'detail': 'Mantenimiento marcado como completado.'}, status=status.HTTP_200_OK)