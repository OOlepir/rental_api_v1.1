from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import Booking
from .serializers import BookingSerializer, BookingCreateSerializer, BookingUpdateSerializer
from .permissions import OnlyOwnerChangeStatus

@extend_schema_view(
    list=extend_schema(summary="Список бронирований", responses={200: BookingSerializer}),
    create=extend_schema(summary="Создание бронирования", responses={201: BookingSerializer}),
    retrieve=extend_schema(summary="Просмотр бронирования", responses={200: BookingSerializer}),
    update=extend_schema(summary="Обновление бронирования", responses={200: BookingSerializer}),
    partial_update=extend_schema(summary="Частичное обновление бронирования", responses={200: BookingSerializer}),
    destroy=extend_schema(summary="Удаление бронирования", responses={204: OpenApiResponse(description="Удалено")})
)
class BookingViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, OnlyOwnerChangeStatus]
    queryset = Booking.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'tenant':
            return Booking.objects.filter(tenant=user)
        return Booking.objects.filter(property__owner=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return BookingCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BookingUpdateSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        if self.request.user.user_type != 'tenant':
            raise PermissionDenied("Только арендаторы могут создавать бронирования")
        property_obj = serializer.validated_data['property']
        if property_obj.owner == self.request.user:
            raise PermissionDenied("Нельзя бронировать собственное жилье")
        serializer.save(tenant=self.request.user)

    @extend_schema(
        summary="Подтверждение бронирования",
        description="Подтвердить активное ожидающее бронирование. Доступно только владельцу жилья.",
        responses={200: BookingSerializer}
    )
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        booking = self.get_object()
        if booking.property.owner != request.user:
            return Response({"detail": "Вы не владелец жилья"}, status=403)
        if booking.status != 'pending':
            return Response({"detail": "Нельзя подтвердить это бронирование"}, status=400)
        booking.status = 'confirmed'
        booking.save()
        return Response({"message": "Бронирование подтверждено"})

    @extend_schema(
        summary="Отклонение бронирования",
        description="Отклонить активное ожидающее бронирование. Доступно только владельцу жилья.",
        responses={200: BookingSerializer}
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        booking = self.get_object()
        if booking.property.owner != request.user:
            return Response({"detail": "Вы не владелец жилья"}, status=403)
        if booking.status != 'pending':
            return Response({"detail": "Нельзя отклонить это бронирование"}, status=400)
        booking.status = 'rejected'
        booking.save()
        return Response({"message": "Бронирование отклонено"})

    @extend_schema(
        summary="Отмена бронирования",
        description="Арендатор отменяет свое бронирование.",
        responses={200: BookingSerializer}
    )
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.tenant != request.user:
            return Response({"detail": "Вы не можете отменить"}, status=403)
        if booking.status not in ['pending', 'confirmed']:
            return Response({"detail": "Отмена невозможна"}, status=400)
        booking.status = 'canceled'
        booking.save()
        return Response({"message": "Бронирование отменено"})
