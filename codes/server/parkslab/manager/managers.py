from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class PersonManager(BaseUserManager):

    def create_user(self, identifier, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')

        email = PersonManager.normalize_email(email)
        person = self.model(
            identifier=identifier,
            email=email,
            **extra_fields
        )
        person.set_password(password)
        person.save(using=self._db)

        return person