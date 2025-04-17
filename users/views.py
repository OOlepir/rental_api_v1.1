from django.contrib.auth import authenticate
from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.generics import CreateAPIView
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .cookies_manager import set_jwt_cookies
from .models import User
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    CustomTokenObtainPairSerializer,
    LoginSerializer
)

@extend_schema(
    summary="Регистрация нового пользователя",
    description="Создает нового пользователя в системе.",
    request=RegisterSerializer,
    responses={201: UserSerializer}
)
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

@extend_schema(
    summary="Получение пары токенов",
    description="Возвращает access и refresh токены по email и паролю.",
    request=CustomTokenObtainPairSerializer,
    responses={200: OpenApiResponse(description="Токены успешно выданы")}
)
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

@extend_schema(
    summary="Получение/обновление профиля",
    description="Получает или обновляет данные авторизованного пользователя.",
    responses=UserSerializer
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@extend_schema(
    summary="Вход пользователя",
    description="Аутентифицирует пользователя и устанавливает JWT в cookies.",
    request=LoginSerializer,
    responses={
        200: OpenApiResponse(description="Успешный вход"),
        401: OpenApiResponse(description="Неверные учетные данные")
    }
)
class LoginView(CreateAPIView):
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        user = authenticate(email=request.data['email'], password=request.data['password'])
        if user:
            response = Response({"message": "Logged in successfully"}, status=status.HTTP_200_OK)
            return set_jwt_cookies(response, user)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

@extend_schema(
    summary="Выход пользователя",
    description="Удаляет access и refresh токены из cookies.",
    responses={204: OpenApiResponse(description="Успешный выход")}
)
@api_view(['GET'])
def logout(request):
    response = Response({"message": "Successful logout"}, status=status.HTTP_204_NO_CONTENT)
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return response
