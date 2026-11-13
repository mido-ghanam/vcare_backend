from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from django.db import models
import uuid

class UserManager(BaseUserManager):
  use_in_migrations = True

  def create_user(self, phone, full_name, password=None, **extra_fields):
    if not phone:
      raise ValueError("A phone number is required.")
    if not full_name:
      raise ValueError("A full name is required.")

    user = self.model(phone=phone, full_name=full_name, **extra_fields)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, phone, full_name, password=None, **extra_fields):
    extra_fields.setdefault("is_staff", True)
    extra_fields.setdefault("is_superuser", True)
    extra_fields.setdefault("is_active", True)
    extra_fields.setdefault("user_type", User.UserType.ADMIN)

    if extra_fields["is_staff"] is not True:
      raise ValueError("A superuser must have is_staff=True.")
    if extra_fields["is_superuser"] is not True:
      raise ValueError("A superuser must have is_superuser=True.")

    return self.create_user(phone, full_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
  class UserType(models.TextChoices):
    ADMIN = "admin", "Admin"
    USER = "user", "User"

  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  full_name = models.CharField(max_length=150)
  phone = PhoneNumberField(unique=True)
  user_type = models.CharField(max_length=10, choices=UserType.choices, default=UserType.USER)
  is_staff = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)
  date_joined = models.DateTimeField(default=timezone.now)

  email = None

  objects = UserManager()

  USERNAME_FIELD = "phone"
  REQUIRED_FIELDS = ["full_name"]

  def __str__(self): return str(self.phone)

class RevokedToken(models.Model):
  jti = models.CharField(max_length=255, unique=True)
  expires_at = models.DateTimeField(db_index=True)
