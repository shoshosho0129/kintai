from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin #追加
from letswork.models import Paid
# Create your models here.



class AccountAManager(BaseUserManager):
    def create_user(self, a_no, password=None, **extra_fields):
        """
        通常のユーザーを作成し、返す。
        """
        if not a_no:
            raise ValueError('a_no フィールドは必須です。')
        user = self.model(a_no=a_no, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, a_no, password=None, **extra_fields):
        """
        スーパーユーザーを作成し、返す。
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('スーパーユーザーは is_staff=True である必要があります。')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('スーパーユーザーは is_superuser=True である必要があります。')

        return self.create_user(a_no, password, **extra_fields)

# 従業員アカウント
class Account_e(models.Model):
    class Meta:
        db_table = 'account_e'
    e_id = models.AutoField(verbose_name='従業員id', primary_key=True)
    e_first1 = models.CharField(verbose_name='姓', max_length=50)
    e_last1 = models.CharField(verbose_name='名', max_length=50)
    e_first2 = models.CharField(verbose_name='セイ', max_length=50)
    e_last2 = models.CharField(verbose_name='メイ', max_length=50)
    hour = models.IntegerField(verbose_name='時給')
    
    def __str__(self):
        return f"{self.e_id}"
    
# 管理者アカウント
class Account_a(models.Model):
    class Meta:
        db_table = 'account_a'
    a_no = models.IntegerField(verbose_name='No.', primary_key=True)
    a_first = models.CharField(verbose_name='姓', max_length=50)
    a_last = models.CharField(verbose_name='名', max_length=50)
    a_pass = models.CharField(verbose_name='管理者パスワード', max_length=128)
    is_active = models.BooleanField(default=True) #追加
    is_staff = models.BooleanField(default=False)  # 追加
    is_superuser = models.BooleanField(default=False) #追加

    objects = AccountAManager()
    
    USERNAME_FIELD = 'a_no'
    def __str__(self):
        return f"{self.a_first} {self.a_last}"
    
    def set_password(self, raw_password):
        self.a_pass = make_password(raw_password)
        self.save()
        
    def check_password(self, raw_password):
        return check_password(raw_password, self.a_pass)
    
    def has_perm(self, perm, obj=None):
        """ユーザーが特定の権限を持つかを確認"""
        return True  # 全ての権限を許可する場合はTrueを返す

    def has_module_perms(self, app_label):
        """ユーザーがアプリケーションの権限を持つかを確認"""
        return True  # 全てのアプリにアクセスを許可する
    
    def get_username(self):
        return str(self.a_no)
