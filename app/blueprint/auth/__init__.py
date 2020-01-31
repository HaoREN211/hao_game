# 作者：hao.ren3
# 时间：2019/11/11 14:50
# IDE：PyCharm

from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.blueprint.auth.routes import login, logout, register
