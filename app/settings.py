# !/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Author: yuezhang
#

from common import *
from utils import apm2int, int2apm


defaultSetting = {
    "scantime": 30,
    "dailyrepohour": 10,
    "dailyrepomin": 0,
    "dailyrepoapm": "am"
}

# 删除用户
@app.route('/users', methods=["DELETE"])
def delUsers():
    ids = request.data
    ids = json.loads(ids)
    user = betaUser()
    res = user.deletes(ids)
    if res:
        t = {"status": True, "msg": "Success to delete users"}
    else:
        t = {"status": False, "msg": "Fail to delete all selected users"}
    return json.dumps(t, ensure_ascii=False)


#################################################################
# 探测器相关操作
#################################################################

# 编辑邮箱
@app.route('/mail', methods=["POST"])
def changeMail():
    param = request.data
    param = json.loads(param)
    id = param["id"]
    host = param["host"]
    username = param["username"]
    password = param["password"]
    sender = param["sender"]
    mails = betaMail()
    try:
        myid = mails.update(id, host=host, username=username, password=password, sender=sender)
        if myid:
            t = {"status": True, "msg": "Success to update mail server"}
        else:
            t = {"status": False, "msg": "Fail to update the mail server"}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


# 编辑探测器
@app.route('/setschedule', methods=["POST"])
def setSchedule():
    if current_user.is_anonymous:
        t = {"status": False, "msg": "Please login first"}
    else:
        param = request.data
        param = json.loads(param)
        scantime = param["scantime"]
        dailyrepohour = param["dailyrepohour"]
        dailyrepomin = param["dailyrepomin"]
        dailyrepoapm = param["dailyrepoapm"]
        dailyrepotime = apm2int(int(dailyrepohour), int(dailyrepomin), dailyrepoapm)
        schedule = betaSetting().getSettingbyUid(current_user.get_id())
        try:
            if schedule:
                myid = betaSetting().update(schedule.id, scantime=scantime, dailyrepotime=dailyrepotime)
            else:
                myid = betaSetting().create(user_id=current_user.get_id(), scantime=scantime, dailyrepotime=dailyrepotime)
            if myid:
                t = {"status": True, "msg": "Success to set schedule"}
            else:
                t = {"status": False, "msg": "Fail to set schedule"}
        except UnicodeDecodeError:
            t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
        except:
            t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


@app.route('/emailSetting', methods=["GET"])
def getMailSetting():
    mail_info = betaMail()

    default_mail = mail_info.getItemByID(mail_info.getDefaultMailID())
    mail_settings = {
        "id": default_mail["id"],
        "host": default_mail["host"],
        "username": default_mail["username"],
        "password": default_mail["password"],
        "sender": default_mail["sender"]
    }
    result = {'result': 'success', 'msg': ' Get email settings success!', 'data': mail_settings}
    return json.dumps(result)


@app.route('/dailyReportSetting', methods=["GET"])
def getDailySetting():
    dailySetting = {}
    if current_user.is_anonymous:
        t = {"status": False, "msg": "Please login first", "data": dailySetting}
    else:
        setting_info = betaSetting().getSettingbyUid(current_user.get_id())
        if setting_info and setting_info.dailyrepotime is not None:
            daily = int2apm(setting_info.dailyrepotime)
        else:
            daily = (defaultSetting["dailyrepohour"],defaultSetting["dailyrepomin"],defaultSetting["dailyrepoapm"])
        dailySetting = {
            "hour": daily[0],
            "min": daily[1],
            "apm": daily[2]
        }
        t = {"status": True, "msg": "Get daily setting success", "data":dailySetting}
    return json.dumps(t, ensure_ascii=False)

@app.route('/themeSetting', methods=["GET"])
def getThemeSetting():
    theme = "default"
    if current_user.is_anonymous:
        t = {"status": True, "msg": "Anonymous user, use default theme", "data": theme}
    else:
        setting_info = betaSetting().getSettingbyUid(current_user.get_id())
        if setting_info and setting_info.theme is not None:
            theme = setting_info.theme
        else:
            theme = "default"
        t = {"status": True, "msg": "Get theme success", "data": theme}
    return json.dumps(t, ensure_ascii=False)


@app.route('/setTheme', methods=["POST"])
def setTheme():
    param = request.data
    param = json.loads(param)
    theme = param["theme"]
    setting = betaSetting().getSettingbyUid(current_user.get_id())
    try:
        if setting:
            myid = betaSetting().update(setting.id, theme=theme)
        else:
            myid = betaSetting().create(user_id=current_user.get_id(), theme=theme)
        if myid:
            t = {"status": True, "msg": "Success to set theme"}
        else:
            t = {"status": False, "msg": "Fail to set theme"}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)



@app.route("/users/reset", methods=["post"])
def resetPassword():
    ids = request.data
    ids = json.loads(ids)
    user = betaUser()
    res = user.reset(ids)
    if res:
        t = {"status": True, "msg": "Success to reset password"}
    else:
        t = {"status": False, "msg": "Fail to reset password"}
    return json.dumps(t, ensure_ascii=False)
