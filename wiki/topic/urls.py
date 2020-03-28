# -*- encoding: utf-8 -*-
"""
@File    : urls.py
@Time    : 3/20/20 10:21 AM
@Author  : qiuyucheng
@Software: PyCharm
"""
from django.conf.urls import url
from . import views
urlpatterns = [
    url(r"^/(?P<author_name>\w{1,11})$",views.topics)
]