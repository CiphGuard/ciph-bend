from django.contrib import admin
from .models import CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    list_display = [
        "username",
        "email",
        "is_active",
        "is_staff",
        "is_superuser",
    ]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    search_fields = ["username", "email"]


admin.site.register(CustomUser, CustomUserAdmin)
