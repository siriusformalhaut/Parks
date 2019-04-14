from django.db import models
from django.core.mail import send_mail
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill
import uuid, os


class UserAccountManager(BaseUserManager):
    """ユーザーマネージャー."""

    use_in_migrations = True

    def _create_user(self, email, password, name, **extra_fields):
        """メールアドレスでの登録を必須にする"""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)

        if not name:
            raise ValueError('名前を入力してください')
        name = self.name

        up_date = timezone.now()

        user = self.model(email=email, name=name, up_date=up_date, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, name, **extra_fields):
        """is_staff(管理サイトにログインできるか)と、is_superuer(全ての権限)をFalseに"""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, name, **extra_fields)

    def create_superuser(self, email, password, name, **extra_fields):
        """スーパーユーザーは、is_staffとis_superuserをTrueに"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, name, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin):
    """カスタムユーザーモデル."""

    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(_('name'), max_length=128, blank=False)

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
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return self.name

    def get_short_name(self):
        return self.name

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

class UserProfile(models.Model):
    user_account = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=128, blank=False)
    birthday = models.DateField(blank=False, default='2000-01-01')
    details = models.TextField(blank=True)
    homepage = models.URLField(blank=True)
    title = models.CharField(max_length=128,blank=True)

    def get_image_path(self, filename):
        """カスタマイズした画像パスを取得する.

        :param self: インスタンス (models.Model)
        :param filename: 元ファイル名
        :return: カスタマイズしたファイル名を含む画像パス
        """
        prefix = 'user_profile/'
        name = str(uuid.uuid4()).replace('-', '')
        extension = os.path.splitext(filename)[-1]
        return prefix + name + extension

    def delete_previous_file(function):
        """不要となる古いファイルを削除する為のデコレータ実装.

        :param function: メイン関数
        :return: wrapper
        """
        def wrapper(*args, **kwargs):
            """Wrapper 関数.

            :param args: 任意の引数
            :param kwargs: 任意のキーワード引数
            :return: メイン関数実行結果
            """
            self = args[0]

            # 保存前のファイル名を取得
            result = UserProfile.objects.filter(pk=self.pk)
            previous = result[0] if len(result) else None
            super(UserProfile, self).save()

            # 関数実行
            result = function(*args, **kwargs)

            # 保存前のファイルがあったら削除
            if previous:
                os.remove(MEDIA_ROOT + '/' + previous.image.name)
            return result
        return wrapper

    @delete_previous_file
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(UserProfile, self).save()

    @delete_previous_file
    def delete(self, using=None, keep_parents=False):
        super(UserProfile, self).delete()

    image_origin = models.ImageField(_('image_origin'), upload_to=get_image_path, blank=True)
    image_thumbnail = ImageSpecField(source='image_origin',
                            processors=[ResizeToFill(250,250)],
                            format="JPEG",
                            options={'quality': 60}
                            )

    image_middle = ImageSpecField(source='image_origin',
                        processors=[ResizeToFill(400, 400)],
                        format="JPEG",
                        options={'quality': 75}
                        )

    def __str__(self):
        return self.display_name

class OrganizationDivM(models.Model):
    name = models.CharField(max_length=7)

    def __str__(self):
        return self.name

class Organization(models.Model):
    member = models.ManyToManyField(UserAccount)
    name = models.CharField(max_length=256)
    organization_div = models.ForeignKey(OrganizationDivM, on_delete=models.CASCADE)
    details = models.TextField(blank=True)
    homepage = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    def get_image_path(self, filename):
        """カスタマイズした画像パスを取得する.

        :param self: インスタンス (models.Model)
        :param filename: 元ファイル名
        :return: カスタマイズしたファイル名を含む画像パス
        """
        prefix = 'organization/'
        name = str(uuid.uuid4()).replace('-', '')
        extension = os.path.splitext(filename)[-1]
        return prefix + name + extension

    def delete_previous_file(function):
        """不要となる古いファイルを削除する為のデコレータ実装.

        :param function: メイン関数
        :return: wrapper
        """
        def wrapper(*args, **kwargs):
            """Wrapper 関数.

            :param args: 任意の引数
            :param kwargs: 任意のキーワード引数
            :return: メイン関数実行結果
            """
            self = args[0]

            # 保存前のファイル名を取得
            result = Organization.objects.filter(pk=self.pk)
            previous = result[0] if len(result) else None
            super(Organization, self).save()

            # 関数実行
            result = function(*args, **kwargs)

            # 保存前のファイルがあったら削除
            if previous:
                os.remove(MEDIA_ROOT + '/' + previous.image.name)
            return result
        return wrapper

    @delete_previous_file
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Organization, self).save()

    @delete_previous_file
    def delete(self, using=None, keep_parents=False):
        super(Organization, self).delete()

    image_origin = models.ImageField(_('image_origin'), upload_to=get_image_path, blank=True)
    image_thumbnail = ImageSpecField(source='image_origin',
                            processors=[ResizeToFill(250,250)],
                            format="JPEG",
                            options={'quality': 60}
                            )

    image_middle = ImageSpecField(source='image_origin',
                        processors=[ResizeToFill(400, 400)],
                        format="JPEG",
                        options={'quality': 75}
                        )

    def __str__(self):
        return self.name

class ProjectStatusM(models.Model):
    project_status = models.CharField(max_length=4)
    icon_color = models.CharField(max_length=7)

    def __str__(self):
        return self.project_status

class Project(models.Model):
    users = models.ManyToManyField(UserAccount)
    name = models.CharField(max_length=256)
    details = models.TextField(blank=True)
    start_date = models.DateField()
    project_status = models.ForeignKey(ProjectStatusM, on_delete=models.CASCADE)
    homepage = models.URLField(blank=True)
    email = models.EmailField(blank=True)

    def get_image_path(self, filename):
        """カスタマイズした画像パスを取得する.

        :param self: インスタンス (models.Model)
        :param filename: 元ファイル名
        :return: カスタマイズしたファイル名を含む画像パス
        """
        prefix = 'project/'
        name = str(uuid.uuid4()).replace('-', '')
        extension = os.path.splitext(filename)[-1]
        return prefix + name + extension

    def delete_previous_file(function):
        """不要となる古いファイルを削除する為のデコレータ実装.

        :param function: メイン関数
        :return: wrapper
        """
        def wrapper(*args, **kwargs):
            """Wrapper 関数.

            :param args: 任意の引数
            :param kwargs: 任意のキーワード引数
            :return: メイン関数実行結果
            """
            self = args[0]

            # 保存前のファイル名を取得
            result = Project.objects.filter(pk=self.pk)
            previous = result[0] if len(result) else None
            super(Project, self).save()

            # 関数実行
            result = function(*args, **kwargs)

            # 保存前のファイルがあったら削除
            if previous:
                os.remove(MEDIA_ROOT + '/' + previous.image.name)
            return result
        return wrapper

    @delete_previous_file
    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        super(Project, self).save()

    @delete_previous_file
    def delete(self, using=None, keep_parents=False):
        super(Project, self).delete()

    image_origin = models.ImageField(_('image_origin'), upload_to=get_image_path, blank=True)
    image_thumbnail = ImageSpecField(source='image_origin',
                            processors=[ResizeToFill(250,250)],
                            format="JPEG",
                            options={'quality': 60}
                            )

    image_middle = ImageSpecField(source='image_origin',
                        processors=[ResizeToFill(400, 400)],
                        format="JPEG",
                        options={'quality': 75}
                        )

    def __str__(self):
        return self.name

class CategoryM(models.Model):
    name = models.CharField(max_length=256)
    related = models.ManyToManyField("CategoryM", blank=True)

    def __str__(self):
        return self.name
