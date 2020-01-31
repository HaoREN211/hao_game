# -*- coding: UTF-8 -*-
# 作者：hao.ren3
# 时间：2019/12/21 8:04
# IDE：PyCharm

import os
from config_db import ConfigDb
from numpy import array


class Config(object):
    # 分页功能，每页显示的个数
    POSTS_PER_PAGE = 10

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-hao-guess'
    DIALECT = 'mysql'
    DRIVER = 'pymysql'
    USERNAME = ConfigDb.USERNAME
    PASSWORD = ConfigDb.PASSWORD
    HOST = ConfigDb.HOST
    PORT = ConfigDb.PORT
    DATABASE = ConfigDb.DATABASE
    SQLALCHEMY_DATABASE_URI = '{}+{}://{}:{}@{}:{}/{}?charset=utf8'.format(
        DIALECT, DRIVER, USERNAME, PASSWORD, HOST, PORT, DATABASE
    )
    # 设置是否在每次连接结束后自动提交数据库中的变动。
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # Flask-SQLAlchemy 将会追踪对象的修改并且发送信号。这需要额外的内存，如果不必要的可以禁用它。
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 数据库连接池的大小。默认是引擎默认值（通常 是 5 ）
    SQLALCHEMY_POOL_SIZE = 10

    # 控制在连接池达到最大值后可以创建的连接数。当这些额外的连接使用后回收到连接池后将会被断开和抛弃。
    # 保证连接池只有设置的大小；
    SQLALCHEMY_MAX_OVERFLOW = 5

    # 设定连接池的连接超时时间。默认是 10 。
    SQLALCHEMY_POOL_TIMEOUT = 10

    # 设置多少秒后回收连接，在使用 MySQL 时是必须设置的。
    SQLALCHEMY_POOL_RECYCLE = 30

    BOOTSTRAP_SERVE_LOCAL = True

class TranslateForm(object):
    class Login(object):
        Username = "账号"
        Password = "密码"
        PageTitle = "请登录"
        RememberMe = "请记住我"
        submit = "登录"
        register = "注册"

    class TranslatePage(object):
        Home = "主页"
        Login = "登录"

    class ChineseLanguage:
        class Profile:
            edit_profile = "修改资料"
            saved = "资料修改成功"
            profile = "用户资料"

class Poker(object):
    cards = [('红桃', 'A', 41), ('红桃', '2', 45), ('红桃', '3', 49), ('红桃', '4', 1), ('红桃', '5', 5), ('红桃', '6', 9),
             ('红桃', '7', 13), ('红桃', '8', 17),
             ('红桃', '9', 21), ('红桃', '10', 25), ('红桃', 'J', 29), ('红桃', 'Q', 33), ('红桃', 'K', 37), ('方块', 'A', 42),
             ('方块', '2', 46), ('方块', '3', 50),
             ('方块', '4', 2), ('方块', '5', 6), ('方块', '6', 10), ('方块', '7', 14), ('方块', '8', 18), ('方块', '9', 22),
             ('方块', '10', 26), ('方块', 'J', 30),
             ('方块', 'Q', 34), ('方块', 'K', 38), ('黑桃', 'A', 43), ('黑桃', '2', 47), ('黑桃', '3', 51), ('黑桃', '4', 3),
             ('黑桃', '5', 7), ('黑桃', '6', 11),
             ('黑桃', '7', 15), ('黑桃', '8', 19), ('黑桃', '9', 23), ('黑桃', '10', 27), ('黑桃', 'J', 31), ('黑桃', 'Q', 35),
             ('黑桃', 'K', 39), ('梅花', 'A', 44),
             ('梅花', '2', 48), ('梅花', '3', 52), ('梅花', '4', 4), ('梅花', '5', 8), ('梅花', '6', 12), ('梅花', '7', 16),
             ('梅花', '8', 20), ('梅花', '9', 24),
             ('梅花', '10', 28), ('梅花', 'J', 32), ('梅花', 'Q', 36), ('梅花', 'K', 40)]
