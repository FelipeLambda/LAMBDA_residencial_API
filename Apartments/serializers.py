from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Apartamento

Usuario = get_user_model()

class ApartamentoSerializer(serializers.ModelSerializer):
    propietario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Apartamento
        fields = ['id', 'numero', 'torre', 'piso', 'tipo', 'area_m2', 'propietario', 'ocupantes', 'descripcion', 'creado', 'modificado', 'is_active']
        read_only_fields = ['creado', 'modificado']