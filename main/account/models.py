from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The Phone Number field must be set")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True , verbose_name="Phone Number")
    is_phone_verified = models.BooleanField(default=False, verbose_name="Is Phone Verified")
    first_name = models.CharField(max_length=30, verbose_name="First Name" , null=True, blank=True)
    last_name = models.CharField(max_length=30, verbose_name="Last Name" , null=True, blank=True)
    username = models.CharField(max_length=30, unique=True, verbose_name="Username" , null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', verbose_name="Avatar", null=True, blank=True)
    bio = models.TextField(verbose_name="Bio", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    is_active = models.BooleanField(default=True, verbose_name="Is Active")
    is_staff = models.BooleanField(default=False, verbose_name="Is Staff")

    objects = UserManager()

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone