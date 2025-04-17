from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Property
from .serializers import PropertySerializer, PropertyToggleSerializer
from .permissions import IsOwnerOrReadOnly

@extend_schema(
    summary="Управление объявлениями",
    description="Создание, редактирование и просмотр списка активных объявлений. Только владелец может редактировать свои объявления.",
    responses={200: PropertySerializer}
)
class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['housing_type', 'location', 'rooms']
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'views_count', 'review_count']

    def get_queryset(self):
        return Property.objects.annotate(
            review_count=Count('reviews')
        ).filter(is_active=True)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views_count += 1
        instance.save()
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Переключение активности объявления",
        description="Меняет статус активности объявления. Только владелец может изменить.",
        responses={200: OpenApiResponse(description="Изменен статус активности"), 403: OpenApiResponse(description="Нет доступа")}
    )
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        property = self.get_object()
        if property.owner != request.user:
            return Response({'detail': 'Нет доступа'}, status=403)
        property.is_active = not property.is_active
        property.save()
        return Response({'status': 'Изменен статус активности'})
