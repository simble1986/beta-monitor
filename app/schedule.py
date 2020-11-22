# !/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Author: yzhang
#

from common import *

TASK_PASS = 1
TASK_FAIL = 2
TASK_ABORT = 3

TASK_FINISH = 3
TASK_RUNNING = 2
TASK_PENDING = 1

TASK_SCAN_TYPE = 1
TASK_DAILY_TYPE = 2

taskStatus = {1: "PENDING",
              2: "RUNNING",
              3: "FINISH"}

taskResult = {1: "PASS",
              2: "FAIL",
              3: "ABORT"}

taskStatusInfo = {
    TASK_FINISH: "Task finished",
    TASK_RUNNING: "Task is running",
    TASK_PENDING: "Waiting for schedule"
    }

#################################################################
# Task相关操作
#################################################################

# 新增一个任务
@app.route('/addTask', methods=["POST"])
def scanNow():
    param = request.data
    param = json.loads(param)
    id = param["id"]
    if current_user.is_anonymous:
        t = {"status": False, "msg": "No permission! Please Login!"}
    else:
        dev_obj = betaDevice().getItemByID(id)
        user_id = dev_obj["user_id"]
        device_name = dev_obj["name"]
        if str(current_user.get_id()) != str(user_id):
            t = {"status": False, "msg": "You are NOT the device owner!"}
        else:
            d_task = betaTaskCurrent().getItemsByDid(id, task_type=TASK_SCAN_TYPE)
            if d_task and d_task[-1]['status'] in [1, 2]:
                if betaTaskCurrent().update(d_task[-1]['id'], start_time=time.time(), update_time=time.time()):
                    t = {"status": True, "msg": "Update task '%s' success!" % d_task[-1]['id']}
                else:
                    t = {"status": False, "msg": "Update task '%s' failed!" % d_task[-1]['id']}
            else:
                new_task = betaTaskCurrent()
                task_id = new_task.create(device_id=id, start_time=time.time(), user_id=user_id, task_type=TASK_SCAN_TYPE)
                if task_id:
                    t = {"status": True, "msg": "New task '%s' created for %s!" %(task_id, device_name)}
                else:
                    t = {"status": False, "msg": "Fail to created for %s!" % (device_name)}
        return json.dumps(t, ensure_ascii=False)


# 删除任务
@app.route('/tasks', methods=["DELETE"])
def delTasks():
    ids = request.data
    ids = json.loads(ids)
    taskcurrent = betaTaskCurrent()
    res = taskcurrent.deletes(ids)
    if res:
        t = {"status": True, "msg": "Success to delete tasks"}
    else:
        t = {"status": False, "msg": "Failed to delete all selected tasks"}
    return json.dumps(t, ensure_ascii=False)


# 获取任务详细信息
@app.route('/tasks/detail', methods=["GET"])
def getTaskInfo():
    id = request.values.get('id')
    task_detail = betaTaskCurrent().getItemByID(id)
    task_detail['status'] = taskStatus[int(task_detail["status"])]
    if task_detail["schedule_time"]:
        task_detail['schedule_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(task_detail["schedule_time"]))
    else:
        task_detail['schedule_time'] = "not start"
    task_detail['update_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(task_detail["update_time"]))
    task_detail['device_name'] = betaDevice().getNameByID(task_detail["device_id"])
    if not task_detail['log']:
        task_detail['log'] = ""
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': task_detail}
    return json.dumps(result)


# 删除历史任务
@app.route('/historytasks', methods=["DELETE"])
def delHistoryTasks():
    ids = request.data
    ids = json.loads(ids)
    taskhistory = betaTaskHistory()
    res = taskhistory.deletes(ids)
    if res:
        t = {"status": True, "msg": "Success to delete history tasks"}
    else:
        t = {"status": False, "msg": "Failed to delete all selected history tasks"}
    return json.dumps(t, ensure_ascii=False)


# 获取历史任务详细信息
@app.route('/historytasks/detail', methods=["GET"])
def getHistoryTaskInfo():
    id = request.values.get('id')
    task_detail = betaTaskHistory().getItemByID(id)
    task_detail['result'] = taskResult[int(task_detail["result"])]
    task_detail['start_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(task_detail["start_time"]))
    task_detail['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(task_detail["end_time"]))
    task_detail['device_name'] = betaDevice().getNameByID(task_detail["device_id"])
    if not task_detail['log']:
        task_detail['log'] = ""
    result = {'result': 'success', 'msg': ' Get detail success!', 'data': task_detail}
    return json.dumps(result)


@app.route("/getTaskPages", methods=["GET"])
def getTaskPages():
    type = request.values.get("type")
    per_page = request.values.get("per")

    if not current_user.is_anonymous:
        user_id = current_user.get_id()
        if type == "current":
            tasks = betaTaskCurrent().getItemsByUid(user_id)
        elif type == "history":
            tasks = betaTaskHistory().getItemsByUid(user_id)
        else:
            tasks = []

        if len(tasks) % int(per_page):
            pages = len(tasks)//int(per_page) + 1
        else:
            pages = len(tasks) // int(per_page)
    else:
        pages = 0

    data={
        "pages": pages
    }
    result = {'result': 'success', 'msg': 'Get tasks pages success!', 'data': data}
    return json.dumps(result)


@app.route('/getSchedules', methods=['GET'])
def getScheduleLists():
    tasks = []
    if not current_user.is_anonymous:
        user_id = current_user.get_id()
        type = request.values.get("type")
        page_num = request.values.get("page")
        per = request.values.get("per")
        if int(page_num)>0:
            offset = int(int(page_num)-1)*50
        else:
            offset = 0
        if user_id and type == "current":
            task_obj = betaTaskCurrent().getItemsByUid(user_id, limit=int(per), offset=offset)
            for i in task_obj:
                if i["schedule_time"]:
                    schedule_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["schedule_time"]))
                else:
                    schedule_time = "Not Start"
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["start_time"]))
                status = taskStatus[int(i["status"])]
                tasks.append({
                    "id": i["id"],
                    "device_id": i["device_id"],
                    "schedule_time": schedule_time,
                    "start_time": start_time,
                    "status": status,
                    "result": i["result"],
                    "device_name": betaDevice().getNameByID(i["device_id"]),
                    "log": i["log"],
                    "status_info": taskStatusInfo[int(i["status"])]
                })
        elif user_id and type == "history":
            task_obj = betaTaskHistory().getItemsByUid(user_id, limit=int(per), offset=offset)
            for i in task_obj:
                start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["start_time"]))
                end_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(i["end_time"]))
                if not i["result"]:
                    result = ""
                else:
                    result = taskResult[int(i["result"])]
                if not i["result_info"]:
                    i["result_info"] = ""
                tasks.append({
                    "id": i["id"],
                    "start_time": start_time,
                    "end_time": end_time,
                    "result": result,
                    "device_id": i["device_id"],
                    "device_name": betaDevice().getNameByID(i["device_id"]),
                    "log": i["log"],
                    "result_info": i["result_info"]
                })

    result = {'result': 'success', 'msg': ' Get detail success!', 'data': tasks}
    return json.dumps(result)
