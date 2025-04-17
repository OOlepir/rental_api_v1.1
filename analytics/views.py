from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter

from .models import SearchHistory, ViewHistory
from .serializers import (
    SearchHistorySerializer,
    ViewHistorySerializer,
    PopularSearchSerializer
)
from properties.models import Property

@extend_schema(
    summary="Популярные поисковые запросы",
    description="Возвращает 10 самых популярных поисковых запросов за последние 30 дней.",
    responses={200: PopularSearchSerializer}
)
class PopularSearchesView(generics.ListAPIView):
    serializer_class = PopularSearchSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        last_month = timezone.now() - timedelta(days=30)
        return SearchHistory.objects.filter(
            timestamp__gte=last_month
        ).values('query').annotate(
            count=Count('query')
        ).order_by('-count')[:10]

@extend_schema(
    summary="История просмотров пользователя",
    description="Возвращает историю просмотров текущего пользователя.",
    responses={200: ViewHistorySerializer}
)
class UserViewHistoryView(generics.ListAPIView):
    serializer_class = ViewHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ViewHistory.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')

@extend_schema(
    summary="Запись просмотра объявления",
    description="Записывает просмотр объявления пользователем и увеличивает счетчик просмотров.",
    parameters=[
        OpenApiParameter(name='property_id', location=OpenApiParameter.PATH, description='ID объявления', required=True, type=int)
    ],
    responses={
        200: OpenApiResponse(description="Просмотр объявления записан"),
        404: OpenApiResponse(description="Объявление не найдено")
    }
)
class RecordPropertyViewView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, property_id):
        try:
            property_obj = Property.objects.get(pk=property_id)

            view_history, created = ViewHistory.objects.get_or_create(
                user=request.user,
                property=property_obj,
                defaults={'timestamp': timezone.now()}
            )

            if not created:
                view_history.timestamp = timezone.now()
                view_history.save()

            property_obj.views_count += 1
            property_obj.save()

            return Response({"message": "Просмотр объявления записан"}, status=status.HTTP_200_OK)
        except Property.DoesNotExist:
            return Response({"detail": "Объявление не найдено"}, status=status.HTTP_404_NOT_FOUND)

