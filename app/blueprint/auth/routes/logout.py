# 作者：hao.ren3
# 时间：2019/11/11 16:03
# IDE：PyCharm

from app.blueprint.auth import bp
from flask_login import logout_user
from flask import redirect, url_for

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))