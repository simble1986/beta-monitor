#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Bo Qi

from db.dbBase import *


class betaUser(betaBase):

    def __init__(self):
        super(betaUser, self).__init__()
        self.tname = "hs_users"
        self.super_admin_id = self.createSuperAdmin()

    def createSuperAdmin(self):
        try:
            if session.query(eval(self.tname)).filter_by(name=SUPER_ADMIN_NAME).count():
                self.super_admin_id = session.query(eval(self.tname)).filter_by(name=SUPER_ADMIN_NAME).first().id
            else:
                self.super_admin_id = self.create(name=SUPER_ADMIN_NAME, fullname=SUPER_ADMIN_FULLNAME, password=SUPER_ADMIN_PWD, group=1)
        except:
            self.super_admin_id = self.create(name=SUPER_ADMIN_NAME, fullname=SUPER_ADMIN_FULLNAME, password=SUPER_ADMIN_PWD, group=1)
        return self.super_admin_id

    def getSuperAdminID(self):
        return self.super_admin_id

    def getItemByName(self, name):
        try:
            return session.query(eval(self.tname)).filter_by(name=name).one()
        except:
            return None

    def getIDByName(self, name):
        try:
            return session.query(eval(self.tname)).filter_by(name=name).one().id
        except:
            return 0

    def getNameByID(self, id):
        try:
            return session.query(eval(self.tname)).filter_by(id=id).one().name
        except:
            return ""

    def create(self, name='', fullname='', password='', email='', avatar="", group=2):
        if not name or self.getItemByName(name=name):
            return False
        cls = eval(self.tname+"()")
        cls.name = name
        cls.fullname = fullname
        cls.password = password
        cls.email = email
        cls.avatar = avatar
        cls.group = group
        # cls.create_time = int(time.time())
        session.add(cls)
        session.flush()
        return cls.id

    def get(self, limit=10, offset=0):
        items = []
        if limit:
            t = session.query(eval(self.tname)).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).all()
        for i in t:
            p = {}
            p['id'] = i.id
            p['name'] = i.name
            # p['password'] = i.password
            p['fullname'] = i.fullname
            p['email'] = i.email
            p['avatar'] = i.avatar
            p['group'] = i.group
            # p['create_time'] = i.create_time
            p['projects'] = session.query(hs_projects).filter_by(user_id=i.id).count()
            p['devices'] = session.query(hs_devices).filter_by(user_id=i.id).count()
            items.append(p)
        return items

    def update(self, id, fullname='', password='', email='', avatar="", group=''):
        args = {}
        if fullname:
            args["fullname"] = fullname
        if password:
            args["password"] = password
        if email:
            args["email"] = email
        #if avatar:
        args["avatar"] = avatar
        if group:
            args["group"] = group
        return update_table(self.tname, id, **args)

    def deletes(self, ids):
        # ids should be a list
        flag = True
        for k in ids:
            if k == self.getSuperAdminID():
                print "Can't Remove the super admin"
                flag = False
            else:
                # update devices pid to default
                try:
                    # for i in session.query(hs_devices).filter_by(
                    #         pid=k).all():
                    #     if not update_table("hs_devices", i.id,
                    #                         pid=self.default_project_id):
                    #         flag = False
                    # todo: need to remove the avatar
                    item = session.query(eval(self.tname)).get(k)
                    session.delete(item)
                except:
                    flag = False
        return flag

    def reset(self, ids):
        # ids should be a list
        flag = True
        for id in ids:
            try:
                update_table(self.tname, id, password='beta')
            except:
                flag = False
        return flag

    def getItemByUid(self, uid):
        r = session.query(eval(self.tname)).get(uid)
        d = {}
        if r:
            d['id'] = uid
            d['name'] = r.name
            d['fullname'] = r.fullname
            d['email'] = r.email
            d['avatar'] = r.avatar
            d['group'] = r.group
            d['projects'] = r.projects
            d['devices'] = r.devices
        return d


class betaProject(betaBase):

    def __init__(self):
        super(betaProject, self).__init__()
        self.tname = "hs_projects"

    def _objFormat(self, items):
        l = []
        for i in items:
            d = {}
            d['id'] = i.id
            d['name'] = i.name
            d['desc'] = i.desc
            #d['owner'] = i.owner
            d['create_time'] = i.create_time
            d['devices'] = session.query(hs_devices).filter_by(pid=i.id).count()
            d['user_id'] = i.user_id
            l.append(d)
        return l

    def getNameByID(self, id):
        try:
            return session.query(eval(self.tname)).filter_by(id=id).one().name
        except:
            return None

    def create(self, name='', desc='', user_id=None):
        if not name:
            return False
        cls = eval(self.tname+"()")
        cls.name = name
        #cls.owner = owner
        cls.create_time = int(time.time())
        cls.desc = desc
        cls.user_id = user_id
        session.add(cls)
        session.flush()
        return cls.id

    def get(self, limit=0, offset=0):
        if limit:
            t = session.query(eval(self.tname)).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).all()
        items = self._objFormat(t)

        return items

    def getCountByUid(self, uid):
        try:
            return session.query(eval(self.tname)).filter_by(user_id=uid).count()
        except:
            return 0

    def getItemsByUid(self, uid, limit=0, offset=0):
        if limit:
            t = session.query(eval(self.tname)).filter_by(user_id=uid).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).filter_by(user_id=uid).all()
        items = self._objFormat(t)

        return items

    def update(self, id, name="", desc=""):
        args = {}
        if name:
            args["name"] = name
        if desc:
            args["desc"] = desc
        return update_table(self.tname, id, **args)


    def deletes(self, ids):
        flag = True
        for k in ids:
            if session.query(hs_devices).filter_by(pid=k).all():
                flag = False
            else:
                try:
                    item = session.query(eval(self.tname)).get(k)
                    session.delete(item)
                except:
                    flag = False
        return flag


class betaDevice(betaBase):

    def __init__(self):
        super(betaDevice, self).__init__()
        self.tname = "hs_devices"

    def _objFormat(self, items):
        l = []
        for i in items:
            d = {}
            d['id'] = i.id
            d['name'] = i.name
            d['desc'] = i.desc
            d["ip"] = i.ip
            d["os"] = i.os
            #d['owner'] = i.owner
            d['user'] = i.user
            d['password'] = i.password
            d["sn"] = i.sn
            d["ssh"] = i.ssh
            d["ssh_port"] = i.ssh_port
            d["telnet"] = i.telnet
            d["telnet_port"] = i.telnet_port
            d["rest_api"] = i.rest_api
            d["rest_url"] = i.rest_url
            #d["deploy"] = i[0].deploy
            d["admin_status"] = i.admin_status
            d["daily_report"] = i.daily_report
            d["pid"] = i.pid
            d['create_time'] = i.create_time
            d['update_time'] = i.update_time
            d["user_id"] = i.user_id

            l.append(d)

        return l

    def getNameByID(self, id):
        try:
            return session.query(eval(self.tname)).filter_by(id=id).one().name
        except:
            return None

    def create(self, name, desc="", ip="", os="", user="", password="", ssh=True, ssh_port=22, telnet=False, telnet_port=23, sn='',
               rest_api=False, rest_url="", admin_status=ADMIN_STATUS_UP, daily_report="", pid=0, user_id=''):
        if not name or not ip:
            return False
        if not pid:
            return False
        cls = hs_devices()
        cls.name = name
        cls.desc = desc
        cls.ip = ip
        cls.sn = sn
        #base_cls.owner = owner
        cls.os = os
        cls.user = user
        cls.password = password
        #base_cls.deploy = deploy
        cls.ssh = ssh
        cls.ssh_port = ssh_port
        cls.telnet = telnet
        cls.telnet_port = telnet_port
        cls.rest_api = rest_api
        cls.rest_url = rest_url
        cls.admin_status = admin_status
        cls.daily_report = daily_report
        cls.pid = pid
        cls.create_time = cls.update_time = int(time.time())
        cls.user_id = user_id
        session.add(cls)
        session.flush()
        return cls.id


    def getItemsByPid(self, pid, limit=0, offset=0):
        if limit:
            t = session.query(hs_devices).filter_by(pid=pid).offset(offset).limit(limit).all()
        else:
            t = session.query(hs_devices).filter_by(pid=pid).offset(offset).all()

        items = self._objFormat(t)
        return items

    def getItemsByUid(self, uid, limit=0, offset=0):
        if limit:
            t = session.query(hs_devices).filter_by(user_id=uid).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(hs_devices).filter_by(user_id=uid).offset(offset).all()
        items = self._objFormat(t)

        return items

    def get(self, limit=0, offset=0):
        if limit:
            t = session.query(hs_devices).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(hs_devices).all()

        items = self._objFormat(t)

        return items

    def getCountByUid(self, uid):
        try:
            return session.query(eval(self.tname)).filter_by(user_id=uid).count()
        except:
            return 0

    def getItemByID(self, id):
        t = session.query(hs_devices).filter(hs_devices.id==id).all()
        items = self._objFormat(t)
        try:
            return items[0]
        except:
            return None

    def update(self, id, name="", desc="", ip="", ssh="", ssh_port="", telnet="", telnet_port="", os="", user="", password="", sn='',
               rest_api=False, rest_url="", admin_status=False, daily_report=False, pid=""):
        args = {}
        args1 = {}
        if name:
            args["name"] = name
        if desc:
            args["desc"] = desc
        if ip:
            args["ip"] = ip
        if os:
            args["os"] = os
        if sn:
            args["sn"] = sn
        if user:
            args["user"] = user
        if password:
            args["password"] = password
        if ssh in [True, False]:
            args["ssh"] = ssh
        if ssh_port:
            args["ssh_port"] = ssh_port
        if telnet in [True, False]:
            args["telnet"] = telnet
        if telnet_port:
            args["telnet_port"] = telnet_port
        if rest_api in [True, False]:
            args["rest_api"] = rest_api
        if rest_url:
            args["rest_url"] = rest_url
        if admin_status in [True, False]:
            args["admin_status"] = admin_status
        if daily_report in [True, False]:
            args["daily_report"] = daily_report
        if pid:
            args["pid"] = pid
        args["update_time"] = int(time.time())

        return update_table('hs_devices', id, **args)


    def deletes(self, ids):
        # ids should be a list
        flag = True
        for k in ids:
            try:
                # delete tasks
                taskHistory = betaTaskHistory()
                tasks = taskHistory.getItemsByDid(k)                
                task_ids = []
                if tasks:
                    for i in tasks:
                        task_ids.append(i["id"])
                
                taskHistory.delete(task_ids)

                # delete current tasks
                taskCurr = betaTaskCurrent()
                tasks = taskCurr.getItemsByDid(k)                
                task_ids = []
                if tasks:
                    for i in tasks:
                        task_ids.append(i["id"])
                taskCurr.delete(task_ids)

                # delete device_status
                devstatus = betaDeviceDetail()
                status = devstatus.getItemsByDid(k)
                status_ids = []
                for i in status:
                    status_ids.append(i["id"])
                devstatus.delete(status_ids)

                #delete device_rss
                devicerss=betaRss().deleteByDid(k)

                # delete device detail
                # issue: delete failed with  No row was found for one()
                #item = session.query(hs_devices_detail).filter_by(device_id=k).one()
                #session.delete(item)

                # delete device info
                item = session.query(eval(self.tname)).get(k)
                session.delete(item)

            except Exception as e:
                print (e.message)
                flag = False
        return flag


class betaDeviceDetail(betaBase):

    def __init__(self):
        super(betaDeviceDetail, self).__init__()
        self.tname = "hs_devices_detail"

    def create(self, device_id, cpu=0, dcpu=0, mem=0, dmem=0, sess=0, ctime=int(time.time())):
        if not device_id:
            return False
        cls = eval(self.tname+"()")
        cls.device_id = device_id
        cls.cpu = cpu
        cls.dcpu = dcpu
        cls.mem = mem
        cls.dmem = dmem
        cls.create_time = ctime
        cls.sess = sess
        session.add(cls)
        session.flush()
        return cls.id

    def get(self, limit=0, offset=0):
        details = []
        if limit:
            d = session.query(eval(self.tname)).order_by("-id").offset(offset).limit(limit).all()
        else:
            # get all
            d = session.query(eval(self.tname)).order_by("-id").all()
        for i in d:
            detail = {}
            detail['device_id'] = i.device_id
            detail['create_time'] = i.create_time
            detail['cpu'] = i.cpu
            detail['dcpu'] = i.dcpu
            detail['mem'] = i.mem
            detail['dmem'] = i.dmem
            detail['sess'] = i.sess
            details.append(detail)
        return details

    def getCountByUid(self, uid):
        try:
            return session.query(eval(self.tname)).filter_by(user_id=uid).count()
        except:
            return 0

    def getItemsByDid(self, device_id, start_time=None, end_time=None):
        details = []
        d = session.query(eval(self.tname)).filter_by(device_id=device_id)
        if start_time:
            d = d.filter(hs_devices_detail.create_time>start_time)
        if end_time:
            d = d.filter(hs_devices_detail.create_time<end_time)
        d = d.order_by(hs_devices_detail.create_time).all()
        for i in d:
            detail = {}
            detail['id']=i.id
            detail['create_time'] = i.create_time
            detail['cpu'] = i.cpu
            detail['dcpu'] = i.dcpu
            detail['mem'] = i.mem
            detail['dmem'] = i.dmem
            detail['sess'] = i.sess
            details.append(detail)
        return details

    def getCPU(self, device_id, start_time=None, end_time=None):
        cpus = []
        c = self.getItemsByDid(device_id=device_id, start_time=start_time, end_time=end_time)
        for i in c:
            cpu = {}
            cpu['create_time'] = i["create_time"]
            cpu['cpu'] = i["cpu"]
            cpus.append(cpu)

        return cpus

    def getMem(self, device_id, start_time=None, end_time=None):
        mems = []
        c = self.getItemsByDid(device_id=device_id, start_time=start_time, end_time=end_time)
        for i in c:
            mem = {}
            mem['create_time'] = i["create_time"]
            mem['mem'] = i["mem"]
            mems.append(mem)

        return mems

    def getSess(self, device_id, start_time=None, end_time=None):
        ses = []
        c = self.getItemsByDid(device_id=device_id, start_time=start_time, end_time=end_time)
        for i in c:
            se = {}
            se['create_time'] = i["create_time"]
            se['sess'] = i["sess"]
            ses.append(se)

        return ses


class betaDeviceCurrentStatus(betaBase):

    def __init__(self):
        super(betaDeviceCurrentStatus, self).__init__()
        self.tname = "hs_devices_current_status"

    def create(self, device_id, status=DEVICE_UNKNOWN, status_info="Unknown Status", plat_license=0, uptime=0, coredumps="", version=""):
        if not device_id:
            return False
        cls = hs_devices_current_status()
        cls.device_id = device_id
        cls.status = status
        cls.status_info = status_info
        cls.plat_license = plat_license
        cls.uptime = uptime
        cls.coredumps = coredumps
        cls.version = version
        session.add(cls)
        session.flush()
        return cls.id

    def update(self, id, status="", status_info="", plat_license=0, uptime=0, coredumps="", version=""):
        args = {}
        if status:
            args["status"] = status
        if status_info:
            args["status_info"] = status_info
        if plat_license:
            args["plat_license"] = plat_license
        if uptime:
            args["uptime"] = uptime
        if coredumps:
            args["coredumps"] = coredumps
        if version:
            args["version"] = version

        return update_table(self.tname, id, **args)

    def getItemsByDid(self, device_id):
        try:
            d = session.query(eval(self.tname)).filter_by(device_id=device_id).one()
            tmpDict = {}
            for i in d.__dict__.keys():
                if i.startswith("_"):
                    continue
                else:
                    tmpDict[i] = d.__dict__[i]
            return tmpDict
        except Exception as e:
            print e
            return None

    def updateCurrentStatus(self, device_id, status="", status_info="", plat_license=0, uptime=0, coredumps="", version=""):
        # update the current status
        if not device_id:
            return False
        current_item = self.getItemsByDid(device_id)
        if not current_item:
            self.create(device_id=device_id, status=status, status_info=status_info,
                        plat_license=plat_license, uptime=uptime, coredumps=coredumps,
                        version=version)
        else:
            current_id = current_item["id"]
            self.update(current_id, status=status, status_info=status_info, plat_license=plat_license,
                        uptime=uptime, coredumps=coredumps, version=version)


class betaDeviceStatus(betaBase):

    def __init__(self):
        super(betaDeviceStatus, self).__init__()
        self.tname = "hs_device_status"

    def create(self, device_id, status=DEVICE_UNKNOWN, status_info="Unknown Status", plat_license=0, uptime=0, coredumps="", version=""):
        if not device_id:
            return False
        cls = hs_devices_status()
        cls.device_id = device_id
        cls.status = status
        cls.status_info = status_info
        cls.plat_license = plat_license
        cls.uptime = uptime
        cls.coredumps = coredumps
        cls.version = version

        session.add(cls)
        session.flush()

        # update the current status
        betaDeviceCurrentStatus().updateCurrentStatus(device_id=device_id, status=status, status_info=status_info,
                                                      plat_license=plat_license, uptime=uptime, coredumps=coredumps,
                                                      version=version)
        return cls.id

    def update(self, device_id):
        print "Device status can't update"
        return False


class betaTaskCurrent(betaBase):

    def __init__(self):
        super(betaTaskCurrent, self).__init__()
        self.tname = "hs_tasks_current"

    def _objFormat(self, items):
        l = []
        for i in items:
            d = {}
            d['id'] = i.id
            d['create_time'] = i.create_time
            d['schedule_time'] = i.schedule_time
            d['start_time'] = i.start_time
            d['update_time'] = i.update_time
            d['device_id'] = i.device_id
            d['status'] = i.status
            d['result'] = i.result
            d['task_type'] = i.task_type
            d['log'] = i.log
            d['result_info'] = i.result_info
            d['user_id'] = i.user_id
            l.append(d)
        return l

    def create(self, device_id, start_time, task_type, user_id):
        if not device_id or not start_time:
            return False
        cls = hs_tasks_current()
        cls.create_time = int(time.time())
        cls.update_time = int(time.time())
        cls.device_id = device_id
        cls.start_time = start_time
        cls.task_type = task_type
        cls.user_id = user_id
        cls.status = 1
        #cls.result = 1
        session.add(cls)
        session.flush()
        return cls.id

    def update(self, id, schedule_time=0, start_time=0, update_time=0, status=0, result=0, result_info="", log=""):
        # status: 1-pending, 2-running, 3-finish
        # result: 1-pass, 2-fail, 3-abort
        if status not in range(4) or result not in range(4):
            return False
        args = {}
        if log:
            args["log"] = log
        if schedule_time:
            args["schedule_time"] = schedule_time
        if start_time:
            args["start_time"] = start_time
        if update_time:
            args["update_time"] = update_time
        if status:
            args["status"] = status
        if result:
            args["result"] = result
        if result_info:
            args["result_info"] = result_info
        return update_table(self.tname, id, **args)
    
    def get(self, limit=0, offset=0):
        if limit:
            t = session.query(eval(self.tname)).order_by(desc(eval(self.tname).id)).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).order_by(desc(eval(self.tname).id)).all()
        items = self._objFormat(t)
        return items

    def getCountByUid(self, uid):
        try:
            return session.query(eval(self.tname)).filter_by(user_id=uid).count()
        except:
            return 0

    def getItemsByDid(self, device_id, task_type=None):
        
        if task_type is None:
            # get all
            t = session.query(eval(self.tname)).filter_by(device_id=device_id).all()
        else:
            # filter by task_type
            t = session.query(eval(self.tname)).filter(and_(eval(self.tname).device_id==device_id, eval(self.tname).task_type==task_type)).all()
        items = self._objFormat(t)
        return items

    def getItemsByUid(self, user_id, limit=0, offset=0):
        if limit:
            t = session.query(eval(self.tname)).filter_by(user_id=user_id).order_by(desc(eval(self.tname).id)).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).filter_by(user_id=user_id).order_by(desc(eval(self.tname).id)).all()
        items = self._objFormat(t)
        return items
    

class betaTaskHistory(betaBase):

    def __init__(self):
        super(betaTaskHistory, self).__init__()
        self.tname = "hs_tasks_history"

    def _objFormat(self, items):
        l = []
        for i in items:
            d = {}
            d['id'] = i.id
            d['start_time'] = i.start_time
            d['end_time'] = i.end_time
            d['device_id'] = i.device_id
            d['result'] = i.result
            d['task_type'] = i.task_type
            d['log'] = i.log
            d['result_info'] = i.result_info
            d['user_id'] = i.user_id
            l.append(d)

        return l

    def getItemsByDid(self, device_id):
        try:
            items = []
            for i in session.query(eval(self.tname)).filter_by(device_id=device_id).all():
                tmpDict = {}
                for j in i.__dict__.keys():
                    if j.startswith("_"):
                        continue
                    else:
                        tmpDict[j] = i.__dict__[j]
                items.append(tmpDict)
            return items
        except:
            return None

    def create(self, device_id, start_time, end_time, result, task_type, user_id, log="", result_info=""):
        cls = hs_tasks_history()
        cls.device_id = device_id
        cls.start_time = start_time
        cls.end_time = end_time
        cls.result = result
        cls.task_type = task_type
        cls.log =log
        cls.result_info = result_info
        cls.user_id = user_id
        session.add(cls)
        session.flush()
        return cls.id

    def get(self, limit=0, offset=0):
        if limit:
            t = session.query(eval(self.tname)).order_by(desc(eval(self.tname).id)).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).order_by(desc(eval(self.tname).id)).all()
        items = self._objFormat(t)

        return items

    def getCountByUid(self, uid):
        try:
            return session.query(eval(self.tname)).filter_by(user_id=uid).count()
        except:
            return 0

    def getItemsByUid(self, user_id, limit=0, offset=0):
        if limit:
            t = session.query(eval(self.tname)).filter_by(user_id=user_id).order_by(desc(eval(self.tname).id)).offset(offset).limit(limit).all()
        else:
            # get all
            t = session.query(eval(self.tname)).filter_by(user_id=user_id).order_by(desc(eval(self.tname).id)).all()
        items = self._objFormat(t)

        return items


class betaMail(betaBase):
    def __init__(self):
        super(betaMail, self).__init__()
        self.tname = "hs_mails"
        # self.default_mail_id = self.createDefaultSender()

    # def createDefaultSender(self):
    #     try:
    #         if session.query(eval(self.tname)).filter_by(username='xxx').count():
    #             self.default_mail_id = session.query(eval(self.tname)).filter_by(username='xxx').first().id
    #         else:
    #             self.default_mail_id = self.create(host="xxx", username="xxx", password="xxx", sender="xxx")
    #     except:
    #         self.default_mail_id = self.create(host="xxx", username="xxx", password="xxx", sender="xxx")
    #     return self.default_mail_id
    #
    def getDefaultMailID(self):
        return 1

    def getDefaultSmtp(self):
        smtp_info = session.query(eval(self.tname)).filter_by(id=self.getDefaultMailID()).first()
        return [smtp_info.host, smtp_info.username, smtp_info.password, smtp_info.sender]

    def create(self, host="", username="", password="", sender=""):
        cls = hs_mails()
        cls.host = host
        cls.username = username
        cls.password = password
        cls.sender = sender
        cls.user_id = user_id
        session.add(cls)
        session.flush()
        return cls.id

    def update(self, id, host="", username="", password="", sender=""):
        args = {}
        if host:
            args["host"] = host
        if username:
            args["username"] = username
        if password:
            args["password"] = password
        if sender:
            args["sender"] = sender
        return update_table(self.tname, id, **args)


class betaSetting(betaBase):

    def __init__(self):
        super(betaSetting, self).__init__()
        self.tname = "hs_setting"

    def create(self, user_id, scantime=None, dailyrepotime=None, theme="default"):
        cls = eval(self.tname+"()")
        cls.user_id = user_id
        cls.scantime = scantime
        cls.dailyrepotime = dailyrepotime
        cls.theme = theme
        session.add(cls)
        session.flush()
        return cls.id

    def update(self, id, scantime=None, dailyrepotime=None, theme=None):
        args = {}
        if scantime is not None:
            args["scantime"] = scantime
        if dailyrepotime is not None:
            args["dailyrepotime"] = dailyrepotime
        if theme is not None:
            args["theme"] = theme
        return update_table(self.tname, id, **args)

    def getSettingbyUid(self, uid):
        t = session.query(eval(self.tname)).filter_by(user_id=uid).first()
        return t


class betaLogging(betaBase):

    def __init__(self):
        super(betaLogging, self).__init__()
        self.tname = "hs_loggings"


class betaRss(betaBase):
    def __init__(self):
        super(betaRss, self).__init__()
        self.tname = "hs_rss"
    
    
    def create(self,deviceid,userid,mailaddress):
        flag=True
        clt=hs_rss()
        clt.device_id=deviceid
        clt.mail=mailaddress
        clt.user_id=userid
        session.add(clt)
        session.flush()
        return flag

    def getRssMail(self,deviceid):
        rssmail=[]
        rss_info = session.query(eval(self.tname)).filter_by(device_id=deviceid).all()
        for i in rss_info:
            rssmail.append(i.mail)
        return rssmail
    def getRssByUser(self,deviceid,userid):
        rssmail=[]
        rss_info = session.query(eval(self.tname)).filter(eval(self.tname).device_id==deviceid).filter_by(user_id=userid).all()
        for i in rss_info:
            rssmail.append(i.mail)
        return rssmail
    
    def getRssUser(self,deviceid):
        rssuser=[]
        rss_info = session.query(eval(self.tname)).filter_by(device_id=deviceid).all()
        for i in rss_info:
            rssuser.append(i.user_id)
        return rssuser
        
    def deletes(self, deviceid, userid):
        flag=True
        rss_info = session.query(eval(self.tname)).filter(eval(self.tname).user_id==userid).filter_by(device_id=deviceid).all()
        for iterm in rss_info:
            session.delete(iterm)
            #session.flush()
        return flag

    def deleteByDid(self,deviceid):
        flag=True
        rss_info = session.query(eval(self.tname)).filter_by(device_id=deviceid).all()
        for iterm in rss_info:
            session.delete(iterm)
            #session.flush()
        return flag
    
    def deleteByUid(self,userid):
        flag=True
        rss_info = session.query(eval(self.tname)).filter_by(user_id=userid).all()
        for iterm in rss_info:
            session.delete(iterm)
            #session.flush()
        return flag

