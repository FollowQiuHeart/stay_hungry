# -*- encoding: utf-8 -*-
"""
@File    : urls.py
@Time    : 3/18/20 9:34 PM
@Author  : qiuyucheng
@Software: PyCharm
"""
from django.conf.urls import url
from . import views
urlpatterns = [
    #http://127.0.0.1:8000/v1/users
    url(r"^$",views.users),
    # http://127.0.0.1:8000/v1/users/<username>
    #(?P<username>\w+)是将后面匹配的\w+数据,取一个组名，这个组名必须是唯一的,不重复的,没有特殊符号
    url(r"^/(?P<username>\w{1,11})$",views.users),
    # http://127.0.0.1:8000/v1/users/<username>/avatar
    url(r"^/(?P<username>\w{1,11})/avatar$",views.user_avatars),
    url(r"^/send_sms_codes$",views.send_sms_codes),
]


