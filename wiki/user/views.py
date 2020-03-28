import re
import jwt
import time
import json
import hashlib
import datetime
from tools.configs import CODE_TOKEN_KEY
from .models import UserProfile
from .tasks import send_sms_code
from django.shortcuts import render
from wtoken.views import make_token
from django.http import JsonResponse, HttpResponse
from tools.logging_check import logging_check
from celery.result import AsyncResult


# Create your views here.

@logging_check('PUT')
def users(request, username=None):
    if request.method == "GET":
        # 拿数据
        if username:
            # 拿具体用户数据
            users = UserProfile.objects.filter(username=username)
            user = users[0]
            if user:
                if request.GET.keys():
                    # 取字段数据
                    data = {}
                    for key in request.GET.keys():
                        # 过滤字段
                        if key == "password":
                            continue
                        if hasattr(user, key):
                            value = getattr(user, key)
                            data[key] = value
                    result = {"code": 200, "data": data}
                else:
                    data = {}
                    data["nickname"] = user.nickname
                    data["username"] = user.username
                    data["sign"] = user.sign
                    data["info"] = user.info
                    data["avatar"] = str(user.avatar)  # 第四步
                    result = {"code": 200, "data": data}
            else:
                result = {"code": 101, "error": "user is None"}
        else:
            # 拿所有用户数据
            all_users = UserProfile.objects.all()
            users_data = []
            print(all_users)
            for user in all_users:
                dic = {}
                dic['nickname'] = user.nickname
                dic['username'] = user.username
                dic['sign'] = user.sign
                dic['info'] = user.info
                users_data.append(dic)
            result = {"code": 200, "data": users_data}
            return JsonResponse(result)
        return JsonResponse(result)
    elif request.method == "POST":
        # 创建用户
        json_str = request.body
        if not json_str:
            result = {"code": 10101, "error": "please give me some datas!!"}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        username = json_obj.get("username")
        if not username:
            result = {'code': 10102, 'error': 'Please give me username~'}
            return JsonResponse(result)
        users = UserProfile.objects.filter(username=username)
        if users:
            result = {"code": 10103, "error": "The username already exists!"}
            return JsonResponse(result)

        # 获取手机号码
        phone = json_obj.get("phone")
        if not phone:
            result = {"code": 10104, "error": "Phone number cannot be empty!!"}
            return JsonResponse(result)
        # 验证手机号是否正确
        phone_re = re.compile('^1[3-9]\d{9}$')
        res = re.search(phone_re, phone)

        if not res:  # 不正确
            result = {"code": 10104, "error": "The phone number is error!!"}
            return JsonResponse(result)
        password_1 = json_obj.get("password_1")
        password_2 = json_obj.get("password_2")
        if password_1 == "" or password_2 == "":
            result = {"code": 10105, "error": "Password cannot be empty!!!"}
            return JsonResponse(result)
        if password_1 != password_2:
            result = {"code": 10106, "error": "Two passwords do not match!!"}
            return JsonResponse(result)

        ver_code = json_obj.get("ver_code")
        code_token = json_obj.get("code_token")
        if not ver_code:
            result = {"code": 10107, "error": "Verify code cannot be empty!"}
            return JsonResponse(result)
        if not code_token:
            result = {"code": 10108, "error": "Vertifying failed_01!"}
            return JsonResponse(result)
        try:
            json_obj = jwt.decode(code_token, key=CODE_TOKEN_KEY, algorithms="HS256")
        except Exception as e:
            result = {"code": 10109, "error": e}
            return JsonResponse(result)
        code_expired_time = json_obj.get("exp")
        if not code_expired_time:
            result = {"code": 10108, "error": "Vertifying failed_02!"}
            return JsonResponse(result)
        if time.time() > code_expired_time:
            result = {"code": 10108, "error": "Vertifying is overtime!"}
            return JsonResponse(result)
        code = json_obj.get("code")
        if not code:
            result = {"code":10108,"error":"Vertifying failed_03!"}
            return JsonResponse(result)
        if code != ver_code:
            result = {"code":10109,"error":"Vertifying failed_04!"}
            return JsonResponse(result)


        # 生成散列密码
        pm = hashlib.md5()
        pm.update(password_1.encode())  # 将字符串转为字节串

        # 创建用户
        try:
            UserProfile.objects.create(username=username, phone=phone, password=pm.hexdigest(),
                                       nickname=username)
        except Exception as e:
            print("----create error----")
            print(e)
            result = {"code": 10107, "error": "The username already exists!!!"}
            return JsonResponse(result)

        # 生成Token
        now_datetime = datetime.datetime.now()
        token = make_token(username, 3600 * 24, now_datetime)
        result = {"code": 200, "data": {"token": token.decode()}, 'username': username}
        return JsonResponse(result)
    elif request.method == "PUT":
        # 更新 http://127.0.0.1:8000/v1/users/username
        if username:
            user = request.user
            if user:
                if username != user.username:
                    result = {"code": 10109, 'error': 'The username is error!!'}
                else:
                    json_str = request.body
                    json_obj = json.loads(json_str)
                    nickname = json_obj.get('nickname')
                    sign = json_obj.get('sign')
                    info = json_obj.get('info')
                    # 更新
                    to_update = False
                    if user.nickname != nickname:
                        to_update = True
                    if user.info != info:
                        to_update = True
                    if user.sign != sign:
                        to_update = True
                    if to_update:
                        user.sign = sign
                        user.nickname = nickname
                        user.info = info
                        user.save()
                    result = {"code": 200, "username": username}
            else:
                result = {"code": 10110, "error": "The user not exists!!"}
        else:
            result = {"code": 10108, 'error': 'Must be give me username!!'}
        return JsonResponse(result)


@logging_check("POST")
def user_avatars(request, username):
    # 处理头像上传
    if request.method != "POST":
        result = {"code": 10110, 'error': "Please use POST"}
        return JsonResponse(result)
    user = request.user
    if user.username != username:  # 左边是token里的,右边是路由里的
        result = {"code": 10109, "error": "The username is error!"}
        return JsonResponse(result)
    user.avatar = request.FILES["avatar"]  # 真正的存取图片
    user.save()
    return JsonResponse({'code': 200, 'username': username})


def send_sms_codes(request):
    if request.method == "POST":
        json_str = request.body
        json_obj = json.loads(json_str)
        phone = json_obj.get("phone")
        if not phone:
            result = {"code": 10103, "error": "please enter a phone number"}
            return JsonResponse(result)
        # 验证手机号是否正确
        phone_re = re.compile('^1[3-9]\d{9}$')
        res = re.search(phone_re, phone)

        if not res:  # 不正确
            result = {"code": 10104, "error": "The phone number is error!!"}
            return JsonResponse(result)

        # delay 返回的是一个 AsyncResult 对象，里面存的就是一个异步的结果，
        # 当任务完成时result.ready() 为 true，然后用 result.get() 取结果即可。
        result = send_sms_code.delay(mobile=phone)  # 手机号,验证码
        print("apply_async的result:", result)
        count = 0  # 定时
        while not result.ready():
            time.sleep(0.1)
            count += 1
            if count == 10:
                break

        if result.ready():
            print("result.get的type", type(result.get()))
            print("result的结果", result.result)
            print("result的结果", result.get())
            return JsonResponse(result.get())  # result.get()是发送短信返回的结果
        else:
            return JsonResponse({"code": 10102, "error": "发送失败01"})
