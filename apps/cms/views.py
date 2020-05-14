# encoding: utf-8

from flask import Blueprint, views, render_template, request, session, redirect, url_for, g, jsonify
from .forms import LoginForm, ResetpwdForm, ResetEmailForm
from .models import CMSUser
from .decorators import login_request
import config
from exts import db, mail
from flask_mail import Message
from utils import restful, zlcache
import string
import random

bp = Blueprint("cms", __name__, url_prefix="/cms")


@bp.route("/")
@login_request
def index():
    # g.cms_user
    return render_template('cms/cms_index.html')


@bp.route("/logout/")
@login_request
def logout():
    del session[config.CMS_USER_ID]
    return redirect(url_for('cms.login'))


@bp.route("/profile/")
@login_request
def profile():
    return render_template("cms/cms_profile.html")


@bp.route("/email_captcha/")
def email_captcha():
    email = request.args.get("email")
    if not email:
        return restful.params_error("没有邮箱 ")

    source = list(string.ascii_letters)
    source.extend(map(lambda x: str(x), range(0, 10)))
    captcha = "".join(random.sample(source, 6))

    message = Message("测试验证码", recipients=["1438008260@qq.com"], body="验证码是%s" % captcha)
    print("发送之前")
    try:
        mail.send(message)
        print("邮箱验证码%s" % captcha)
    except:
        return restful.server_error()
    zlcache.set(email, captcha)
    return restful.success()


@bp.route('/posts/')
def posts():
    return render_template('cms/cms_posts.html')


@bp.route('/comments/')
def comments():
    return render_template('cms/cms_comments.html')


@bp.route('/boards/')
def boards():
    return render_template('cms/cms_boards.html')


@bp.route('/fusers/')
def fusers():
    return render_template('cms/cms_fusers.html')


@bp.route('/cusers/')
def cusers():
    render_template('cms/cms_cusers.html')


@bp.route('/croles/')
def croles():
    render_template("cms/cms_croles.html")


class LoginView(views.MethodView):

    def get(self, message=None):
        return render_template("cms/cms_login.html", message=message)

    def post(self):
        form = LoginForm(request.form)
        if form.validate():
            email = form.email.data
            password = form.password.data
            remember = form.remember.data
            user = CMSUser.query.filter_by(email=email).first()
            if user and user.check_password(password):
                session[config.CMS_USER_ID] = user.id
                if remember:
                    session.permanent = True
                return redirect(url_for("cms.index"))
            else:
                return self.get(message="邮箱或密码错误")
        else:
            message = form.get_error()
            return self.get(message=message)


class ResetPwdView(views.MethodView):
    decorator = [login_request]

    def get(self):
        return render_template('cms/cms_resetpwd.html')

    def post(self):
        form = ResetpwdForm(request.form)
        if form.validate():
            oldpwd = form.oldpwd.data
            newpwd = form.newpwd.data
            user = g.cms_user
            if user.check_password(oldpwd):
                user.password = newpwd
                db.session.commit()
                return restful.success()
            else:
                return restful.params_error("旧密码错误")
        else:
            return restful.params_error(form.get_error())


class ResetEmailView(views.MethodView):
    decorator = [login_request]

    def get(self):
        return render_template("cms/cms_resetemail.html")

    def post(self):
        form = ResetEmailForm(request.form)
        if form.validate():
            email = form.email.data
            g.cms_user.email = email
            db.session.commit()
            return restful.success()
        else:
            return restful.params_error(form.get_error())


bp.add_url_rule("/login/", view_func=LoginView.as_view("login"))
bp.add_url_rule("/resetpwd/", view_func=ResetPwdView.as_view("resetpwd"))
bp.add_url_rule('/resetemail/', view_func=ResetEmailView.as_view("resetemail"))
