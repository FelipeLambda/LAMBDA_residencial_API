from rest_framework import serializers
from .models import Visit
from Apartamentos.models import Apartamento
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class VisitSerializer(serializers.ModelSerializer):
    creado = serializers.DateTimeField(read_only=True)
    modificado = serializers.DateTimeField(read_only=True)
    ingresado_por = serializers.PrimaryKeyRelatedField(read_only=True)
    autoriza_por = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)
    apartamento = serializers.PrimaryKeyRelatedField(queryset=Apartamento.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Visit
        fields = [
            'id', 'visitante_nombre', 'visitante_documento', 'visitante_telefono',
            'placa', 'apartamento', 'autoriza_por', 'ingresado_por',
            'fecha_ingreso', 'fecha_salida', 'motivo', 'autorizado',
            'observaciones', 'creado', 'modificado'
        ]
        read_only_fields = ['creado', 'modificado', 'ingresado_por']