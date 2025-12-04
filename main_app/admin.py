from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Patient, Appointment, Report
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    list_display = ("email", "first_name", "last_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_staff", "is_active")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "role", "specialization")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "first_name", "last_name", "role", "password1", "password2", "is_staff", "is_active")}
        ),
    )

    search_fields = ("email", "first_name", "last_name", "role")
    ordering = ("email",)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Patient)
admin.site.register(Appointment)
admin.site.register(Report)
