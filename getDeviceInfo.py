#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import functools
import datetime
from copy import deepcopy
import time
import datetime
from dateutil.relativedelta import relativedelta
from HBB.device import getDevice
from HBB.connection import ConnException
from db.db import *
import sys, os, re
import xmltodict
from app.utils import mySMTP

# map把按严重程度定义的状态和db.py中的状态映射起来
task_result_map = {0: TASK_PASS, 1: TASK_FAIL, 2: TASK_ABORT}
device_status_map = {0: DEVICE_ONLINE, 1: DEVICE_UNKNOWN, 2: DEVICE_ALARM, 3: DEVICE_COREDUMP, 4: DEVICE_OFFLINE}

taskCls = betaTaskCurrent()
deviceCls = betaDevice()
deviceStatus = betaDeviceStatus()
deviceDetailCls = betaDeviceDetail()

def main(device_id, task_id):
    taskCls.update(task_id, status=TASK_RUNNING)
    device = get_dev(device_id)
    try:
        dut = DUT(device)
        data, err_msg, task_result, device_status = dut.collectAllInfo()
    except ConnException, e:
        err_msg = ['Connect to device failed: %s'%e]
        task_result = TASK_ABORT
        device_status = DEVICE_OFFLINE
    except Unsupported_Platform, e: 
        # 不支持的设备
        err_msg =[str(e)]
        task_result = TASK_ABORT
        device_status = DEVICE_UNKNOWN
    except Exception, e:
        err_msg = [str(e)]
        task_result = TASK_ABORT
        device_status = DEVICE_UNKNOWN
    else:
        # todo: 更改数据表，存储更多设备信息, 如license、cp dp memory等。。
        deviceDetailCls.create(device_id, cpu=data['cpu'], mem=data['mem_detail'].get('cp'), sess=data['session'])
    finally:
        err_msg = '<hr>'.join(err_msg)
        taskCls.update(task_id, status=TASK_FINISH, result=task_result, result_info=err_msg if err_msg else 'TASK Completed Successfully!')
        deviceStatus.create(device_id, status=device_status, status_info = err_msg if err_msg else 'Device is OK!') # 添加到这里不合适 plat_license=1)
        if err_msg:
            send_mail(device_id, subject = '[Beta-Monitor]Your device %s got problems!'%device.name, content=[err_msg,])


def send_mail(dev_id, subject, content):
    """将某id设备的错误信息发送给owner
    """
    receivers = betaRss().getRssMail(device_id)
    if receivers:
    # 发件人不为空才发邮件
        dev = get_dev(dev_id)
        #smtp_host, smtp_user, smtp_pass, smtp_sender = betaMail().getDefaultSmtp()
        #smtp = mySMTP(smtp_sender, smtp_pass, smtp_host)
        smtp = mySMTP('beta.testsite.com', 'password', '127.0.0.1')
        smtp.send(receivers, subject, content)
        # todo: 优化邮件格式


def get_dev(dev_id):

    """通过dev_id获取设备对象

    """
    dev_attr = deviceCls.getItemByID(dev_id)
    cur_dev_attr = {}
    cur_dev_attr['os'] = dev_attr['os'] if dev_attr['os'] else 'StoneOS'
    cur_dev_attr['ip'] = dev_attr['ip']
    cur_dev_attr['con_method'] = 'ssh' if dev_attr['ssh'] else 'telnet'
    cur_dev_attr['port'] = dev_attr['ssh_port'] if dev_attr['ssh'] else dev_attr['telnet_port']
    cur_dev_attr['name'] = dev_attr['name']
    cur_dev_attr['user'] = dev_attr['user']
    cur_dev_attr['password'] = dev_attr['password']
    dev = getDevice(**cur_dev_attr)
    return dev




# ==================== Fuction Start ==========================


# def 装饰器，记录收集函数名###

#def collect_method(func):
#    @functools.wraps(func)
#    def wrapper(self, *args, **kw):
#        self.clct_mtd.add(func)
#        return func(self, *args, **kw)
#    return wrapper


class DUT(object):
    support_plat = ['E', 'T', 'S', 'K', 'A', 'AX', 'W']
#    clct_mtd = set([])

    def __init__(self, dev_obj):
        self.dut = dev_obj
        self.type = self.getDutType()
        if self.type not in self.support_plat:
            raise Unsupported_Platform("Current platform is not supported: %s"%self.type)

    def getDutType(self):
        return self.basic_info["type"]

    def collectAllInfo(self):
        data = {}
        err_msg = []
        task_result = device_status = 0

        data['cpu'] = self.checkCpu()
        data['mem_detail'] = self.checkMemDetail()
        data['session'] = self.checkSessions()
        data['coredumps'] = self.checkCoredumps() # cli方法不维护状态，先放后面
        data['license'] = self.checkLicense()

        dv = data.values()
        for i in dv:
            err_msg +=i[1]
        task_result = task_result_map[max(i[2] for i in dv)]
        device_status = device_status_map[max(i[3] for i in dv)]

        data_copy = deepcopy(data)
        for k, v  in data_copy.items():
            data[k] = v[0]

        return data, err_msg, task_result, device_status


    @property
    def basic_info(self):
        dutInfo = {}
        rt = self.dut.cli("show version")
        for i in rt.split("\r\n"):
            if "Product name" in i:
                dutInfo["type"] = re.search(r'Product name: SG-6000-(\w+?)\d+', i).groups()[0]
            if "Boot file" in i:
                dutInfo["image"] = re.search(r'Boot file is (\S+)', i).groups()[0]
            if "Uptime" in i:
                m = "Uptime is (\d+) days* (\d+) hours* (\d+) minutes* (\d+) seconds"
                r = re.search(m, i)
                t = int(r.groups()[0])*86400 + int(r.groups()[1])*3600 + int(r.groups()[2])*60 + int(r.groups()[3])
                dutInfo["uptime"] = t
        dutInfo["shell_pw"] = self.dut.shell_password
        return dutInfo

    def getLicense(self):
        days = None
        m = "(\d+)\s+days left"
        xml = '<rpc><get-config><configuration language="1" start-index="0" end-index="99"><vsys id="0"><mgmt><license_list target="1"  operation="8"></license_list></mgmt></vsys></configuration></get-config></rpc>'
        rs = self._xmlSend(xml)
        if rs:
            plat_time = ""
            try:
                lics = rs['rpc-reply']['get-config']['configuration']['vsys']['mgmt']['license_list']
                for l in lics:
                    if l['type'].upper() == "platform".upper():
                        plat_time = l['effective_time']
                        break
            except:
                return days
            rt = re.search(m, plat_time)
            if rt:
                days = int(rt.groups()[0])

        return days

    def checkLicense(self):
        # todo: check方法可以扩展告警条件，可以过滤重复告警
        days = self.getLicense()
        err_msg = []
        task_result = device_status = 0

        if days is None:
            err_msg.append('Get license info failed')
            task_result = device_status = 1
        else:
            # 以后可扩展告警条件
            pass
        return days, err_msg, task_result, device_status

    def getAppTop10(self, sort_by=2, time_range=2):
        '''
        sort_by: sort by streams or sessions.
                 streams: 2, sessions: 3
        time_range: one hour: 1, one day: 2, one month: 3

        '''
        top_app = []
        xml = '<rpc><get-config><configuration language="2" start-index="0" end-index="9"><vsys id="0"><statistics_set_dynamic><traffic_rank target="1" operation="8"><time_range>%s</time_range><sort_by>%s</sort_by><type>app</type></traffic_rank></statistics_set_dynamic></vsys></configuration></get-config></rpc>' %(time_range, sort_by)
        rs = self._xmlSend(xml)
        if rs:
            try:
                apps = rs['rpc-reply']['get-config']['configuration']['vsys']['statistics_set_dynamic']['traffic_rank']
                if not isinstance(apps,list):
                    apps = [apps]
                if sort_by == 2:
                    for app in apps:
                        top_app.append((app['app_name'], int(app['upStream']) + int(app['downStream'])))
                elif sort_by == 3:
                    for app in apps:
                        top_app.append((app['app_name'], app['sessions']))
            except:
                return top_app
        return top_app


    def getUserTop10(self, sort_by=2, time_range=2):
        '''
        sort_by: sort by streams or sessions.
                 streams: 2, sessions: 3
        time_range: one hour: 1, one day: 2, one month: 3

        '''
        top_user = []
        xml = '<rpc><get-config><configuration language="2" start-index="0" end-index="9"><vsys id="0"><statistics_set_dynamic><traffic_rank target="1"  operation="8"><time_range>%s</time_range><sort_by>%s</sort_by><type>user</type></traffic_rank></statistics_set_dynamic></vsys></configuration></get-config></rpc>' %(sort_by, time_range)
        rs = self._xmlSend(xml)
        if rs:
            try:
                users = rs['rpc-reply']['get-config']['configuration']['vsys']['statistics_set_dynamic']['traffic_rank']
                if not isinstance(users,list):
                    users = [users]
                if sort_by == 2:
                    for user in users:
                        top_user.append((user['user'], int(user['upStream']) + int(user['downStream'])))
                elif sort_by == 3:
                    for user in users:
                        top_user.append((user['user'], user['sessions']))
            except:
                return top_user
        return top_user


    def getThreatTop10(self, sort_by=3, time_range=2):
        '''
        sort_by: sort by dstip or srcip or threat name.
                 dstip: 3, srcip: 2, threat name: 1
        time_range: one hour: 1, one day: 2, one month: 3

        '''
        now_datetime = self.getDatetime()
        if time_range == 1:
            t = now_datetime + relativedelta(hours=-1)
        elif time_range == 2:
            t = now_datetime + relativedelta(days=-1)
        elif time_range == 3:
            t = now_datetime + relativedelta(months=-1)
        t_timestamp = int(time.mktime(t.timetuple()))
        top_threat = []
        xml = '<rpc><get-config><configuration language="2" start-index="0" end-index="9"><vsys id="0"><logd><threat_msg_tbl target="1"  operation="8"><reversed>1</reversed><threat_merge>%s</threat_merge><time_start>%s</time_start><type>9</type></threat_msg_tbl></logd></vsys></configuration></get-config></rpc>' %(sort_by, t_timestamp)
        rs = self._xmlSend(xml)
        if rs:
            try:
                threats = rs['rpc-reply']['get-config']['configuration']['vsys']['logd']['threat_msg_tbl']
                if not isinstance(threats,list):
                    threats = [threats]
                if sort_by == 1:
                    for threat in threats:
                        top_threat.append((threat['threat_name'], threat['merge_count']))
                elif sort_by == 2:
                    for threat in threats:
                        top_threat.append((threat['src_ip'], threat['merge_count']))
                elif sort_by == 3:
                    for threat in threats:
                        top_threat.append((threat['dst_ip'], threat['merge_count']))
            except:
                return top_threat
        return top_threat


    def getCoredumps(self):
        rt = self.dut.shell('ls /etc/coredump')
        coredumps = rt.split()
        return coredumps

#    @collect_method
    def checkCoredumps(self):

        coredumps = self.getCoredumps()
        err_msg = []
        task_result = device_status = 0
        if coredumps:
            err_msg.append('Found coredump file')
            device_status = 3

        return coredumps, err_msg, task_result, device_status

        # todo:完善coredumps告警条件, 每个设备coredump文件列表入库，每次新获取的coredump文件列表与数据库历史记录对比，不一致则告警

    def getCpu(self):
        """
            Only get CPU info and return.

        """
        # todo: 完善不同设备获取信息的方法
        cpu = None
        if self.type in ['E', 'T', 'S', 'K', 'A', 'AX', 'W']:
            m = "Current cpu utilization :\s*([\d\.]+)%"
            rt = re.search(m, self.dut.cli("show cpu"))
            if rt:
                cpu = float(rt.groups()[0])
        return cpu

#    @collect_method
    def checkCpu(self):
        """
            Get CPU info and decide whether to send err_msg or not.

        """
        cpu = self.getCpu()
        err_msg = []
        task_result = device_status = 0

        if cpu is None:
            err_msg.append('Get CPU info failed')
            task_result = device_status = 1
        else:
            # 以后可扩展告警条件
            pass
        return cpu, err_msg, task_result, device_status



    def getMemDetail(self):
        """
            Only get Memory Detail info and return.

        """
        mem = {}
        if self.type in ['E', 'T', 'S', 'K', 'A', 'AX', 'W']:
            m = "The percentage of CP memory utilization:\s*([\d\.]+)%\s+DP memory utilization:\s*([\d\.]+)%"
            rt = re.search(m, self.dut.cli("show memory detail"))
            if rt:
                mem = {"cp": float(rt.groups()[0]), "dp": float(rt.groups()[1])}
        return mem

    def checkMemDetail(self):
        """
            Get Memory detail info  and decide whether to send err_msg or not .

        """
        mem = self.getMemDetail()
        err_msg = []
        task_result = device_status = 0

        if not mem:
            err_msg.append('Get Memory detail info failed')
            task_result = device_status = 1
        else:
            # 以后可扩展告警条件
            pass
        return mem, err_msg, task_result, device_status

    def getMemCP(self):
        memcp = self.getMemDetail().get('cp')
        return memcp

    def checkMemCP(self):
        memcp = self.getMemCP()
        err_msg = []
        task_result = device_status = 0

        if memcp is None:
            err_msga.append('Get CP Memory info failed')
            task_result = device_status = 1
        else:
            # 以后可扩展告警条件
            pass
        return memcp, err_msg, task_result, device_status


    def getMemDP(self):
        memdp = self.getMemDetail().get('dp')
        return memdp

    def checkMemDP(self):
        memdp = self.getMemDP()
        err_msg = []
        task_result = device_status = 0

        if memdp is None:
            err_msg.append('Get DP Memory info failed')
            task_result = device_status = 1
        else:
            # 以后可扩展告警条件
            pass
        return memdp, err_msg, task_result, device_status


    def getSessions(self):
        sess = None
        if self.type in ['E', 'T', 'S', 'K', 'A', 'AX', 'W']:
            m = "Device: max \d+, alloc (\d+),"
            rt = re.search(m, self.dut.cli("show session g"))
            if rt:
                sess = rt.groups()[0]
        return sess

    def checkSessions(self):
        sess = self.getSessions()
        err_msg = []
        task_result = device_status = 0

        if sess is None:
            err_msg.append('Get Session info failed')
            task_result = device_status = 1
        else:
            # 以后可扩展告警条件
            pass
        return sess, err_msg, task_result, device_status

    def getDatetime(self):
        clock = self.dut.cli("show clock")
        m = re.search("Current time zone:\s+(\w+)\s+(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", clock)
        t_zone = m.groups()[0]
        t_str = m.groups()[1]
        t_datetime = datetime.datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
        if t_zone == 'gmt':
            t_datetime = t_datetime +  relativedelta(hours=8)
        return t_datetime


    def _xmlSend(self, xml):
        try:
            # try to parse the input as xml
            xmltodict.parse(xml)
        except:
            print "The String isn't like a xml: "
            print "="*100
            print xml
            print "="*100
            return False
        # xml re-assemble
        try:
            rs = self.dut.shell("echo '%s' | nc 127.0.0.1 999" % xml, mid_prompts={"/rpc-reply":"\r\n"})
            if "Connection refused" in rs:
                rs = self.dut.shell("echo '%s' | nc 127.0.0.1 9999" % xml, mid_prompts={"/rpc-reply":"\r\n"})
            rx = rs[rs.index("<rpc-reply"):rs.index("</rpc-reply>")+12]
        except ValueError:
            print "Send xml got an error"
            return False
        else:
            try:
                return xmltodict.parse(rx)
            except:
                print "The response isn't like a valid XML: "
                print "=" * 100
                print xml
                print "=" * 100
                return False


#def getLicense(dut):
#    days = 0
#    m = "(\d+)\s+days left"
#    xml = '<rpc><get-config><configuration language="1" start-index="0" end-index="99"><vsys id="0"><mgmt><license_list target="1"  operation="8"></license_list></mgmt></vsys></configuration></get-config></rpc>'
#    r = dut.shell("echo '%s' | nc 127.0.0.1 999" % xml, prompt="/rpc-reply")
#    r = r[r.index("<rpc-reply"):] + "/rpc-reply>"
#    try:
#        lic = xmltodict.parse(r)
#        plat_time = ""
#        for i in lic['rpc-reply']['get-config']['configuration']['vsys']['mgmt']['license_list']:
#            if i['type'].upper() == "platform".upper():
#                plat_time = i['effective_time']
#        rslt = re.search(m, plat_time)
#        if rslt:
#            days = int(rslt.groups()[0])
#        return days
#    except:
#        return days


# ====================  Fuction End  ==========================

class Unsupported_Platform(Exception):
    def __init__(self, *args):
        self.args = args

if __name__ == '__main__':
    device_id = sys.argv[1]
    task_id = sys.argv[2]
    main(device_id, task_id)
