from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from drf_spectacular.extensions import OpenApiAuthenticationExtension

from .models import RevokedToken


class RevocableJWTAuthenticationScheme(OpenApiAuthenticationExtension):
  target_class = "authentication.authentication.RevocableJWTAuthentication"
  name = "BearerAuth"

  def get_security_definition(self, auto_schema):
    return {
      "type": "http",
      "scheme": "bearer",
      "bearerFormat": "JWT",
    }


class RevocableJWTAuthentication(JWTAuthentication):
  def get_validated_token(self, raw_token):
    token = super().get_validated_token(raw_token)
    if RevokedToken.objects.filter(jti=token["jti"]).exists(): raise InvalidToken("This token has been revoked.")
    return token
