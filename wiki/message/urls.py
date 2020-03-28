# -*- encoding: utf-8 -*-
"""
@File    : urls.py
@Time    : 3/21/20 10:14 AM
@Author  : qiuyucheng
@Software: PyCharm
"""
from django.conf.urls import url
from . import views
urlpatterns = [
    url("^/(?P<topic_id>\d+)$",views.messages)
]
