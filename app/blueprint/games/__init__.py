# -*- coding: UTF-8 -*- 
# 作者：hao.ren3
# 时间：2020/1/29 22:13
# IDE：PyCharm

from flask import Blueprint

bp = Blueprint('game', __name__)

from app.blueprint.games.red3.routes import client