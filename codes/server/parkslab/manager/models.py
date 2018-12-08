from django.db import models

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




    