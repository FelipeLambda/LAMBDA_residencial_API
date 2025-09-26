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
        # Si no tiene permiso de ver todas, solo ve las suyas
        if not request.user.has_perm('Visits.view_visits_all'):
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
        if (
            not request.user.has_perm('Visits.view_visits_all')
            and v.ingresado_por != request.user
            and v.autoriza_por != request.user
        ):
            return Response({'detail': 'No tienes permiso para ver esta visita.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(VisitSerializer(v).data)

    def put(self, request, pk):
        v = get_object_or_404(Visit, pk=pk)
        if (
            v.ingresado_por != request.user
            and not request.user.has_perm('Visits.view_visits_all')
        ):
            return Response({'detail': 'No tienes permiso para editar esta visita.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = VisitSerializer(v, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class VisitAuthorizeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        v = get_object_or_404(Visit, pk=pk)
        # Solo el autorizado por la visita o quien tenga permiso puede autorizar
        if (
            request.user != v.autoriza_por
            and not request.user.has_perm('Visits.authorize_visit')
        ):
            return Response({'detail': 'No tienes permiso para autorizar esta visita.'},
                            status=status.HTTP_403_FORBIDDEN)
        v.autorizado = True
        v.save(update_fields=['autorizado'])
        return Response({'detail': 'Visita autorizada.'}, status=status.HTTP_200_OK)