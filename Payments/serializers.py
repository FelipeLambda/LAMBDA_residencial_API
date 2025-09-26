from rest_framework import serializers
from .models import Payment
from django.contrib.auth import get_user_model

Usuario = get_user_model()

class PaymentSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='creado', read_only=True)
    updated_at = serializers.DateTimeField(source='modificado', read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'apartamento', 'usuario', 'periodo', 'monto', 'metodo',
            'referencia', 'status', 'fecha_pago', 'nota', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status', 'fecha_pago']