# !/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Author: bqi
#

from common import *
from copy import deepcopy
from datetime import datetime

deployStatus = {
    1: 'In-Line',
    2: 'Tap'
}
deviceStatus = {
    1: "ONLINE",
    2: "COREDUMP",
    3: "OFFLINE",
    4: "UNKNOWN",
    5: "ALARM"
}

#################################################################
# Device相关操作
#################################################################
@app.route('/getDeviceList', methods=['GET'])
def getDeviceList():
    owner_id = request.values.get("owner")
    page_num = request.values.get("page", 0)
    if int(page_num) > 0:
        offset = int(int(page_num)-1)*10
    else:
        offset = 0
    devices = []
    if owner_id:
        dev_obj = betaDevice().getItemsByUid(owner_id, limit=10, offset=offset)
    else:
        dev_obj = betaDevice().get(limit=10, offset=offset)

    for i in dev_obj:
        status = deviceStatus[4]
        status_info = "Unknown"
        current_status = betaDeviceCurrentStatus().getItemsByDid(i["id"])
        plat_license = 0
        if current_status:
            status = deviceStatus[int(current_status["status"])]
            status_info = current_status["status_info"]
            plat_license = current_status["plat_license"]

        # if i["status"] and int(i["status"]) in deviceStatus:
        #     status = deviceStatus[int(i["status"])]

        try:
            editable = True if i["user_id"] == current_user.id else False
        except:
            editable = False
        try:
            runable = True if i["user_id"] == current_user.id else False
        except:
            runable = False
        try:
            deleteable = True if i["user_id"] == current_user.id else False
        except:
            deleteable = False
        try:
            rssable = True if not current_user.is_anonymous else False
        except:
            rssable = False
        devices.append({
            "id": i["id"],
            "name": i["name"],
            "status": status,
            "owner": betaUser().getNameByID(i["user_id"]),
            "pid": i["pid"],
            "project": betaProject().getNameByID(i["pid"]),
            "status_info": status_info,
            "editable": editable,
            "plat_license": plat_license,
            "runable": runable,
            "deleteable": deleteable,
            "rssable": rssable
        })

    result = {'result': 'success', 'msg': ' Get detail success!', 'data': devices}
    return json.dumps(result)


@app.route('/getMyDevices', methods=['GET'])
def getMyDevices():
    devices = []
    dev_obj = betaDevice().getItemsByUid(current_user.id)

    for i in dev_obj:
        status = deviceStatus[4]
        current_status = betaDeviceCurrentStatus().getItemsByDid(i["id"])
        if current_status:
            status = deviceStatus[int(current_status["status"])]

        devices.append({
            "id": i["id"],
            "name": i["name"],
            "status": status,
        })

    result = {'result': 'success', 'msg': ' Get detail success!', 'data': devices}
    return json.dumps(result)


@app.route("/getDeviceByProject", methods=["GET"])
def getDeviceByProject():
    page_num = request.values.get("page", 0)
    project_id = request.values.get("project")
    if int(page_num) > 0:
        offset = int(int(page_num)-1)*10
    else:
        offset = 0
    if project_id:
        dev_obj = betaDevice().getItemsByPid(project_id, limit=10, offset=offset)
    else:
        dev_obj = []
    devices = []
    for i in dev_obj:
        status = deviceStatus[4]
        status_info = "Unknown"
        current_status = betaDeviceCurrentStatus().getItemsByDid(i["id"])
        if current_status:
            status = deviceStatus[int(current_status["status"])]
            status_info = current_status["status_info"]

        devices.append({
            "id": i["id"],
            "name": i["name"],
            "status": status,
            "owner": betaUser().getNameByID(i["user_id"]),
            "pid": i["pid"],
            "project": betaProject().getNameByID(i["pid"]),
            "status_info": status_info,
        })

    result = {'result': 'success', 'msg': ' Get detail success!', 'data': devices}
    return json.dumps(result)


@app.route("/getDevicePages", methods=["GET"])
def getDevicePages():
    owner_id = request.values.get("owner")
    per_page = request.values.get("per")
    if owner_id:
        count = betaDevice().getCountByUid(owner_id)
    else:
        count = betaDevice().count()
    if int(count) % int(per_page):
        pages = int(count)//int(per_page) + 1
    else:
        pages = int(count) // int(per_page)
    data={
        "pages": pages
    }
    result = {'result': 'success', 'msg': 'Get detail success!', 'data': data}
    return json.dumps(result)


@app.route("/getDevicePagesByProject", methods=["GET"])
def getDevicePagesByProject():
    per_page = request.values.get("per")
    project_id = request.values.get("project")
    if project_id:
        count = len(betaDevice().getItemsByPid(project_id))
    else:
        count = 0

    if int(count) % int(per_page):
        pages = int(count)//int(per_page) + 1
    else:
        pages = int(count) // int(per_page)
    data={
        "pages": pages
    }
    result = {'result': 'success', 'msg': 'Get detail success!', 'data': data}
    return json.dumps(result)


# 设备添加
@app.route("/devices/add", methods=["post"])
def addDevice():
    if current_user.is_anonymous:
        t = {"status": False, "msg": "Please login first！"}
        return json.dumps(t, ensure_ascii=False)
    param = request.data
    param = json.loads(param)
    name = param["name"]
    project = param["project"]
    ip = param["ip"]
    sn = param["sn"]
    devos = param["os"]
    user = param["user"] if param["user"] else "beta"
    password = param["password"] if param["password"] else "beta"
    ssh = param["ssh"]
    ssh_port = param["ssh_port"] if param["ssh_port"] else 22
    telnet = param["telnet"]
    telnet_port = param["telnet_port"] if param["telnet_port"] else 23
    # rest_api = param["rest_api"]
    # rest_url = param["rest_url"] if param["rest_url"] else ""
    # deploy = DEPLOY_IN_LINE if param["deploy"] == 'inline' else DEPLOY_TAP
    admin_status = param["admin_status"]
    daily_report = param["daily_report"]
    desc = param["desc"]
    # owner = current_user.name
    user_id = betaUser().getIDByName(name=current_user.name)
    # userinfo=betaUser().getItemByUid(user_id)
    user_mail=betaUser().getItemByUid(user_id)['email']
    device = betaDevice()
    try:
        myid = device.create(name, desc=desc, ip=ip, sn=sn, ssh=ssh,
                             ssh_port=ssh_port, telnet=telnet, os=devos,
                             telnet_port=telnet_port, user=user, password=password,
                             pid=project, admin_status=admin_status, daily_report=daily_report, user_id=user_id)
        if myid:
            t = {"status": True, "msg": "'%s' create success" % name}
            if user_mail:
                result=betaRss().create(myid, user_id, user_mail)
        else:
            t = {"status": False, "msg": "'%s' create failed" % name}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except Exception as e:
        print e
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


# 获取设备详细信息
@login_required
@app.route('/devices/detail', methods=["GET"])
def getDeviceInfo():
    id = request.values.get('id')
    projects_info = betaProject().getItemsByUid(current_user.get_id())
    projects = {}
    for j in projects_info:
        projects[j["id"]] = j["name"]
    device_detail = betaDevice().getItemByID(id)
    result = {'result': 'success', 'msg': 'Get detail success!', 'data': device_detail, 'projects': projects}
    return json.dumps(result)


# 编辑设备信息
@app.route("/devices/edit", methods=["post"])
def updateDevice():
    param = request.data
    param = json.loads(param)
    id = param["id"]
    name = param["name"]
    project = param["project"]
    ip = param["ip"]
    ssh = param["ssh"]
    sn = param["sn"]
    user = param["user"]
    password = param["password"]
    os = param["os"]
    ssh_port = param["ssh_port"] if param["ssh_port"] else 22
    telnet = param["telnet"]
    telnet_port = param["telnet_port"] if param["telnet_port"] else 23
    # rest_api = param["rest_api"]
    # rest_url = param["rest_url"] if param["rest_url"] else ""
    # deploy = DEPLOY_IN_LINE if param["deploy"] == 'inline' else DEPLOY_TAP
    admin_status = param["admin_status"]
    daily_report = param["daily_report"]
    desc = param["desc"]
    device = betaDevice()
    try:
        myid = device.update(id, name, desc=desc, ip=ip, sn=sn,
                             ssh=ssh, ssh_port=ssh_port, telnet=telnet, os=os, user=user,
                             password=password, telnet_port=telnet_port, rest_api=False, rest_url="",
                             pid=project, admin_status=admin_status, daily_report=daily_report)
        if myid:
            t = {"status": True, "msg": "'%s' Update Success!" % name}
        else:
            t = {"status": False, "msg": "'%s' Update Failed!" % name}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


# 删除设备
@app.route('/devices', methods=["DELETE"])
def delDevice():
    ids = request.data
    ids = json.loads(ids)
    device = betaDevice()
    res = device.deletes(ids)
    if res:
        t = {"status": True, "msg": "Delete Success!"}
    else:
        t = {"status": False, "msg": "Delete Failed!"}
    return json.dumps(t, ensure_ascii=False)


#get device rss
@app.route('/devices/rss', methods=['get'])
def get_device_rss():
    deviceId = request.values.get('id')
    rss_info = betaRss().getRssByUser(deviceId,current_user.get_id())
    mails=''
    if not rss_info:
        rss_flag=False

    else:
        rss_flag=True
        for mail in rss_info:
            mails=mails+mail+','
        mails=mails[:-1]
    deviceRssInfo={}
    deviceRssInfo['rss_flag']=rss_flag
    deviceRssInfo['rss_mail']=mails
    result = {'result': 'success', 'msg': 'Get detail success!', 'data': deviceRssInfo}
    return json.dumps(result)


#update device rss
@app.route('/devices/rss', methods=['post'])
def set_device_rss():
    param = request.data
    param = json.loads(param)
    deviceId = param["id"]
    rssFlag=param["rss_flag"]
    mails=param["mail"]
    mails=mails.split(',')
    user_id = betaUser().getIDByName(name=current_user.name)
    rss=betaRss()
    try:
        
        myid = rss.deletes(deviceid=deviceId, userid=user_id)
        if myid:
            t = {"status": True, "msg": " Success!" }
        else:
            t = {"status": False, "msg": "Failed!" }
        
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    if eval(rssFlag):
        try:
            myid=True
            for mail in mails:
                if mail!='':
                    result = rss.create(deviceid=deviceId,userid=user_id,mailaddress=mail)
                    myid=myid and result
            if myid:
                t = {"status": True, "msg": " Success!" }
            else:
                t = {"status": False, "msg": "Failed!" }
        except UnicodeDecodeError:
            t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
        except:
            t = {"status": False, "msg": "Unknown error, please contact the administrator"}
        
    
    return json.dumps(t, ensure_ascii=False)


@app.route('/deviceStatus', methods=['GET'])
def getStatusByID():
    deviceId = request.values.get("id")
    current_status = betaDeviceCurrentStatus().getItemsByDid(deviceId)
    status = 'UNKNOWN'
    if current_status:
        status = deviceStatus[int(current_status["status"])]
    result = {'result': 'success', 'msg': 'Get detail success!', 'data': status}
    return json.dumps(result)