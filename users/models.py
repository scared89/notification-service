from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(
        max_length=15,
        unique=True,
        verbose_name='Телефон'
    )
    email = models.EmailField(
        max_length=50,
        blank=True,
        null=True
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        blank=True,
        null=True,
        verbose_name='Телеграм ID'
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'