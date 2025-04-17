# === users/cookies_manager.py ===
from datetime import datetime
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def set_jwt_cookies(response: Response, user: User) -> Response:
    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token

    access_expiry = datetime.fromtimestamp(access_token['exp'])
    refresh_expiry = datetime.fromtimestamp(refresh_token['exp'])

    response.set_cookie("access_token", str(access_token), httponly=True, expires=access_expiry)
    response.set_cookie("refresh_token", str(refresh_token), httponly=True, expires=refresh_expiry)
    return response