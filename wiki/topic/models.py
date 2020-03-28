from django.db import models
from user.models import UserProfile
# Create your models here.
class Topic(models.Model):
    title = models.CharField(max_length=50,verbose_name="博客主题")
    #tec技术类文章 or no-tec非技术类文章
    category = models.CharField(max_length=20,verbose_name="博客分类")
    #public 公开博客 or private 私有博客
    limit = models.CharField(max_length=10,verbose_name="博客权限")
    introduce = models.CharField(max_length=90,verbose_name="博客简介")
    content = models.TextField(verbose_name="博客内容")
    created_time = models.DateTimeField(verbose_name="博客创建时间",auto_now_add=True)
    updated_time = models.DateTimeField(verbose_name="博客更新时间",auto_now=True)
    author = models.ForeignKey(UserProfile)  #多对一

    class Meta:
        db_table = 'topic'

