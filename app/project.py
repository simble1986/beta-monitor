# !/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Author: bqi
#

from common import *

#################################################################
# Project相关操作
#################################################################
@app.route("/getProjList", methods=["GET"])
def getProjList():
    owner_id = request.values.get("owner")
    page_num = request.values.get("page", 0)
    if int(page_num)>0:
        offset = int(int(page_num)-1)*10
    else:
        offset = 0
    projects = []
    if owner_id:
        project_obj = betaProject().getItemsByUid(owner_id, limit=10, offset=offset)
    else:
        project_obj = betaProject().get(limit=10, offset=offset)
    for i in project_obj:
        try:
            editable = True if i["user_id"] == current_user.id else False
        except:
            editable = False
        try:
            deleteable = True if i["user_id"] == current_user.id else False
        except:
            deleteable = False
        try:
            rssable = True if not current_user.is_anonymous else False
        except:
            rssable = False
        projects.append({
            "id": i["id"],
            "name": i["name"],
            "desc": i["desc"],
            "owner": betaUser().getNameByID(i["user_id"]),
            "dcount": i["devices"],
            "editable": editable,
            "deleteable": deleteable,
            "rssable":rssable
        })
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': projects}
    return json.dumps(result)


@app.route("/getMyProjList", methods=["GET"])
def getMyProject():
    projects = []
    if not current_user.is_anonymous:
        user_id = current_user.get_id()
        project_obj = betaProject().getItemsByUid(user_id)

        for i in project_obj:
            projects.append({
                "id": i["id"],
                "name": i["name"]
            })
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': projects}
    return json.dumps(result)


@app.route("/getProjectPages", methods=["GET"])
def getProjectPages():
    owner_id = request.values.get("owner")
    per_page = request.values.get("per")
    if owner_id:
        count = betaProject().getCountByUid(owner_id)
    else:
        count = betaProject().count()
    if int(count) % int(per_page):
        pages = int(count)//int(per_page) + 1
    else:
        pages = int(count) // int(per_page)
    data={
        "pages": pages
    }
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': data}
    return json.dumps(result)

# 项目详细信息
@app.route('/projects/detail', methods=["GET"])
def getProjectInfo():
    id = request.values.get('id')
    project_detail = betaProject().getItemByID(id)
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': project_detail}
    return json.dumps(result)


# 新增项目
@app.route("/projects/add", methods=["post"])
def addProject():
    if current_user.is_anonymous:
        t = {"status": False, "msg": "Please login first！"}
        return json.dumps(t, ensure_ascii=False)
    param = request.data
    param = json.loads(param)
    name = param["name"]
    desc = param["desc"]
    # owner = current_user.name
    user_id = betaUser().getIDByName(name=current_user.name)
    project = betaProject()
    try:
        myid = project.create(name, desc, user_id)
        if myid:
            t = {"status": True, "msg": "Success to add project %s" % name}
        else:
            t = {"status": False, "msg": "Fail to add project <span class='test-danger'>%s</span>" % name}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except Exception as e:
        print e
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


# 更新项目
@app.route("/projects/edit", methods=["post"])
def editProject():
    param = request.data
    param = json.loads(param)
    id = param["id"]
    name = param["name"]
    desc = param["desc"]
    project = betaProject()
    try:
        myid = project.update(id, name, desc)
        if myid:
            t = {"status": True, "msg": "Success to edit project %s" % name}
        else:
            t = {"status": False, "msg": "Fail to edit project <span class='test-danger'>%s</span>" % name}
    except UnicodeDecodeError:
        t = {"status": False, "msg": "The beta monitor system doesn't support Chinese words"}
    except:
        t = {"status": False, "msg": "Unknown error, please contact the administrator"}
    return json.dumps(t, ensure_ascii=False)


# 删除项目
@app.route('/projects', methods=["DELETE"])
def delProjects():
    ids = request.data
    ids = json.loads(ids)
    project = betaProject()
    res = project.deletes(ids)
    if res:
        t = {"status": True, "msg": "Success to delete projects"}
    else:
        t = {"status": False, "msg": "Fail to delete all selected projects"}
    return json.dumps(t, ensure_ascii=False)

#get project rss
@app.route('/projects/rss',methods=['get'])
def get_project_rss():
    projectId = request.values.get('id')
    devices=betaDevice().getItemsByPid(projectId)
    mails=''
    rssInfos=[]
    for device in devices:
        rss_info = betaRss().getRssByUser(device['id'],current_user.get_id())
        if rssInfos==[]:
            rssInfos=set(rss_info)
        else:
            rssInfos=rssInfos&set(rss_info)

    rssInfos=list(rssInfos)
    if not rssInfos:
        rss_flag=False

    else:
        rss_flag=True
        for mail in rssInfos:
            mails=mails+mail+','
        mails=mails[:-1]
    projectRssinfo={}
    projectRssinfo['rss_flag']=rss_flag
    projectRssinfo['rss_mail']=mails
    result = {'result': 'success', 'msg': 'Get detail success!', 'data': projectRssinfo}
    return json.dumps(result)

#update project rss
@app.route('/projects/rss',methods=['post'])
def set_project_rss():
    param = request.data
    param = json.loads(param)
    projectId = param["id"]
    rssFlag=param["rss_flag"]
    mails=param["mail"]
    mails=mails.split(',')
    user_id = betaUser().getIDByName(name=current_user.name)
    rss=betaRss()
    devices=betaDevice().getItemsByPid(projectId)
    
    try:
        myid=True
        for device in devices:
            result = rss.deletes(deviceid=device['id'],userid=user_id)
            myid=myid and result
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
            for device in devices:
                for mail in mails:
                    if mail!='':
                        result = rss.create(deviceid=device['id'],userid=user_id,mailaddress=mail)
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

