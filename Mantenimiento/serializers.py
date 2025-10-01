from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import MaintenanceAttachment, MaintenanceRequest

Usuario = get_user_model()

class MaintenanceAttachmentSerializer(serializers.ModelSerializer):
    subido_por = serializers.StringRelatedField(read_only=True)
    archivo_url = serializers.SerializerMethodField()
    extension = serializers.ReadOnlyField()
    tamaño_mb = serializers.ReadOnlyField()

    class Meta:
        model = MaintenanceAttachment
        fields = ['id', 'archivo', 'archivo_url', 'nombre_original', 'tamaño',
                  'tamaño_mb', 'tipo_contenido', 'extension', 'subido_por',
                  'subido_en', 'es_evidencia_final']
        read_only_fields = ['subido_por', 'subido_en']

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)
        return None

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    creado = serializers.DateTimeField(read_only=True)
    modificado = serializers.DateTimeField(read_only=True)
    solicitado_por = serializers.PrimaryKeyRelatedField(read_only=True)
    asignado_a = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)
    attachments = MaintenanceAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'area', 'descripcion', 'solicitado_por', 'asignado_a',
            'fecha_programada', 'fecha_finalizado', 'costo_estimado', 'costo_final',
            'estado', 'notificar_residentes', 'comentario_admin',
            'creado', 'modificado', 'attachments'
        ]
        read_only_fields = ['creado', 'modificado', 'solicitado_por']