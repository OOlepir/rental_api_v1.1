
from rest_framework import viewsets, status, filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view

from .models import Review
from .serializers import ReviewSerializer
from .permissions import IsOwnerOrReadOnly

@extend_schema_view(
    list=extend_schema(summary="Список отзывов", responses={200: ReviewSerializer}),
    create=extend_schema(summary="Создание отзыва", responses={201: ReviewSerializer}),
    retrieve=extend_schema(summary="Детали отзыва", responses={200: ReviewSerializer}),
    update=extend_schema(summary="Обновление отзыва", responses={200: ReviewSerializer}),
    partial_update=extend_schema(summary="Частичное обновление отзыва", responses={200: ReviewSerializer}),
    destroy=extend_schema(summary="Удаление отзыва", responses={204: None})
)
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['rating', 'created_at']
    search_fields = ['text']
    ordering_fields = ['created_at', 'rating']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(
    summary="Отзывы по ID объявления",
    description="Возвращает список отзывов, относящихся к определенному объявлению по его ID.",
    responses={200: ReviewSerializer}
)
class PropertyReviewsView(ListAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        property_id = self.kwargs.get('property_id')
        return Review.objects.filter(property_id=property_id)