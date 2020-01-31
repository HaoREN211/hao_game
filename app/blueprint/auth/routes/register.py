# 作者：hao.ren3
# 时间：2019/11/11 16:04
# IDE：PyCharm

from app import db
from app.blueprint.auth import bp
from flask_login import current_user, login_user
from flask import render_template, flash, redirect, url_for
from app.models.User import User
from app.blueprint.auth.forms.registration import RegistrationForm


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if not (current_user.is_authenticated and current_user.is_admin):
        flash("您不是超级管理员，无法创建新用户")
        if current_user.is_authendicated:
            return redirect(url_for('game.red3'))
        return redirect(url_for("auth.login"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('创建成功')
        if not (current_user.is_authenticated and current_user.is_admin):
            login_user(user, remember=True)
        return redirect(url_for('game.red3'))
    return render_template('auth/register.html', title='Register', form=form)
