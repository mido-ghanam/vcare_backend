from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from authentication.models import User

class RegisterSerializer(serializers.Serializer):
  full_name = serializers.CharField(
    max_length=150,
    error_messages={"required": "The full_name field is required."},
  )
  phone = PhoneNumberField(
    error_messages={"required": "The phone field is required."}
  )
  password = serializers.CharField(
    write_only=True,
    trim_whitespace=False,
    error_messages={"required": "The password field is required."},
  )

  def validate_phone(self, value):
    if User.objects.filter(phone=value).exists():
      raise serializers.ValidationError("The phone has already been taken.")
    return value

  def validate_password(self, value):
    try:
      validate_password(value)
    except DjangoValidationError as exc:
      raise serializers.ValidationError(exc.messages) from exc
    return value

  def create(self, validated_data):
    user = User(
      full_name=validated_data["full_name"],
      phone=validated_data["phone"],
    )
    user.set_password(validated_data["password"])
    user.save()
    return user


class LoginSerializer(serializers.Serializer):
  phone = serializers.RegexField(
    regex=r"^[0-9]+$",
    error_messages={
      "required": "The phone field is required.",
      "invalid": "The phone must contain digits only.",
    },
  )
  password = serializers.CharField(
    write_only=True,
    trim_whitespace=False,
    error_messages={"required": "The password field is required."},
  )


class ApiErrorResponseSerializer(serializers.Serializer):
  message = serializers.CharField()
  data = serializers.JSONField()
  status = serializers.BooleanField()
  code = serializers.IntegerField()


class RegisterTokenSerializer(serializers.Serializer):
  access = serializers.CharField()
  refresh = serializers.CharField()


class RegisterDataSerializer(serializers.Serializer):
  token = RegisterTokenSerializer()


class RegisterResponseSerializer(serializers.Serializer):
  message = serializers.CharField()
  data = RegisterDataSerializer()
  status = serializers.BooleanField()
  code = serializers.IntegerField()


class LoginDataSerializer(serializers.Serializer):
  token = serializers.CharField()
  username = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
  message = serializers.CharField()
  data = LoginDataSerializer()
  status = serializers.BooleanField()
  code = serializers.IntegerField()


class LogoutResponseSerializer(serializers.Serializer):
  message = serializers.CharField()
  data = serializers.ListField()
  status = serializers.BooleanField()
  code = serializers.IntegerField()
