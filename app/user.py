# !/usr/bin/env python
# encoding: utf-8
#
# Author: lcheng
#

from common import *


@app.route('/getauth', methods=['GET'])
def getAuth():
    userInfo = getUserInfo(show_password=False)
    return json.dumps(userInfo)


@app.route('/img/<filename>', methods=['GET'])
def getImg(filename):
    return url_for('static', filename='img/'+filename)


@app.route('/register', methods=['GET', 'POST'])
def register():
    param = request.data
    param = json.loads(param)
    name = param["username"]
    fullname = param["fullname"]
    password = param["password"]
    email = param["email"]
    user = betaUser()
    try:
        myid = user.create(name, fullname, password, email)
        if myid:
            t = {"status": True, "msg": "Success to register"}
        else:
            t = {"status": False, "msg": "Name <span class='test-danger'>%s</span> has been registered" % name}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


@app.route('/login', methods=['POST'])
def login():
    param = request.data
    param = json.loads(param)
    username = param["username"]
    password = param["password"]
    keeplogin = True if param["keeplogin"] else False
    user = betaUser().getItemByName(name=username)
    if user is not None and user.verify_password(password):
        login_user(user, keeplogin)
        t = {"status": True, "msg": "Login as %s success" % username}
    else:
        t = {"status": False, "msg": "Username/Password isn't correct"}

    return json.dumps(t, ensure_ascii=False)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    t = {"status": True, "msg": "Logout success!"}
    return json.dumps(t, ensure_ascii=False)

