import datetime
import hashlib
import time
import jwt
import json
from tools.configs import CODE_TOKEN_KEY
from django.shortcuts import render
from django.http import JsonResponse
# Create your views heere.
from user.models import UserProfile


def tokens(request):
    if request.method != "POST":
        result = {"code": "20101", "erorr": 'Please use POST'}
        return result
    json_str = request.body
    json_obj = json.loads(json_str)
    login_mode = json_obj.get("login_mode")
    user_t = None
    print("json_obj:", json_obj)
    if login_mode == "sms_login":
        phone = json_obj.get("phone")
        user = UserProfile.objects.get(phone=phone)
        if not user:
            result = {"code": 10103, "error": "The user not existed!"}
            return JsonResponse(result)
        ver_code = json_obj.get("ver_code")
        if not ver_code:
            result = {"code":10108,"error":"Vertify code cannot be empty!!"}
            return JsonResponse(result)
        code_token = json_obj.get("code_token")
        if not code_token:
            result = {"code": 10102, "error": "Vertifying failed!"}
            return JsonResponse(result)
        try:
            json_obj = jwt.decode(code_token, key=CODE_TOKEN_KEY, algorithms="HS256")
        except Exception as e:
            result = {"code": 10102, "error": "Vertifying failed!"}
            return JsonResponse(result)
        code_expired_time = json_obj.get("exp")
        if not code_expired_time:
            result = {"code": 10108, "error": "Vertifying failed!!"}
            return JsonResponse(result)
        if time.time() > code_expired_time:
            result = {"code": 10102, "error": "Vertifying is overtime!!"}
            return JsonResponse(result)
        if ver_code != json_obj["code"]:
            result = {"code": 10109, "error": "Vertifying failed!"}
            return JsonResponse(result)
        user_t = user
    elif login_mode == "uname_login":
        username = json_obj.get("username")
        password = json_obj.get("password")
        print(password)
        # 找用户
        users = UserProfile.objects.filter(username=username)
        if not users:
            result = {"code": 20102, "error": "The username or password is error!!"}
            return JsonResponse(result)
        user = users[0]
        pm = hashlib.md5()
        pm.update(password.encode())  # update需要的是字节串,不是字符串
        if user.password != pm.hexdigest():
            result = {"code": 20103, "error": "The username or password is error!!"}
            return JsonResponse(result)
        user_t = user

    # 生成token
    now_d = datetime.datetime.now()
    user_t.login_time = now_d
    user_t.save()  # 数据保存更新
    token = make_token(user_t.username, 3600 * 24, now_d)
    result = {"code": 200, "username": user_t.username, "data": {"token": token.decode()}}

    return JsonResponse(result)


# 生成token
def make_token(username, exp, now_datetime):
    key = '1234567ab'
    now_t = time.time()
    payload = {"username": username, "login_time": str(now_datetime), "exp": int(now_t + exp)}
    return jwt.encode(payload, key, algorithm="HS256")
