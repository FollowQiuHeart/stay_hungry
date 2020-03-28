from django.db import models
from topic.models import Topic
from user.models import UserProfile
# Create your models here.
class Message(models.Model):
    content = models.CharField(max_length=50,verbose_name="留言内容")
    created_time = models.DateTimeField(verbose_name="创建时间",auto_now_add=True)
    parent_message = models.IntegerField(default=0,verbose_name="关联的留言ID")
    publisher = models.ForeignKey(UserProfile)
    topic = models.ForeignKey(Topic)

    class Meta:
        db_table = "message"
