from rest_framework import serializers
from .models import Reservation, CommonArea
from django.utils import timezone

class CommonAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommonArea
        fields = ['id', 'nombre', 'descripcion', 'capacidad']


class ReservationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    created_by = serializers.PrimaryKeyRelatedField(read_only=True)
    approved_by = serializers.PrimaryKeyRelatedField(read_only=True)
    area = serializers.PrimaryKeyRelatedField(queryset=CommonArea.objects.all())

    class Meta:
        model = Reservation
        fields = ['id', 'apartamento', 'area', 'fecha_inicio', 'fecha_fin', 'status', 'created_by', 'approved_by', 'notas', 'created_at', 'updated_at']
        read_only_fields = ['status', 'created_by', 'approved_by', 'created_at', 'updated_at']

    def validate(self, data):
        
        #Validaciones

        start = data.get('fecha_inicio')
        end = data.get('fecha_fin')
        area = data.get('area')
        instance = getattr(self, 'instance', None)

        if not start or not end:
            raise serializers.ValidationError("Se requieren fecha_inicio y fecha_fin.")

        if start >= end:
            raise serializers.ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")

        # Reserva sea a futuro
        if start < timezone.now():
            raise serializers.ValidationError("La fecha de inicio debe ser en el futuro.")

        qs = Reservation.objects.filter(area=area).exclude(status=Reservation.STATUS_REJECTED).exclude(status=Reservation.STATUS_CANCELLED)
        if instance:
            qs = qs.exclude(pk=instance.pk)

        for r in qs:
            if r.overlaps(start, end):
                raise serializers.ValidationError("La franja seleccionada se solapa con otra reserva existente.")

        return data