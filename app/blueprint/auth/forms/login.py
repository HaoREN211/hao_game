# 作者：hao.ren3
# 时间：2019/11/11 14:51
# IDE：PyCharm

from app.blueprint.RenderForm import RenderForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from config import TranslateForm

# 登录界面
class LoginForm(RenderForm):
    username = StringField(TranslateForm.Login.Username, validators=[DataRequired()])
    password = PasswordField(TranslateForm.Login.Password, validators=[DataRequired()])
    remember_me = BooleanField(TranslateForm.Login.RememberMe)
    submit = SubmitField(TranslateForm.Login.submit, render_kw={"class":"btn btn-xs btn-success"})
