from django.db import models
from django.core.mail import send_mail
from django.conf import settings
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
    """カスタムユーザーモデル.(Parks共通)"""

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
    """ユーザー情報(JoiRePa用)

    user_account: Parks共通アカとの紐付け
    display_name: 表示用名前
    birthday: 誕生日
    details: ユーザー詳細
    homepage: ホームページ
    title: 肩書き
    image_origin: プロフィール画像　アップロード保存
    image_thumnail,middle: プロフィール画像　表示用
    """
    user_account = models.OneToOneField(UserAccount, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=128, blank=False, default=user_account.name)
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
        """不要となる古いファイルを削除する為のデコレータ実装.(未検証)

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
                file_path = settings.MEDIA_ROOT + '/' + previous.image_origin.name
                if os.path.isfile(file_path):
                    os.remove(file_path)

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
    """所属団体区分マスタ(企業・研究室)"""
    name = models.CharField(max_length=7)

    def __str__(self):
        return self.name

class Organization(models.Model):
    """所属団体

    member: 参加メンバー
    name: 団体名
    organization_div: 所属団体区分
    details: 詳細
    homepage: 団体HPリンク先
    email: 団体連絡先Email
    image_xxx: サムネイル画像
    """
    member = models.ManyToManyField(UserProfile, related_name="organization")
    name = models.CharField(max_length=256)
    organization_div = models.ForeignKey(OrganizationDivM, on_delete=models.PROTECT)
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
        """不要となる古いファイルを削除する為のデコレータ実装.(未検証)

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
                file_path = settings.MEDIA_ROOT + '/' + previous.image_origin.name
                if os.path.isfile(file_path):
                    os.remove(file_path)
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

class OrganizationLight(models.Model):
    """JoiRePaには正式登録してない、一時的な団体名登録用"""
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="organization_light")
    name = models.CharField(max_length=256)
    organization_div = models.ForeignKey(OrganizationDivM, on_delete=models.PROTECT)
    homepage = models.URLField(blank=True)

    def __str__(self):
        return self.name

class ProjectStatusM(models.Model):
    """プロジェクトステータスマスタ(急募、実績etc)
    icon_color: 表示アイコンの背景色(ex:#00ffff)
    """
    project_status = models.CharField(max_length=4)
    icon_color = models.CharField(max_length=7)

    def __str__(self):
        return self.project_status

class Project(models.Model):
    """プロジェクト
    users: 参加メンバー
    name: プロジェクト名
    details: プロジェクト詳細
    start_date: プロジェクト開始日付
    project_status: ステータス
    homepage: プロジェクトHPリンク
    email: Email
    organization(_l): 参加団体
    image_xxx: サムネイル画像
    """
    users = models.ManyToManyField(UserProfile, related_name="project")
    name = models.CharField(max_length=256)
    details = models.TextField(blank=True)
    start_date = models.DateField()
    project_status = models.ForeignKey(ProjectStatusM, on_delete=models.PROTECT)
    homepage = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    organization = models.ManyToManyField(Organization, related_name="organization", blank=True)
    organization_l = models.ManyToManyField(OrganizationLight, related_name="organization_l", blank=True)

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
        """不要となる古いファイルを削除する為のデコレータ実装.(未検証)

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
                file_path = settings.MEDIA_ROOT + '/' + previous.image_origin.name
                if os.path.isfile(file_path):
                    os.remove(file_path)
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

class BulletinBoard(models.Model):
    """掲示板　スレッドの紐付け先"""
    user = models.OneToOneField("UserProfile", null=True, blank=True, on_delete=models.CASCADE, related_name="bulletin_board_u")
    organization = models.OneToOneField("Organization", null=True, blank=True, on_delete=models.CASCADE, related_name="bulletin_board_o")
    project = models.OneToOneField("Project", null=True, blank=True, on_delete=models.CASCADE, related_name="bulletin_board_p")

    def __str__(self):
        name = ""
        if self.user is not None:
            name = self.user.display_name
        elif self.organization is not None:
            name = self.organization.name
        elif self.project is not None:
            name = self.project.name
        else:
            return "N/A"

        if self.id:
            return "掲示板/" + str(self.id) + "/" + name 
        else:
            return "掲示板/" + name 


class BulletinBoardThread(models.Model):
    """掲示板スレッド　コメント紐付け先"""
    parent_board = models.ManyToManyField("BulletinBoard",
                                            blank=True,
                                            related_name="child_thread")
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(default=timezone.now)

class BulletinBoardMessage(models.Model):
    """掲示板コメント"""
    thread = models.ForeignKey("BulletinBoardThread", on_delete=models.CASCADE, related_name="child_message")
    seq_no = models.IntegerField()
    sender = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="send_message")
    message = models.CharField(max_length=500)
    send_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)

