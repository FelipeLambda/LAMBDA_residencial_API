from rest_framework import serializers
from .models import MaintenanceRequest
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class MaintenanceRequestSerializer(serializers.ModelSerializer):
    creado = serializers.DateTimeField(read_only=True)
    modificado = serializers.DateTimeField(read_only=True)
    solicitado_por = serializers.PrimaryKeyRelatedField(read_only=True)
    asignado_a = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)

    class Meta:
        model = MaintenanceRequest
        fields = [
            'id', 'area', 'descripcion', 'solicitado_por', 'asignado_a',
            'fecha_programada', 'fecha_finalizado', 'costo_estimado', 'costo_final',
            'estado', 'notificar_residentes', 'comentario_admin',
            'creado', 'modificado'
        ]
        read_only_fields = ['creado', 'modificado', 'solicitado_por']