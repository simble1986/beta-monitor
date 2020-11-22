#!/usr/bin/env python
# encoding: utf-8

from device import *
from settings import *
from profile import *


# 项目列表页面
@app.route('/index.html', methods=['GET'])
@app.route('/', methods=['GET'])
@app.route('/projects', methods=['GET'])
def projectsPage():
    return render_template("projects.html", theme=getTheme())

@app.route('/testindex', methods=['GET'])
def homePage():
    return render_template("index.html", theme=getTheme())

# 设备列表
@app.route('/devices')
def devicesPage():
    return render_template('devices.html', theme=getTheme())

# 关于页面
@app.route('/about', methods=["GET"])
def aboutUs():
    return render_template("about.html", theme=getTheme())


# 扫描结果页面
@app.route('/schedules', methods=['GET'])
def schedulesPage():
    return render_template("schedule.html", theme=getTheme())

# 设置页面
@app.route('/settings', methods=["GET"])
def getSettings():
    mail_info = betaMail()

    user = betaUser()
    cur_user_group = user.getItemByName(name=current_user.name).group
    if cur_user_group == 1:
        try:
            default_mail = mail_info.getItemByID(mail_info.getDefaultMailID())
        except:
            default_mail = {}
        userList = user.get()
        user_items = []
        for i in userList:
            groupspan = userGroup[int(i["group"])][0]
            group = userGroup[int(i["group"])][1]
            user_items.append([i["id"], i["name"], i["fullname"], i["email"], i["devices"], i["projects"], group, groupspan])
    else:
        default_mail = ''
        user_items = ''
    user_id = current_user.get_id()
    setting_info = betaSetting().getSettingbyUid(uid=user_id)
    scansetting = setting_info.scantime if setting_info else defaultSetting["scantime"]
    return render_template("settings.html", theme=getTheme(), mailserver=default_mail, users=user_items, scansetting=scansetting)


# 设备详情页面
@app.route('/device_info')
def getDetail():
    dev_info = betaDevice().get()
    dev_info_cp = dev_info[:]
    for i, v in enumerate(dev_info_cp):
        status = betaDeviceCurrentStatus().getItemsByDid(v["id"])
        if not status:
            dev_info[i]["status"] = "UNKNOWN"
        else:
            dev_info[i]["status"] = deviceStatus[status['status']]
#        dev_info[i]["status"] = status
    # if status and int(status) in deviceStatus:
    #     span = deviceStatus[int(status)][0]
    #     status = deviceStatus[int(status)][1]
    # else:
    #     span = deviceStatus[4][0]
    #     status = deviceStatus[4][1]
    #create_time = datetime.utcfromtimestamp(dev_info['create_time'])
    #update_time = datetime.utcfromtimestamp(dev_info['update_time'])
    #dev_info.update({'create_time': create_time, 'update_time': update_time, 'project': betaProject().getNameByID(dev_info['pid'])})
    return render_template('device_info.html', theme=getTheme(), dev_info=dev_info)

# Profile页面
@app.route('/profile', methods=["GET"])
def getProfile():
    userinfo = getUserInfo()
    return render_template("profile.html", theme=getTheme(), userinfo=userinfo)

@app.route('/mydetail', methods=["GET"])
def myDetail():
    return render_template('mydetail.html', theme=getTheme())


# 设备信息
#@app.route('/device_info')
#def get_device_info():
#    all_info = betaDevice().get()
#    all_info_b = deepcopy(all_info)
#    for i, v in enumerate(all_info):
        # status = deviceStatus[4]
        # status_info = "Unknown"
        # current_status = betaDeviceCurrentStatus().getItemsByDid(i["id"])
        # if current_status:
        #     status = deviceStatus[int(current_status["status"])]
        #     status_info = current_status["status_info"]

#        create_time = datetime.utcfromtimestamp(v["create_time"])
#        update_time = datetime.utcfromtimestamp(v["update_time"])
#        all_info_b[i].update({'create_time': create_time, 'update_time': update_time})
#    return render_template('device_info.html', theme=getTheme(), dev_info=all_info_b)

# 设备详情页面
@app.route('/detail/<id>')
def get_detail(id):
    dev_info = betaDevice().getItemByID(id)
    current_status = betaDeviceCurrentStatus().getItemsByDid(id)
    status = current_status['status']
    if status and int(status) in deviceStatus:
        span = deviceStatus[int(status)][0]
        status = deviceStatus[int(status)][1]
    else:
        span = deviceStatus[4][0]
        status = deviceStatus[4][1]
    create_time = datetime.utcfromtimestamp(dev_info['create_time'])
    update_time = datetime.utcfromtimestamp(dev_info['update_time'])
    dev_info.update({'deploy': deployStatus[1], 'span': span, 'status': status, 'create_time': create_time, 'update_time': update_time, 'project': betaProject().getNameByID(dev_info['pid'])})
    return render_template('device_detail.html', id=id, dev_info=dev_info)
