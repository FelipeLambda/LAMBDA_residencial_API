from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Visit
from .serializers import VisitSerializer
from Users.permissions import (
    CanAuthorizeVisits,
    CanViewAllVisits,
    VisitOwnerOrManager
)


class VisitListCreateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Filtrar visitas según permisos
        if request.user.has_perm('Visits.view_visits_all'):
            # Admin puede ver todas las visitas
            qs = Visit.objects.all()
        else:
            # Usuario normal solo ve sus propias visitas
            qs = Visit.objects.filter(ingresado_por=request.user)

        serializer = VisitSerializer(qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = VisitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        visit = serializer.save(ingresado_por=request.user)
        return Response(VisitSerializer(visit).data, status=status.HTTP_201_CREATED)


class VisitDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, VisitOwnerOrManager]

    def get(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)
        self.check_object_permissions(request, visit)
        return Response(VisitSerializer(visit).data)

    def put(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)

        # Solo el creador o admin pueden editar
        if (visit.ingresado_por != request.user and
            not request.user.has_perm('Visits.view_visits_all')):
            return Response({'detail': 'No tienes permiso para editar esta visita.'},
                            status=status.HTTP_403_FORBIDDEN)

        serializer = VisitSerializer(visit, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class VisitAuthorizeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)

        # Solo el autorizado por la visita o quien tenga permiso puede autorizar
        if (request.user != visit.autoriza_por and
            not request.user.has_perm('Visits.authorize_visit')):
            return Response({'detail': 'No tienes permiso para autorizar esta visita.'},
                            status=status.HTTP_403_FORBIDDEN)

        visit.autorizado = True
        visit.save(update_fields=['autorizado'])
        return Response({'detail': 'Visita autorizada.'}, status=status.HTTP_200_OK)