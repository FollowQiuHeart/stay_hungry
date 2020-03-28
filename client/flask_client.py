# -*- coding:utf-8 -*-

from flask import Flask, send_file,url_for,render_template,redirect

#创建flask应用对象，
#__name__当前模块名称flask_client(被别人导入时)
#模块名称，flask以这个模块flask_client所在的目录为总目录,默认这个目录中的static为静态目录，
# templates为模板目录
app = Flask(__name__,
            static_url_path="/static", #访问静态资源的url前缀,默认值是static
            static_folder="static", #静态文件的目录，默认是static
            template_folder="templates", #模板文件目录,默认是templates
            )

#装饰器为url,下面函数是视图函数
#通过method建立访问方式
@app.route('/index')
def index():
    #首页
    return send_file('templates/index.html')

@app.route('/login')
def login():
    #登录
    return send_file('templates/login.html')

@app.route('/sms_login')
def sms_login():
    #短信登录
    return send_file('templates/sms_login.html')

@app.route('/register')
def register():
    #注册
    return send_file('templates/register.html')

@app.route('/<username>/info') #<path:username>,不加转换器(path:)类型,默认是普通字符串规则(除了/字符)
def info(username):
    #个人信息
    return send_file('templates/about.html')

@app.route('/photo')
def photo():
    #个人信息
    #使用url_for函数，通过视图函数的名称可以反推找到视图对应的url路径
    url = url_for("index")
    # return render_template('photo.html')
    return redirect(url)

@app.route('/<username>/change_info')
def change_info(username):
    #修改个人信息
    return send_file('templates/change_info.html')

@app.route('/<username>/topic/release')
def topic_release(username):
    #发表博客
    return send_file('templates/release.html')


@app.route('/<username>/topics')
def topics(username):
    #个人博客列表
    return send_file('templates/list.html')

@app.route('/<username>/topics/detail/<t_id>')
def topics_detail(username, t_id):
    #博客内容详情
    return send_file('templates/detail.html')


if __name__ == '__main__':
    #通过url_map可以查看整个flask的路由信息
    print(app.url_map)
    app.run(debug=True)
    # app.run(
    #     host="127.0.0.1", #host="0.0.0.0"
    #     port=5000,
    #     debug=True)

