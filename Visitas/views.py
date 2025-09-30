from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from Base.views import VisitasPagination
from LAMBDA_residencial_API.decorators import permission_required
from .models import Visit
from .serializers import VisitSerializer


class VisitListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VisitSerializer
    pagination_class = VisitasPagination

    def get_queryset(self):
        # Filtrar visitas según permisos
        if self.request.user.has_perm('Visitas.view_visits_all'):
            # Admin puede ver todas las visitas
            return Visit.objects.all()
        else:
            # Usuario normal solo ve sus propias visitas
            return Visit.objects.filter(ingresado_por=self.request.user)

    def perform_create(self, serializer):
        serializer.save(ingresado_por=self.request.user)


class VisitDetailAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)

        # Permitir acceso si es quien ingresó la visita o tiene permiso para ver todas
        if visit.ingresado_por != request.user and not request.user.has_perm('Visitas.view_visits_all'):
            return Response({'detail': 'No tiene permiso para ver esta visita.'},
                            status=status.HTTP_403_FORBIDDEN)

        return Response(VisitSerializer(visit).data)

    def put(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)

        # Solo el creador o admin pueden editar
        if visit.ingresado_por != request.user and not request.user.has_perm('Visitas.view_visits_all'):
            return Response({'detail': 'No tiene permiso para editar esta visita.'},
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
        if request.user != visit.autoriza_por and not request.user.has_perm('Visitas.authorize_visit'):
            return Response({'detail': 'No tiene permiso para autorizar esta visita.'},
                            status=status.HTTP_403_FORBIDDEN)

        visit.autorizado = True
        visit.save(update_fields=['autorizado'])
        return Response({'detail': 'Visita autorizada.'}, status=status.HTTP_200_OK)