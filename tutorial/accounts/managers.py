from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, username, email, organization, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not username:
            raise ValueError("User must have a username")
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not organization:
            raise ValueError("User must have an organization")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.username = username
        user.organization = organization
        user.is_admin = False
        user.is_staff = False
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, organization, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        user = self.model(
            email=self.normalize_email(email)
        )
        user.username = username
        user.email = email
        user.organization = organization
        user.set_password(password)  # change password to hash
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)

        if not username:
            raise ValueError("User must have a username")
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not organization:
            raise ValueError("User must have an organization")
        return user

    def create_staffuser(self, username, email, organization, password=None):
        if not username:
            raise ValueError("User must have a username")
        if not email:
            raise ValueError("User must have an email")
        if not password:
            raise ValueError("User must have a password")
        if not organization:
            raise ValueError("User must have an organization")

        user = self.model(
            email=self.normalize_email(email)
        )
        user.username = username
        user.email = email
        user.organization = organization
        user.set_password(password)  # change password to hash
        user.is_admin = False
        user.is_staff = True
        user.save(using=self._db)
        return user

