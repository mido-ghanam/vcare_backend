
from rest_framework.permissions import AllowAny, IsAuthenticated
from datetime import datetime, timezone as datetime_timezone
from drf_spectacular.utils import OpenApiResponse, extend_schema
from .serializers import (
  ApiErrorResponseSerializer,
  LoginResponseSerializer,
  LoginSerializer,
  LogoutResponseSerializer,
  RegisterResponseSerializer,
  RegisterSerializer,
)
from rest_framework_simplejwt.tokens import RefreshToken
from .authentication import RevocableJWTAuthentication
from authentication.models import RevokedToken, User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from rest_framework import status

def validation_error_response(errors):
  return Response(
    {
      "message": "Unprocessable Entity",
      "data": errors,
      "status": False,
      "code": status.HTTP_422_UNPROCESSABLE_ENTITY,
    },
    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
  )

class RegisterAPIView(APIView):
  permission_classes = [AllowAny]

  @extend_schema(
    tags=["Authentication"],
    request=RegisterSerializer,
    responses={
      201: RegisterResponseSerializer,
      422: ApiErrorResponseSerializer,
    },
    auth=[],
    description="Create a user account and return access and refresh tokens.",
  )
  def post(self, request):
    serializer = RegisterSerializer(data=request.data)
    if not serializer.is_valid(): return validation_error_response(serializer.errors)

    user = serializer.save()
    token = RefreshToken.for_user(user)
    return Response(
      {
        "message": "Registered Successfully.",
        "data": {
          "token": {
            "access": str(token.access_token),
            "refresh": str(token),
          }
        },
        "status": True,
        "code": status.HTTP_201_CREATED,
      },
      status=status.HTTP_201_CREATED,
    )

class LoginAPIView(APIView):
  permission_classes = [AllowAny]

  @extend_schema(
    tags=["Authentication"],
    request=LoginSerializer,
    responses={
      200: LoginResponseSerializer,
      401: ApiErrorResponseSerializer,
      422: ApiErrorResponseSerializer,
    },
    auth=[],
    description="Authenticate with a phone number and password.",
  )
  def post(self, request):
    serializer = LoginSerializer(data=request.data)
    if not serializer.is_valid(): return validation_error_response(serializer.errors)

    phone = f"+{serializer.validated_data['phone']}"
    user = User.objects.filter(phone=phone).first()
    if user is None or not user.check_password(serializer.validated_data["password"]):
      return Response(
        {
          "message": "Invalid credentials.",
          "data": [],
          "status": False,
          "code": status.HTTP_401_UNAUTHORIZED,
        },
        status=status.HTTP_401_UNAUTHORIZED,
      )

    token = RefreshToken.for_user(user)
    return Response(
      {
        "message": "Loggedin Successfuly.",
        "data": {
          "token": {
            "access": str(token.access_token),
            "refresh": str(token),
          },
          "username": user.full_name,
        },
        "status": True,
        "code": status.HTTP_200_OK,
      },
      status=status.HTTP_200_OK,
    )


class LogoutAPIView(APIView):
  authentication_classes = [RevocableJWTAuthentication]
  permission_classes = [IsAuthenticated]

  @extend_schema(
    tags=["Authentication"],
    request=None,
    responses={
      200: LogoutResponseSerializer,
      401: OpenApiResponse(description="A valid bearer access token is required."),
    },
    description="Revoke the bearer access token used for this request.",
  )
  def post(self, request):
    token = request.auth
    RevokedToken.objects.filter(expires_at__lte=timezone.now()).delete()
    RevokedToken.objects.create(
      jti=token["jti"],
      expires_at=datetime.fromtimestamp(
        token["exp"],
        tz=datetime_timezone.utc,
      ),
    )
    return Response(
      {
        "message": "Loggedout Successfuly",
        "data": [],
        "status": True,
        "code": status.HTTP_200_OK,
      },
      status=status.HTTP_200_OK,
    )