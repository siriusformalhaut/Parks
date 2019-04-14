from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager


class UserAccountManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, name, display_name, birthday, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        if not name:
            raise ValueError('名前を入力してください')
        name = self.name

        if not display_name:
            raise ValueError('表示名を入力してください')

        if not birthday:
            raise ValueError('生年月日を入力してください')

        up_date = timezone.now()

        user = self.model(email=email, name=name, display_name=display_name, birthday=birthday, up_date=up_date, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, name, display_name, birthday, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, name, display_name, birthday, **extra_fields)

    def create_superuser(self, email, password, name, display_name, birthday, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, name, display_name, birthday, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('name'), max_length=128, blank=False)
    display_name = models.CharField(_('display name'), max_length=128, blank=False)
    birthday = models.DateField(_('birthday'), blank=False, default='2000-01-01')

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
 
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    up_date = models.DateTimeField(_('update date'), default=timezone.now)
    
    objects = UserAccountManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'display_name', 'birthday',]

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.display_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def username(self):
        """username属性のゲッター

        他アプリケーションが、username属性にアクセスした場合に備えて定義
        メールアドレスを返す
        """
        return self.email

class Project(models.Model):
    users = models.ManyToManyField(UserAccount)
    name = models.CharField(max_length=256)
    details = models.TextField()
    start_date = models.DateField()

    def __str__(self):
        return self.name

class CategoryM(models.Model):
    name = models.CharField(max_length=256)
    related = models.ManyToManyField("CategoryM", blank=True)

    def __str__(self):
        return self.name
