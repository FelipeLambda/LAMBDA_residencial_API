from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Payment

Usuario = get_user_model()

class PaymentSerializer(serializers.ModelSerializer):
    creado = serializers.DateTimeField(read_only=True)
    modificado = serializers.DateTimeField(read_only=True)
    usuario = serializers.PrimaryKeyRelatedField(queryset=Usuario.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Payment
        fields = [
            'id', 'apartamento', 'usuario', 'periodo', 'monto', 'metodo',
            'referencia', 'status', 'fecha_pago', 'nota', 'creado', 'modificado'
        ]
        read_only_fields = ['creado', 'modificado', 'status', 'fecha_pago']