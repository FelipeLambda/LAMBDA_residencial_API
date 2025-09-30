from django.shortcuts import get_object_or_404
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from Base.views import PagosPagination
from LAMBDA_residencial_API.decorators import permission_required
from .models import Payment
from .serializers import PaymentSerializer

class PaymentListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PaymentSerializer
    pagination_class = PagosPagination

    def get_queryset(self):
        # Filtrar pagos según permisos
        if self.request.user.has_perm('Pagos.view_pago_all'):
            # Admin puede ver todos los pagos
            return Payment.objects.all()
        else:
            # Usuario normal solo ve sus propios pagos
            return Payment.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)


class PaymentDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)

        # Permitir acceso si es propietario del pago o tiene permiso para ver todos
        if payment.usuario != request.user and not request.user.has_perm('Pagos.view_pago_all'):
            return Response({'detail': 'No tiene permiso para ver este pago.'},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(PaymentSerializer(payment).data)

    @permission_required('Pagos.mark_pago')
    def put(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        serializer = PaymentSerializer(payment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class PaymentMarkPaidAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @permission_required('Pagos.mark_pago')
    def post(self, request, pk):
        payment = get_object_or_404(Payment, pk=pk)
        referencia = request.data.get('referencia', None)
        fecha = request.data.get('fecha_pago', None)
        payment.mark_as_paid(fecha=fecha, referencia=referencia)
        return Response({'detail': 'Pago marcado como pagado.'}, status=status.HTTP_200_OK)