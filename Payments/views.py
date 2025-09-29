from django.shortcuts import get_object_or_404
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer

class PaymentListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Payment.objects.all()
        if not request.user.has_perm('Payments.view_pago_all'):
            qs = qs.filter(usuario=request.user)
        serializer = PaymentSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save(usuario=request.user)
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

class PaymentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        p = get_object_or_404(Payment, pk=pk)
        # Si no tiene permiso para ver todos, sólo puede ver su pago
        if not request.user.has_perm('Payments.view_pago_all') and p.usuario != request.user:
            return Response({'detail': 'No tienes permiso para ver este pago.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(PaymentSerializer(p).data)

    def put(self, request, pk):
        p = get_object_or_404(Payment, pk=pk)
        if not request.user.has_perm('Payments.mark_pago'):
            return Response({'detail': 'No tiene permiso para modificar este pago.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PaymentSerializer(p, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class PaymentMarkPaidAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        if not request.user.has_perm('Payments.mark_pago'):
            return Response({'detail': 'No tiene permiso para marcar pago como completado.'},
                            status=status.HTTP_403_FORBIDDEN)
        referencia = request.data.get('referencia', None)
        fecha = request.data.get('fecha_pago', None)
        payment.mark_as_paid(fecha=fecha, referencia=referencia)
        return Response({'detail': 'Pago marcado como pagado.'}, status=status.HTTP_200_OK)