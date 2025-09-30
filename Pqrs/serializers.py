from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import PQRS

Usuario = get_user_model()

class PqrsSerializer(serializers.ModelSerializer):
    creado = serializers.DateTimeField(read_only=True)
    modificado = serializers.DateTimeField(read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(read_only=True)
    respondido_por = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = PQRS
        fields = [
            'id', 'usuario', 'apartamento', 'tipo', 'asunto', 'descripcion',
            'estado', 'respuesta', 'respondido_por', 'fecha_respuesta', 'creado', 'modificado'
        ]
        read_only_fields = ['creado', 'modificado', 'respondido_por', 'fecha_respuesta']