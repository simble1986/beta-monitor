# !/usr/bin/env python
# encoding: utf-8
#
# Author: lcheng
#

import os
from common import *
from utils import allowed_file

# 更新用户信息
@app.route('/users/edit', methods=["POST"])
def updateUser():
    param = request.data
    param = json.loads(param)
    id = param["id"]
    fullname = param["fullname"]
    try:
        if param["password"] != betaUser().getItemByID(id)['password_hash']:
            password = param["password"]
        else:
            password = ''
    except:
        password = ''
    try:
        email = param["email"]
    except:
        email = ''
    try:
        group = param["group"]
    except:
        group = ''
    user = betaUser()
    try:
        myid = user.update(id, fullname=fullname, password=password, email=email, group=group)
        if myid:
            t = {"status": True, "msg": "Success to update user info"}
        else:
            t = {"status": False, "msg": "Fail to update user info"}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


@app.route('/uploadavatar', methods=["POST"])
def uploadAvatar():
    myuserid = current_user.get_id()
    if myuserid != DEFAULT_ANONYMOUS_USERID:
        file = request.files['avatar']
        if file.filename == '':
            t = {"status": False, "msg": "No selected file"}
            return json.dumps(t, ensure_ascii=False)
        if file and allowed_file(file.filename):
            # todo: need to change the filename
            filename = current_user.name + "_id" + str(current_user.id) + "." + file.filename.split(".")[-1]
            file.save(os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], filename))
            user = betaUser()
            user.update(id=myuserid, avatar=filename)
            t = {"status": True, "msg": "Upload avatar success"}
            return json.dumps(t, ensure_ascii=False)
        else:
            t = {"status": False, "msg": "Unknown error"}
            return json.dumps(t, ensure_ascii=False)
    else:
        t = {"status": False, "msg": "You should login at first"}
        return json.dumps(t, ensure_ascii=False)


@app.route('/deleteavatar', methods=["DELETE"])
def deleteAvatar():
    myuserid = current_user.get_id()
    if myuserid != DEFAULT_ANONYMOUS_USERID:
        user = betaUser()
        userInfo = user.getItemByID(myuserid)
        if user.update(id=myuserid, avatar=""):
            if userInfo["avatar"]:
                absAvatarFile = os.path.join(app.root_path, app.config['UPLOAD_FOLDER'], userInfo["avatar"])
                if(os.path.exists(absAvatarFile)):
                    os.remove(absAvatarFile)
            t = {"status": True, "msg": "Clear avatar success"}
        else:
            t = {"status": False, "msg": "Clear avatar fail"}
    else:
        t = {"status": False, "msg": "No permission!"}
    return json.dumps(t, ensure_ascii=False)


# 用户详细信息
@app.route('/users/detail', methods=["GET"])
def getUserDetail():
    id = request.values.get('id')
    user_detail = betaUser().getItemByID(id)
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': user_detail}
    return json.dumps(result)
