from rest_framework import serializers
from .models import PQRS
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class PqrsSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='creado', read_only=True)
    updated_at = serializers.DateTimeField(source='modificado', read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    respondido_por = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)

    class Meta:
        model = PQRS
        fields = [
            'id', 'usuario', 'apartamento', 'tipo', 'asunto', 'descripcion',
            'estado', 'respuesta', 'respondido_por', 'fecha_respuesta', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'respondido_por', 'fecha_respuesta']