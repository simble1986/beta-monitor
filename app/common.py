# !/usr/bin/env python
# encoding: utf-8
#
# Author: bqi
#

from flask import Flask
from flask_moment import Moment
from flask_login import LoginManager, current_user
from flask import url_for
from db.db import *

UPLOAD_FOLDER = 'static/uploads'

app = Flask(__name__)
moment = Moment(app)
app.config['SECRET_KEY'] = '123456'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# app.config['DUBUG'] = True

login_manager = LoginManager(app)
login_manager.session_protection = 'basic'
login_manager.login_view = '/'

DEFAULT_ANONYMOUS_USER = "beta"
DEFAULT_ANONYMOUS_USERID = 0

userGroup = {1: ["btn btn-outline-success", "Admin"],
             2: ["btn btn-outline-dark", "User"]}


@login_manager.user_loader
def loadUser(user_id):
    return session.query(hs_users).get(int(user_id))


def getUserInfo(show_password=True):
    useravatar = ""
    loginStatus = 0
    useremail = ""
    userpassword = ""
    if current_user.is_anonymous:
        username = DEFAULT_ANONYMOUS_USER
        fullname = DEFAULT_ANONYMOUS_USER
        userid = DEFAULT_ANONYMOUS_USERID
    else:
        user = betaUser().getItemByName(name=current_user.name)
        username = user.name
        fullname = user.fullname
        userid = user.id
        useravatar = user.avatar
        useremail = user.email
        loginStatus = 1
        if show_password:
            userpassword = user.password
    userinfo = {}
    userinfo["id"] = str(userid)
    userinfo["name"] = username
    userinfo["fullname"] = fullname
    userinfo["login"] = str(loginStatus)
    userinfo["email"] = useremail
    userinfo["password"] = userpassword
    if useravatar:
        userinfo["avatar"] = url_for('static', filename="uploads/"+useravatar)
    else:
        userinfo["avatar"] = url_for('static', filename='img/avatar.jpg')
    return userinfo

def getTheme():
    theme = ""
    if not current_user.is_anonymous:
        setting_info = betaSetting().getSettingbyUid(current_user.get_id())
        if setting_info and setting_info.theme is not None:
            theme = setting_info.theme
    return theme