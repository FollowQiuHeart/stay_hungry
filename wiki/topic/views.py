import json
from user.models import UserProfile
from django.shortcuts import render
from tools.logging_check import logging_check, get_user_by_request
from .models import Topic
from django.http import JsonResponse
from message.models import  Message

# Create your views here.
@logging_check("POST", "DELETE")
def topics(request, author_name=None):
    if request.method == "GET":
        # 获取用户文章数据
        # /v1/topics/qiu - qiu的所有文章
        # /v1/topics/qiu?category=tec|no-tec 查询具体种类
        # /v1/topics/qiu?t_id=33 #查询具体文章
        # 1,访问当前博客的访问者 visitor
        # 2,当前被访问的博客的博主 author
        authors = UserProfile.objects.filter(username=author_name)
        if not authors:
            result = {"code": 30104, 'error': "The author is not existed!!"}
            return JsonResponse(result)
        author = authors[0]

        # 访问者
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username

        # 判断t_id
        t_id = request.GET.get("t_id", "")
        if t_id:
            # 获取指定t_id的详情页
            t_id = int(t_id)
            if author_name == visitor_username:
                # 博主本人访问自己的博客
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id)
                except Exception as e:
                    print("--get t_id error--")
                    print(e)
                    result = {"code": 30108, "error": "No topic"}
                    return JsonResponse(result)
            else:
                # 非博主访问当前博客
                # id是主键,唯一
                is_self = False
                try:
                    author_topic = Topic.objects.get(id=t_id, limit="public")
                except Exception as e:
                    result = {"code": 200, "error": "No topic visitor!!"}
                    return JsonResponse(result)
            # 生成具体返回值
            result = make_topic_res(author, author_topic, is_self)
            return JsonResponse(result)
        else:
            # 列表页的需求
            # 判断文章类型
            category = request.GET.get("category", "")
            if category in ["tec", "no-tec"]:
                if author_name == visitor_username:
                    # 博主访问自己的博客
                    author_topics = Topic.objects.filter(
                        author_id=author_name, category=category)
                else:
                    author_topics = Topic.objects.filter(
                        category=category, author_id=author_name, limit="public")
            else:
                if author_name == visitor_username:
                    # 博主访问自己的博客
                    author_topics = Topic.objects.filter(
                        author_id=author_name)
                else:
                    author_topics = Topic.objects.filter(
                        author_id=author_name, limit="public")
            res = make_topics_res(author, author_topics)
            return JsonResponse(res)

    if request.method == "POST":
        # 发表博客
        author = request.user
        if author.username != author_name:
            result = {"code": 10102, "error": "The username is error!!"}
            return JsonResponse(result)
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj.get("title")
        # 注意XSS攻击,将用户输入进行转义
        import html
        title = html.escape(title)
        category = json_obj.get("category")
        if category not in ['tec', "no-tec"]:
            result = {"code": 30102, "error": 'Thanks,your category is error!!'}
            return JsonResponse(result)
        limit = json_obj.get("limit")
        if limit not in ['private', 'public']:
            result = {"code": 30103, "error": "Thanks,your limit is error!!"}
            return JsonResponse(result)
        # 带样式的文章内容
        content = json_obj.get("content")
        # 纯文本的文章内容 - 用于做文章简介的切片
        content_txt = json_obj.get("content_text")
        introduce = content_txt[:30]
        # 创建topic
        Topic.objects.create(title=title, category=category, limit=limit,
                             content=content, introduce=introduce, author=author)
        result = {"code": 200, "username": author.username}
        return JsonResponse(result)

    if request.method == "DELETE":
        # 删除博客文章,真删除
        # 请求中携带查询字符串 ?topic_id=3
        # 响应 {"code":200}
        user = request.user
        if user.username != author_name:
            # 查询token中的用户名和前端访问url中的用户名是否一致
            result = {"code": 10103, "error": "The user is error!!"}
            return JsonResponse(result)
        topic_id = request.GET.get("topic_id")
        if not topic_id:
            result = {"code": 30106, "error": "Must be give me a topic_id!"}
        topic_id = int(topic_id)  # id为主键,为int类型

        # 获取具体要删除的文章
        try:
            topic = Topic.objects.get(id=topic_id, author_id=author_name)
        except Exception as e:
            print("--topic--delete--error--")
            print(e)
            result = {"code": 30107, "error": "The topic not exists!"}
            return JsonResponse(result)

        # 文章删除
        topic.delete()
        return JsonResponse({"code": 200})


def make_topic_res(author, author_topic, is_self):
    # 获取上一篇文章的id和title
    # 获取下一篇文章的id和title
    if is_self:
        # 查找下一篇文章SQL版本
        # select * from topic where id > 3 and author_id=qiu order by id ASC limit 1
        # 查找下一篇文章Django版本
        # Topic.objects.filter(id_gt=3,author_id="qiu").first() 自带排序
        # 执行first()的时候,默认执行： order by id ASC limit 1
        # 查找上一篇文章SQL版本
        # select * from topic where id < 3 and author_id=qiu order by id DESC limit 1
        # 查找下一篇文章Django版本
        # Topic.objects.filter(id_lt=3,author_id="qiu").last() 自带排序
        # 执行last()的时候,默认执行： order by id DESC limit 1
        next_topic = Topic.objects.filter(
            id__gt=author_topic.id, author=author).first()
        last_topic = Topic.objects.filter(
            id__lt=author_topic.id, author=author).last()
        if next_topic:
            next_id = next_topic.id
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None
    else:
        next_topic = Topic.objects.filter(
            id__gt=author_topic.id, author=author, limit="public").first()
        last_topic = Topic.objects.filter(
            id__lt=author_topic.id, author=author, limit="public").last()
        if next_topic:
            next_id = next_topic.id
            next_title = next_topic.title
        else:
            next_id = None
            next_title = None
        if last_topic:
            last_id = last_topic.id
            last_title = last_topic.title
        else:
            last_id = None
            last_title = None
    result = {"code": 200, "data": {}}
    result["data"]["title"] = author_topic.title
    result["data"]["nickname"] = author.nickname
    result["data"]["category"] = author_topic.category
    result["data"]["created_time"] = \
        author_topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
    result["data"]["content"] = author_topic.content
    result["data"]["introduce"] = author_topic.introduce
    result["data"]["author"] = author.nickname
    result["data"]["next_id"] = next_id
    result["data"]["next_title"] = next_title
    result["data"]["last_id"] = last_id
    result["data"]["last_title"] = last_title
    # 留言
    all_messages = Message.objects.filter(topic=author_topic).order_by("-created_time")
    #留言+回复条数
    msg_count = 0
    #留言专属容器
    msg_list = []
    #回复专属容器
    reply_home = {}
    if all_messages:
        for message in all_messages:
            msg_count +=1
            if message.parent_message:
                #回复
                reply_home.setdefault(message.parent_message,[])
                reply_home[message.parent_message].append(
                    {"msg_id":message.id,"content":message.content,
                     "publisher":message.publisher.nickname,
                     "publisher_avatar":str(message.publisher.avatar),
                     "created_time":message.created_time.strftime("%Y-%m-%d %H:%M:%S")})
            else:
                #留言
                msg = {}
                msg["id"] = message.id
                msg["content"] = message.content
                msg["publisher"] = message.publisher.nickname
                msg["publisher_avatar"] = str(message.publisher.avatar)
                msg["reply"] = []
                msg["created_time"] = message.created_time.strftime("%Y-%m-%d %H:%M:%S")
                msg_list.append(msg)

        #关联 留言和回复
        for m in msg_list:
            if m["id"] in reply_home:
                m["reply"] = reply_home[m["id"]]

        result["data"]["messages"] = msg_list
        result["data"]["messages_count"] = msg_count
    else:
        result["data"]["messages"] = []
        result["data"]["messages_count"] = 0

    return result


def make_topics_res(author, author_topics):
    # 生成文章列表返回值
    res = {"code": 200, 'data': {}}
    res["data"]["nickname"] = author.nickname
    res["data"]["topics"] = []
    for topic in author_topics:
        d = {}
        d["id"] = topic.id
        d["title"] = topic.title
        d["introduce"] = topic.introduce
        d["category"] = topic.category
        # str:字符串 f:格式
        d["created_time"] = \
            topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        d["author"] = author.nickname
        res['data']["topics"].append(d)
    return res
