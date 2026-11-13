from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import RevokedToken, User


class CustomUserCreationForm(UserCreationForm):
  class Meta(UserCreationForm.Meta):
    model = User
    fields = ("phone", "full_name")


class CustomUserChangeForm(UserChangeForm):
  class Meta(UserChangeForm.Meta):
    model = User
    fields = "__all__"


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
  add_form = CustomUserCreationForm
  form = CustomUserChangeForm
  model = User

  list_display = ("phone", "full_name", "user_type", "is_staff", "is_active")
  list_filter = ("user_type", "is_staff", "is_active")
  search_fields = ("phone", "full_name")
  ordering = ("phone",)

  fieldsets = (
    (None, {"fields": ("phone", "password")}),
    ("Personal info", {"fields": ("full_name", "user_type")}),
    ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
    ("Important dates", {"fields": ("last_login", "date_joined")}),
  )
  add_fieldsets = (
    (None, {
      "classes": (" wide",),
      "fields": ("phone", "full_name", "password1", "password2", "user_type", "is_staff", "is_superuser", "is_active"),
    }),
  )
  filter_horizontal = ("groups", "user_permissions")
  readonly_fields = ("last_login", "date_joined")


@admin.register(RevokedToken)
class RevokedTokenAdmin(admin.ModelAdmin):
  list_display = ("jti", "expires_at")
  search_fields = ("jti",)
  list_filter = ("expires_at",)