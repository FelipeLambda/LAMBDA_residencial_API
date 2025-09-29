from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from Users.permissions import (
    CanMarkPayments,
    CanViewAllPayments,
    PaymentOwnerOrManager
)

class PaymentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filtrar pagos según permisos
        if request.user.has_perm('Payments.view_pago_all'):
            # Admin puede ver todos los pagos
            qs = Payment.objects.all()
        else:
            # Usuario normal solo ve sus propios pagos
            qs = Payment.objects.filter(usuario=request.user)

        serializer = PaymentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(usuario=request.user)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

class PaymentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, PaymentOwnerOrManager]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        self.check_object_permissions(request, payment)
        return Response(PaymentSerializer(payment).data)

    def put(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)

        # Solo admin puede modificar pagos
        if not request.user.has_perm('Payments.mark_pago'):
            return Response({'detail': 'No tiene permiso para modificar este pago.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class PaymentMarkPaidAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanMarkPayments]

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        referencia = request.data.get('referencia', None)
        fecha = request.data.get('fecha_pago', None)
        payment.mark_as_paid(fecha=fecha, referencia=referencia)
        return Response({'detail': 'Pago marcado como pagado.'}, status=status.HTTP_200_OK)