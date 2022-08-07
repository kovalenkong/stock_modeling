from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name='Почта')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()


class Dataset(models.Model):
    data = models.TextField(
        verbose_name='Датасет',
        blank=False, null=False,
        help_text='Значения потребления (каждое значение с новой строки)'
    )
    parameters = models.TextField(
        verbose_name='Параметры',
        blank=False, null=False,
        help_text='Параметры модели (используется как json поле)'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True, null=True
    )
    author = models.ForeignKey(
        to=User, on_delete=models.SET_NULL,
        related_name='datasets', verbose_name='Датасет',
        blank=True, null=True
    )
    is_public = models.BooleanField(
        verbose_name='Публичный',
        null=False, default=False
    )
    dt_created = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True, auto_now=False
    )
    dt_edited = models.DateTimeField(
        verbose_name='Дата редактирования',
        auto_now_add=False, auto_now=True
    )


class Algorithm(models.Model):
    author = models.ForeignKey(
        to=User, on_delete=models.SET_NULL,
        related_name='algorithms', verbose_name='Автор',
        blank=True, null=True
    )
    formula_point_refill = models.CharField(
        verbose_name='Формула точки пополнения заказа',
        max_length=255,
        blank=False, null=False
    )
    formula_order_size = models.CharField(
        verbose_name='Формула размера заказа',
        max_length=255,
        blank=False, null=False
    )
    formula_score = models.CharField(
        verbose_name='Формула оценивающей метрики',
        max_length=255,
        blank=True, null=True
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True, null=True
    )
    is_public = models.BooleanField(
        verbose_name='Публичный',
        null=False, default=False
    )
    dt_created = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True, auto_now=False
    )
    dt_edited = models.DateTimeField(
        verbose_name='Дата редактирования',
        auto_now_add=False, auto_now=True
    )
