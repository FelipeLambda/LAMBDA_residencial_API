from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from Base.views import MantenimientoPagination
from LAMBDA_residencial_API.decorators import permission_required
from .models import MaintenanceAttachment, MaintenanceRequest
from .serializers import MaintenanceAttachmentSerializer, MaintenanceRequestSerializer

class MaintenanceListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MaintenanceRequestSerializer
    pagination_class = MantenimientoPagination

    def get_queryset(self):
        if self.request.user.has_perm('Mantenimiento.view_maintenance_all'):
            return MaintenanceRequest.objects.all()
        else:
            return MaintenanceRequest.objects.filter(solicitado_por=self.request.user)

    def perform_create(self, serializer):
        serializer.save(solicitado_por=self.request.user)


class MaintenanceDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        maintenance = get_object_or_404(MaintenanceRequest, pk=pk)

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

class MaintenanceAttachmentUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, maintenance_id):
        maintenance = get_object_or_404(MaintenanceRequest, pk=maintenance_id)

        if (maintenance.solicitado_por != request.user and
            maintenance.asignado_a != request.user and
            not request.user.has_perm('Mantenimiento.view_maintenance_all')):
            return Response({'detail': 'No tiene permiso para subir archivos a esta solicitud.'},
                            status=status.HTTP_403_FORBIDDEN)

        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'detail': 'No se proporcionó ningún archivo.'},
                            status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024  
        if archivo.size > max_size:
            return Response({'detail': 'El archivo es demasiado grande. Máximo 10MB.'},
                            status=status.HTTP_400_BAD_REQUEST)

        es_evidencia_final = request.data.get('es_evidencia_final', 'false').lower() == 'true'
        if es_evidencia_final and maintenance.asignado_a != request.user and not request.user.has_perm('Mantenimiento.view_maintenance_all'):
            es_evidencia_final = False

        attachment = MaintenanceAttachment.objects.create(
            maintenance_request=maintenance,
            archivo=archivo,
            nombre_original=archivo.name,
            tamaño=archivo.size,
            tipo_contenido=archivo.content_type,
            subido_por=request.user,
            es_evidencia_final=es_evidencia_final
        )

        serializer = MaintenanceAttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, maintenance_id):
        maintenance = get_object_or_404(MaintenanceRequest, pk=maintenance_id)

        if (maintenance.solicitado_por != request.user and
            maintenance.asignado_a != request.user and
            not request.user.has_perm('Mantenimiento.view_maintenance_all')):
            return Response({'detail': 'No tiene permiso para ver archivos de esta solicitud.'},
                            status=status.HTTP_403_FORBIDDEN)

        attachments = maintenance.attachments.all()
        serializer = MaintenanceAttachmentSerializer(attachments, many=True, context={'request': request})
        return Response(serializer.data)

class MaintenanceAttachmentDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, maintenance_id, attachment_id):
        attachment = get_object_or_404(MaintenanceAttachment, pk=attachment_id, maintenance_request_id=maintenance_id)

        if attachment.subido_por != request.user and not request.user.has_perm('Mantenimiento.view_maintenance_all'):
            return Response({'detail': 'No tiene permiso para eliminar este archivo.'},
                            status=status.HTTP_403_FORBIDDEN)

        if attachment.archivo:
            attachment.archivo.delete()

        attachment.delete()
        return Response({'detail': 'Archivo eliminado correctamente.'}, status=status.HTTP_200_OK)