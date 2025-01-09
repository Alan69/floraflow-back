import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
import os
from PIL import Image, ImageOps
from cloudinary.models import CloudinaryField

def user_directory_path_profile(instance, filename):
    # файл будет загружен в MEDIA_ROOT/user_<uuid>/<filename>
    profile_pic_name = 'user_{0}/profile.jpg'.format(instance.user.uuid)
    full_path = os.path.join(settings.MEDIA_ROOT, profile_pic_name)

    if os.path.exists(full_path):
        os.remove(full_path)

    return profile_pic_name

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    USER_TYPE_CHOICES = [
        ('client', 'Client'),
        ('store', 'Flower Store'),
    ]

    CITY_CHOICES = [
        ('Astana', 'Астана'),
        ('Almaty', 'Алматы'),
        ('Shymkent', 'Шымкент'),
        ('Other', 'Другой'),
    ]

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False, verbose_name="Суперадмин")

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='client', verbose_name="Тип пользователя")
    phone = models.CharField(max_length=15, unique=True, verbose_name="Номер телефона")
    city = models.CharField(max_length=50, choices=CITY_CHOICES, default='Astana', verbose_name='Город')
    picture = models.ImageField(upload_to=user_directory_path_profile, blank=True, null=True, verbose_name='Аватар')
    profile_picture = CloudinaryField('profile_picture')

    last_login = models.DateTimeField(auto_now=True, verbose_name="Последний вход",  blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата регистрации", blank=True, null=True)

    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name',]

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        SIZE = 250, 250

        if self.picture:
            pic = Image.open(self.picture.path)
            if pic.mode == 'RGBA':
                alpha = pic.getchannel('A')
                alpha = ImageOps.invert(alpha)
                # Paste white onto image wherever it is transparent
                pic.paste((255, 255, 255), mask=alpha)
                pic = pic.convert('RGB')

            pic.thumbnail(SIZE, Image.LANCZOS)
            pic.save(self.picture.path)

    def __str__(self):
        return f"{self.email} ({self.user_type})"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'