from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from Base.views import PqrsPagination
from LAMBDA_residencial_API.decorators import permission_required
from .email import send_pqrs_created_notification, send_pqrs_response_notification
from .models import PQRS, PQRSAttachment
from .serializers import PqrsSerializer, PQRSAttachmentSerializer

class PqrsListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PqrsSerializer
    pagination_class = PqrsPagination

    def get_queryset(self):
        if self.request.user.has_perm('Pqrs.view_pqrs_all'):
            return PQRS.objects.all()
        else:
            return PQRS.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        pqrs = serializer.save(usuario=self.request.user)
        send_pqrs_created_notification(pqrs)


class PqrsDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        pqrs = get_object_or_404(PQRS, pk=pk)

        if pqrs.usuario != request.user and not request.user.has_perm('Pqrs.view_pqrs_all'):
            return Response({'detail': 'No tiene permiso para ver esta PQRS.'},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(PqrsSerializer(pqrs).data)

    @permission_required('Pqrs.respond_pqrs')
    def put(self, request, pk):
        pqrs = get_object_or_404(PQRS, pk=pk)

        respuesta = request.data.get('respuesta', None)
        estado = request.data.get('estado', None)
        should_notify = False

        if respuesta:
            pqrs.respuesta = respuesta
            pqrs.respondido_por = request.user
            pqrs.fecha_respuesta = timezone.now()
            should_notify = True

        if estado:
            pqrs.estado = estado

        pqrs.save()

        if should_notify:
            send_pqrs_response_notification(pqrs)

        return Response(PqrsSerializer(pqrs).data)


class PQRSAttachmentUploadAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pqrs_id):
        pqrs = get_object_or_404(PQRS, pk=pqrs_id)

        if pqrs.usuario != request.user and not request.user.has_perm('Pqrs.view_pqrs_all'):
            return Response({'detail': 'No tiene permiso para subir archivos a esta PQRS.'},
                            status=status.HTTP_403_FORBIDDEN)

        archivo = request.FILES.get('archivo')
        if not archivo:
            return Response({'detail': 'No se proporcionó ningún archivo.'},
                            status=status.HTTP_400_BAD_REQUEST)

        max_size = 10 * 1024 * 1024  
        if archivo.size > max_size:
            return Response({'detail': 'El archivo es demasiado grande. Máximo 10MB.'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Crear el adjunto
        attachment = PQRSAttachment.objects.create(
            pqrs=pqrs,
            archivo=archivo,
            nombre_original=archivo.name,
            tamaño=archivo.size,
            tipo_contenido=archivo.content_type,
            subido_por=request.user
        )

        serializer = PQRSAttachmentSerializer(attachment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get(self, request, pqrs_id):
        """Lista todos los archivos adjuntos de una PQRS"""
        pqrs = get_object_or_404(PQRS, pk=pqrs_id)

        if pqrs.usuario != request.user and not request.user.has_perm('Pqrs.view_pqrs_all'):
            return Response({'detail': 'No tiene permiso para ver archivos de esta PQRS.'},
                            status=status.HTTP_403_FORBIDDEN)

        attachments = pqrs.attachments.all()
        serializer = PQRSAttachmentSerializer(attachments, many=True, context={'request': request})
        return Response(serializer.data)


class PQRSAttachmentDeleteAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pqrs_id, attachment_id):
        attachment = get_object_or_404(PQRSAttachment, pk=attachment_id, pqrs_id=pqrs_id)

        if attachment.subido_por != request.user and not request.user.has_perm('Pqrs.view_pqrs_all'):
            return Response({'detail': 'No tiene permiso para eliminar este archivo.'},
                            status=status.HTTP_403_FORBIDDEN)

        if attachment.archivo:
            attachment.archivo.delete()

        attachment.delete()
        return Response({'detail': 'Archivo eliminado correctamente.'}, status=status.HTTP_200_OK)