#!/usr/bin/env python
# encoding: utf8

# Author: Bo Qi

import os
from db.db import betaTaskCurrent, betaTaskHistory, betaDevice, betaSetting
import time
import datetime
import subprocess

TASK_TIMEOUT = 1800
ON_BETA_SCHEDULE_TIME = 1800
NOT_ON_BETA_SCHEDULE_TIME = 86400
DEFAULT_DAILY_REPORT_TIME = 36000
TASK_PASS = 1
TASK_FAIL = 2
TASK_ABORT = 3


TASK_FINISH = 3
TASK_RUNNING = 2
TASK_PENDING = 1

ADMIN_STATUS_UP = 1
ADMIN_STATUS_DOWN = 0
ADMIN_STATUS_OFFLINE = 2

TASK_SCAN_TYPE = 1
TASK_DAILY_TYPE = 2

path = os.path.dirname(os.path.abspath(__file__))

class runner(object):

    def __init__(self):
        self.tasks = betaTaskCurrent()
        self.taskHistory = betaTaskHistory()
        self.devices = betaDevice()
        self.timeout = TASK_TIMEOUT
        self.upScheduleTime = TASK_TIMEOUT
        self.runningtask = {}
        pass

    def initTask(self):
        """Check and Add tasks for each devices"""
        print "Will create task for each device if neccessary ..."
        deviceList = self.devices.get()
        for i in deviceList:
            if i["admin_status"] == ADMIN_STATUS_OFFLINE:
                # do not check and add task for the offline device
                continue
            else:
                taskList = self.tasks.getItemsByDid(i["id"],task_type=TASK_SCAN_TYPE)
                if len(taskList) ==  0:
                    self.createNewTask(i["id"])
                if i["daily_report"] and i["os"]=="WAF":
                    dailytaskList = self.tasks.getItemsByDid(i["id"],task_type=TASK_DAILY_TYPE)
                    if len(dailytaskList) == 0:
                        self.createNewDailyTask(i["id"])


    def run(self):
        taskList = self.get()
        for i in taskList:
            device_id = i["device_id"]
            task_id = i["id"]
            task_type = i["task_type"]
            cur_time = int(time.time())
            self.tasks.update(task_id, schedule_time=cur_time, status=TASK_PENDING)
            if task_type == TASK_SCAN_TYPE:
                script = os.path.join(path, 'getDeviceInfo.py')
            elif task_type == TASK_DAILY_TYPE:
                script = os.path.join(path, 'wafDailyReport.py')
            #res = os.system("nohup python %s  %s %s 2>&1 &" %(script, str(device_id), str(task_id)))
            process = subprocess.Popen(['nohup','python',script,str(device_id), str(task_id),'2>&1','&'])
            self.runningtask[task_id] = [process,cur_time]

    def get(self):
        taskList = []
        deviceList = []
        for i in self.tasks.get():
            status = i["status"]
            startTime = i["start_time"]
            scheduleTime = i["schedule_time"]
            device_id = i["device_id"]
            task_type = i["task_type"]

            #print "Processing the task %s" %i["id"]

            #if not scheduleTime:
            #    scheduleTime = 0

            if status == TASK_FINISH:
                self.move2History(i)
                if i["id"] in self.runningtask.keys():
                    del self.runningtask[i["id"]]
            else:
                cur_time = time.time()
                if scheduleTime and scheduleTime + self.timeout <= cur_time:
                    print "The Task for %s spend to much time" %i['device_id']
                    self.taskTerminate(i["id"])
                    self.move2History(i)
                elif not scheduleTime and startTime <= cur_time:
                    if (device_id,task_type) not in deviceList:
                        deviceList.append((device_id,task_type))
                        taskList.append(i)
        return taskList

    def move2History(self, item):
        device_id = item["device_id"]
        task_id = item["id"]
        if device_id:
            start_time = item["start_time"]
            end_time = int(time.time())
            result = item["result"]
            log = item["log"]
            result_info = item["result_info"]
            task_type = item["task_type"]
            user_id = item["user_id"]
            # print "Move the Task %s to History list" %item["id"]
            self.taskHistory.create(start_time=start_time,
                                end_time=end_time,
                                result=result,
                                log=log,
                                device_id=device_id,
                                result_info=result_info,
                                task_type=task_type,
                                user_id=user_id)

            self.tasks.delete(task_id)
            if task_type == TASK_SCAN_TYPE:
                return self.createNewTask(device_id)
            elif task_type == TASK_DAILY_TYPE:
                devInfo = betaDevice().getItemByID(device_id)
                if devInfo["os"]=="WAF":
                    return self.createNewDailyTask(device_id)
        else:
            print "The device may removed. Task will be delete"
            self.tasks.delete(task_id)
            return True

    def createNewTask(self,device_id):
        taskList = self.tasks.getItemsByDid(device_id,task_type=TASK_SCAN_TYPE)
        devInfo = betaDevice().getItemByID(device_id)
        if devInfo:
            print "Create New tasks for %s" %device_id
            adminStatus = devInfo["admin_status"]
            user_id = devInfo["user_id"]

            currTime = int(time.time())
            scheduleTime = self.getOnBetaScheduleTime(device_id)
            if len(taskList) == 0:
                if adminStatus == ADMIN_STATUS_UP:
                    self.tasks.create(device_id=device_id, start_time=currTime+scheduleTime, user_id=user_id, task_type=TASK_SCAN_TYPE)
                else:
                    self.tasks.create(device_id=device_id, start_time=currTime+NOT_ON_BETA_SCHEDULE_TIME, user_id=user_id, task_type=TASK_SCAN_TYPE)
            elif len(taskList) == 1:
                task_id = taskList[0]["id"]
                if adminStatus == ADMIN_STATUS_UP:
                    self.tasks.update(id=task_id, start_time=currTime+scheduleTime)
                else:
                    self.tasks.update(id=task_id, start_time=currTime + NOT_ON_BETA_SCHEDULE_TIME)
            elif len(taskList) > 1:
                create_flag = 0
                for i in taskList:
                    start_time = i["start_time"]
                    if create_flag:
                        if start_time < currTime + self.timeout:
                            self.tasks.delete(i["id"])
                    else:
                        if start_time < currTime + self.timeout:
                            self.tasks.update(id=i["id"], start_time = currTime + self.timeout)
                            create_flag = 1
        else:
            print "Get device Information failed"

    def createNewDailyTask(self,device_id):
        taskList = self.tasks.getItemsByDid(device_id,task_type=TASK_DAILY_TYPE)
        devInfo = betaDevice().getItemByID(device_id)
        if devInfo:
            print "Create New daily report task for %s" %device_id
            adminStatus = devInfo["admin_status"]
            user_id = devInfo["user_id"]
            currTime = int(time.time())
            dailyrepotime = self.getDailyReportTime(user_id=user_id)
            if len(taskList) == 0:
                if adminStatus == ADMIN_STATUS_UP:
                    self.tasks.create(device_id=device_id, start_time=dailyrepotime, user_id=user_id, task_type=TASK_DAILY_TYPE)
            elif len(taskList) == 1:
                task_id = taskList[0]["id"]
                if adminStatus == ADMIN_STATUS_UP:
                    self.tasks.update(id=task_id, start_time = dailyrepotime)
            elif len(taskList) > 1:
                self.tasks.update(id=taskList[0]["id"], start_time = dailyrepotime)
                for i in taskList[1:]:
                    self.tasks.delete(i["id"])
        else:
            print "Get device Information failed"

    def taskTerminate(self, task_id):
        try:
            if self.runningtask[task_id][0].poll() is None:
                self.runningtask[task_id][0].kill()
            del self.runningtask[task_id]
        except:
            pass

    def killTimeoutTask(self):
        for task_id in self.runningtask.keys():
            cur_time = time.time()
            schedule_time = self.runningtask[task_id][1]
            if schedule_time + self.timeout <= cur_time:
                task = self.tasks.getItemByID(id=task_id)
                print "The Task for device %s spend to much time" %task["device_id"]
                self.taskTerminate(task["id"])
                self.move2History(task)

    def getOnBetaScheduleTime(self, device_id):
        """Get device's schedule time"""
        devInfo = betaDevice().getItemByID(device_id)
        user_id =devInfo["user_id"]
        setInfo = betaSetting().getSettingbyUid(user_id)
        if setInfo and setInfo.scantime:
            scheduleTime = setInfo.scantime*60
        else:
            scheduleTime = ON_BETA_SCHEDULE_TIME
        return scheduleTime

    def getDailyReportTime(self, user_id):
        setInfo = betaSetting().getSettingbyUid(user_id)
        if setInfo and setInfo.dailyrepotime:
            dailytime = setInfo.dailyrepotime
        else:
            dailytime = DEFAULT_DAILY_REPORT_TIME
        cur=datetime.datetime.now()
        cur_datetime = time.strptime('%s-%s-%s 00:00:00' %(cur.year,cur.month,cur.day), '%Y-%m-%d %H:%M:%S')
        dailyrepotime = int(time.mktime(cur_datetime)+dailytime)
        if dailyrepotime <= int(time.time()):
            dailyrepotime += 86400
        return dailyrepotime


if __name__=="__main__":
    schedule = runner()
    while True:
        try:
            schedule.initTask()
            schedule.run()
            schedule.killTimeoutTask()
            time.sleep(10)
        except:
            print "Meet an error, just continue ..."
            continue
