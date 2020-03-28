# -*- encoding: utf-8 -*-
"""
@File    : urls.py
@Time    : 3/19/20 1:54 PM
@Author  : qiuyucheng
@Software: PyCharm
"""

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$",views.tokens)
]