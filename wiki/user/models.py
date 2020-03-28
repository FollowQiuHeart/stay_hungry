import random

from django.db import models

# Create your models here.

def default_sign():
    signs = ['地表最强','和平主义','我爱我家']
    return random.choice(signs)

#创建数据表
class UserProfile(models.Model):
    username = models.CharField(max_length=11,verbose_name="用户名",primary_key=True)
    nickname = models.CharField(max_length=30,verbose_name="昵称")
    phone = models.EmailField(verbose_name="手机号")
    # email = models.EmailField(verbose_name="邮箱")
    password = models.CharField(max_length=32,verbose_name="密码") #32位,md5
    sign = models.CharField(max_length=50,verbose_name="个人签名",default=default_sign)
    info = models.CharField(max_length=150,verbose_name="个人描述",default="")
    created_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name="更新时间",auto_now=True)
    #upload_to 指定存储路径 MEDIA_ROOT + upload_to的值
    avatar = models.ImageField(upload_to='avatar',default="",verbose_name="头像")
    login_time = models.DateTimeField(verbose_name="登录时间",null=True)
    class Meta:
        db_table = "user_profile"