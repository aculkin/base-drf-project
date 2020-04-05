from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager,\
                                       PermissionsMixin
from django.conf import settings


class UserManager(BaseUserManager):

    def create_user(self, username, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not username:
            raise ValueError("Users must have an username address")
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, username, password):
        '''Creates and Saves a new superuser'''
        user = self.create_user(username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User Model that supports using username instead of username"""
    username = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'


class Tag(models.Model):
    """Tag to be used for recipe"""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
