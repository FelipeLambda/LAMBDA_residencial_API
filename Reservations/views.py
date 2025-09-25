from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Reservation, CommonArea
from .serializers import ReservationSerializer, CommonAreaSerializer

class CommonAreaListCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        areas = CommonArea.objects.all()
        serializer = CommonAreaSerializer(areas, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Solo administradores pueden crear áreas.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = CommonAreaSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReservationCreateAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ReservationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save(created_by=request.user)
        return Response(ReservationSerializer(reservation).data, status=status.HTTP_201_CREATED)


class ReservationListAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        area_id = request.query_params.get('area')
        apartamento_id = request.query_params.get('apartamento')
        status_filter = request.query_params.get('status')
        mine = request.query_params.get('mine', 'false').lower() in ('1','true','yes')

        qs = Reservation.objects.all()

        if not request.user.is_staff and not mine:
            qs = qs.filter(created_by=request.user)
        elif mine:
            qs = qs.filter(created_by=request.user)

        if area_id:
            qs = qs.filter(area_id=area_id)
        if apartamento_id:
            qs = qs.filter(apartamento_id=apartamento_id)
        if status_filter:
            qs = qs.filter(status=status_filter.upper())

        serializer = ReservationSerializer(qs, many=True)
        return Response(serializer.data)


class ReservationDetailAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Reservation, pk=pk)

    def get(self, request, pk):
        reserva = self.get_object(pk)
        if reserva.created_by != request.user and not request.user.is_staff:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = ReservationSerializer(reserva)
        return Response(serializer.data)

    def put(self, request, pk):
        reserva = self.get_object(pk)
        if reserva.created_by != request.user and not request.user.is_staff:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        if reserva.status != Reservation.STATUS_PENDING and not request.user.is_staff:
            return Response({'detail': 'No se puede editar una reserva aprobada/rechazada.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ReservationSerializer(reserva, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        reserva = self.get_object(pk)
        if reserva.created_by != request.user and not request.user.is_staff:
            return Response({'detail': 'No tiene permiso para eliminar esta reserva.'}, status=status.HTTP_403_FORBIDDEN)
        reserva.status = Reservation.STATUS_CANCELLED
        reserva.save(update_fields=['status'])
        return Response({'detail': 'Reserva cancelada.'}, status=status.HTTP_200_OK)


class ReservationApproveAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]

    def post(self, request, pk):
        reserva = get_object_or_404(Reservation, pk=pk)
        action = request.data.get('action', '').lower()
        if action not in ('approve', 'reject'):
            return Response({'detail': 'action debe ser "approve" o "reject".'}, status=status.HTTP_400_BAD_REQUEST)

        if action == 'approve':
            # Validación final de solapamiento antes de aprobar
            temp_data = {
                'apartamento': reserva.apartamento_id,
                'area': reserva.area_id,
                'fecha_inicio': reserva.fecha_inicio,
                'fecha_fin': reserva.fecha_fin
            }
            from .serializers import ReservationSerializer
            s = ReservationSerializer(reserva, data=temp_data, partial=True)
            try:
                s.is_valid(raise_exception=True)
            except Exception:
                return Response({'detail': 'No se puede aprobar: existe solapamiento.'}, status=status.HTTP_400_BAD_REQUEST)

            reserva.status = Reservation.STATUS_APPROVED
            reserva.approved_by = request.user
            reserva.save(update_fields=['status', 'approved_by'])
            return Response({'detail': 'Reserva aprobada.'}, status=status.HTTP_200_OK)

        reserva.status = Reservation.STATUS_REJECTED
        reserva.approved_by = request.user
        reserva.save(update_fields=['status', 'approved_by'])
        return Response({'detail': 'Reserva rechazada.'}, status=status.HTTP_200_OK)