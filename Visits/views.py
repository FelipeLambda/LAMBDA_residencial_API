from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Visit
from .serializers import VisitSerializer

class VisitListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        qs = Visit.objects.all()
        if not request.user.is_staff:
            qs = qs.filter(ingresado_por=request.user)
        serializer = VisitSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = serializer.save(ingresado_por=request.user)
        return Response(VisitSerializer(visit).data, status=status.HTTP_201_CREATED)


class VisitDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        v = get_object_or_404(Visit, pk=pk)
        if not request.user.is_staff and v.ingresado_por != request.user and v.autoriza_por != request.user:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(VisitSerializer(v).data)

    def put(self, request, pk):
        v = get_object_or_404(Visit, pk=pk)
        if not request.user.is_staff and v.ingresado_por != request.user:
            return Response({'detail': 'No tiene permiso.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = VisitSerializer(v, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class VisitAuthorizeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        v = get_object_or_404(Visit, pk=pk)
        if request.user != v.autoriza_por and not request.user.is_staff:
            return Response({'detail': 'No tiene permiso para autorizar.'}, status=status.HTTP_403_FORBIDDEN)
        v.autorizado = True
        v.save(update_fields=['autorizado'])
        return Response({'detail': 'Visita autorizada.'}, status=status.HTTP_200_OK)