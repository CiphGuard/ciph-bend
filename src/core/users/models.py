from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField("correo electrónico", blank=False, unique=True)
    first_name = None
    last_name = None

    class Meta:
        db_table = "auth_user"
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"
