from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import PQRS, PQRSAttachment

Usuario = get_user_model()

class PQRSAttachmentSerializer(serializers.ModelSerializer):
    subido_por = serializers.StringRelatedField(read_only=True)
    archivo_url = serializers.SerializerMethodField()
    extension = serializers.ReadOnlyField()
    tamaño_mb = serializers.ReadOnlyField()

    class Meta:
        model = PQRSAttachment
        fields = ['id', 'archivo', 'archivo_url', 'nombre_original', 'tamaño',
                  'tamaño_mb', 'tipo_contenido', 'extension', 'subido_por', 'subido_en']
        read_only_fields = ['subido_por', 'subido_en']

    def get_archivo_url(self, obj):
        request = self.context.get('request')
        if obj.archivo and request:
            return request.build_absolute_uri(obj.archivo.url)
        return None

class PqrsSerializer(serializers.ModelSerializer):
    creado = serializers.DateTimeField(read_only=True)
    modificado = serializers.DateTimeField(read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    respondido_por = serializers.PrimaryKeyRelatedField(read_only=True)
    attachments = PQRSAttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = PQRS
        fields = [
            'id', 'usuario', 'apartamento', 'tipo', 'asunto', 'descripcion',
            'estado', 'respuesta', 'respondido_por', 'fecha_respuesta',
            'creado', 'modificado', 'attachments'
        ]
        read_only_fields = ['creado', 'modificado', 'respondido_por', 'fecha_respuesta']