# 作者：hao.ren3
# 时间：2019/11/11 14:53
# IDE：PyCharm

from app.blueprint.auth import bp
from app.blueprint.auth.forms.login import LoginForm
from flask_login import current_user, login_user
from config import TranslateForm
from flask import redirect, url_for, flash, render_template, request
from app.models.User import User
from werkzeug.urls import url_parse


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('game.red3'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)

        # 原始URL设置了next查询字符串参数后，应用就可以在登录后使用它来重定向。
        # 装饰器将拦截请求并以重定向到*/login来响应，
        # 但是它会添加一个查询字符串参数来丰富这个URL，如/login?next=/index*。
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('game.red3')
        return redirect(next_page)
    return render_template("auth/login.html", login_title='登录', form=form,
                           home=TranslateForm.TranslatePage.Home,
                           login=TranslateForm.TranslatePage.Login)

