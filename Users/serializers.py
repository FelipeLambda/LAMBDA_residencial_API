from django.contrib.auth import get_user_model
from rest_framework import serializers

Usuario = get_user_model()

class UsuarioSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = Usuario
        fields = ['id', 'correo', 'nombres', 'apellidos', 'password', 'is_active', 'is_staff']
        extra_kwargs = {
            'is_staff': {'write_only': True},
            'is_active': {'required': False},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        is_staff = validated_data.pop('is_staff', False)
        if is_staff:
            # create_superuser espera correo, nombres, apellidos y password
            user = Usuario.objects.create_superuser(password=password, **validated_data)
        else:
            user = Usuario.objects.create_user(password=password, **validated_data)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UsuarioLoginSerializer(serializers.Serializer):
    correo = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        correo = attrs.get('correo')
        password = attrs.get('password')

        if not correo or not password:
            raise serializers.ValidationError("Se requiere correo y contraseña.")
        try:
            user = Usuario.objects.get(correo=correo)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError("Usuario o contraseña inválidos.")

        if not user.check_password(password):
            raise serializers.ValidationError("Usuario o contraseña inválidos.")
        if not user.is_active:
            raise serializers.ValidationError("Cuenta inactiva. Contacte al administrador.")

        attrs['user'] = user
        return attrs