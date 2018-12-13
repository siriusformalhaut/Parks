from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from manager.managers import PersonManager

# Create your models here.
class Account(models.Model):
    MAN = 0
    WOMAN = 1

    COMPANY = 5
    RESERCHER = 10
    GENERAL = 15

    #名前
    name = models.CharField(max_length = 128)
    #アカウント名(本名明かしたくない人向け(一般のアカウントには需要ありそうなので追加)TODO 任意項目にする)
    accountname = models.CharField(max_length = 128)
    #誕生日(仮置き。アカウント認証情報とかに使うかも。使わないかも。)
    birthday = models.DateField()
    #性別
    sex = models.IntegerField()
    #メールアドレス
    email = models.EmailField()
    #パスワード TODO 何文字制限か決める
    password = models.CharField(max_length = 128)
    #所属機関
    institution = models.CharField(max_length = 128)

    #TODO 投げ銭した先の機関名を持たせたい。別テーブルでアカウント情報を紐づけて持たせる。


#ログイン機能実装の際に追記。今後要編集。
class Person(AbstractBaseUser):
    objects = PersonManager()

    identifier = models.CharField(max_length=64, unique=True, blank=False)
    name = models.CharField(max_length = 128)
    email = models.EmailField()

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'identifier'