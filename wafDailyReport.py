#!/usr/bin/python
# -*- coding: UTF-8 -*-

from hbb_waf.device import *
from db.db import *
import sys, re
#from mail import Send_mail
import time
import datetime
from app.utils import Send_mail

TASK_RUNNING = 2
TASK_FINISH = 3
TASK_PASS = 1
TASK_FAIL = 2
TASK_ABORT = 3

DEVICE_ONLINE = 1
DEVICE_COREDUMP = 2
DEVICE_OFFLINE = 3
DEVICE_UNKNOWN = 4
DEVICE_ALARM = 5

device_id = sys.argv[1]
task_id = sys.argv[2]

taskCls = betaTaskCurrent()
deviceCls = betaDevice()
deviceDetailCls = betaDeviceDetail()

taskCls.update(task_id, status=TASK_RUNNING)

thisDevice = deviceCls.getItemByID(device_id)

dutIP = thisDevice["ip"]
dutName = thisDevice["name"]
dutOwner = thisDevice["owner"]
dutOS = thisDevice["os"] if thisDevice["os"] else "StoneOS"
dutSSH = thisDevice["ssh"]
dutTelnet = thisDevice["telnet"]
dutUsername = thisDevice["user"] if thisDevice["user"] else "beta"
dutPassword = thisDevice["password"] if thisDevice["password"] else "beta"
dutCpu = 0
dutVersion = ''
dutMem = 0
dutSession = 0
dutCoredump = ''
dutApmStatus = ''
#dutPid = os.getpid()

#taskCls.update(task_id, pid=dutPid)

if dutSSH:
    dutPort = thisDevice["ssh_port"]
    dutMethod = "ssh"
elif dutTelnet:
    dutPort = thisDevice["telnet_port"]
    dutMethod = "telnet"
else:
    print 'please use a valid method!'
    taskCls.update(task_id,status=TASK_FINISH,result=TASK_ABORT,result_info='No valid method!')
    deviceCls.update(device_id, status=DEVICE_UNKNOWN,status_info='Connection method configuration error!')
    status_info='Connection method configuration error!'
    content = 'susususuccess'
    MAIL = Send_mail(dutOwner,dutName,status_info,content)
    MAIL.send_mail()
    deviceDetailCls.create(device_id, cpu=dutCpu, mem=dutMem, sess=dutSession)
    sys.exit(0)

try:
    #mydut = getDevice(os=dutOS, con_method=dutMethod, ip=dutIP, name=dutName, user=dutUsername, password=dutPassword)
    mydut = WAF(os=dutOS, con_method=dutMethod, ip=dutIP, name=dutName, user=dutUsername, password=dutPassword)
    cpu1 = mydut.cmd('show cpu')
except Exception,e:
    print e
    print 'login failed!'
    taskCls.update(task_id,status=TASK_FINISH,result=TASK_FAIL,result_info='Connect failed!')
    deviceCls.update(device_id, status=DEVICE_OFFLINE,status_info='Connect failed!')
    status_info='Connect failed!'
    content = 'tttt'
    MAIL = Send_mail(dutOwner,dutName,status_info,content)
    MAIL.send_mail()
    deviceDetailCls.create(device_id, cpu=dutCpu, mem=dutMem, sess=dutSession)
    sys.exit(0)

try:
    content_text = []
    # get Version
    version1 = mydut.cmd('show version')
    version2 = version1.split('\r\n')
    version3 = version2[4].split()
    dutVersion = version3[3]
    dutModule = version2[3].split()[2]
    dutSN = version2[3].split()[4]
    dutUptime = version2[8].strip('\r')
    dutVer_to_mail = '版本信息：'+dutVersion
    content_text.append(dutVer_to_mail)
    dutModule_to_mail = '设备型号：'+dutModule
    content_text.append(dutModule_to_mail)
    dutSN_to_mail = '设备S/N:'+dutSN
    content_text.append(dutSN_to_mail)
    dutUptime_to_mail = '设备启动时间：'+dutUptime
    content_text.append(dutUptime_to_mail)

    # get CPU detail
    dcpu1 = mydut.cmd('show cpu detail')
    dcpu2 = dcpu1.split('Cpu utilization in last 60 minutes')[0]
    dcpu3 = 'Current cpu utilization'+dcpu2.split('Current cpu utilization')[1]
    dcpu = dcpu1.replace(dcpu3,'')
    #添加到content_text 列表，方便发邮件
    dcpu_to_mail = 'Show cpu detail: '+'\n'+dcpu
    content_text.append(dcpu_to_mail)

    # get memory detail ( CP&DP)
    dmem1 = mydut.cmd('show memory detail')
    dmem2 = dmem1.split('\n')
    dmem3 = dmem2[0].split(":")
    dmemCP = dmem3[1].split('%')[0]
    dmemDP = dmem3[2].strip(' %\r')
    dmem_to_mail = 'Show memory detail'+'\n'+dmem1
    content_text.append(dmem_to_mail)

    # get Session
    session1 = mydut.cmd('show session generic')
    pattern1 = '(max )(\d+)'
    pattern2 = '(alloc )(\d+)'
    pattern3 = '(deny session )(\d+)'
    pattern4 = '(free )(\d+)'
    pattern5 = '(tunnel )(\d+)'
    pattern6 = '(alloc failed )(\d+)'
    dutMax = int(re.search(pattern1, session1).group(2))
    dutSession = int(re.search(pattern2, session1).group(2))
    dutDeny = int(re.search(pattern3, session1).group(2))
    dutFree = int(re.search(pattern4, session1).group(2))
    dutTunnel = int(re.search(pattern5, session1).group(2))
    dutFailed = int(re.search(pattern6, session1).group(2))
    sess_to_mail = 'Show session generic'+'\n'+session1
    content_text.append(sess_to_mail)

    #get waf-rule info
    wafRuleInfoAll = mydut.cmd('show waf-rule info')
    wafRuleVersion = wafRuleInfoAll.split("\n")[0].split()[2].strip('\r')
    wafRuleRelDate = wafRuleInfoAll.split("\n")[1].split()[2]
    wafRuleRelTime = wafRuleInfoAll.split("\n")[1].split()[3].strip('\r')
    wafTotalRuleNum = wafRuleInfoAll.split("\n")[2].split()[3].strip('\r')
    wafRuleInfo_to_mail = 'Show waf-rule info: '+'\n'+wafRuleInfoAll
    content_text.append(wafRuleInfo_to_mail)

    #get waf-rule update
    wafRuleUpdate = mydut.cmd('show waf-rule update')
    updateMode = wafRuleUpdate.split("\n")[7].split()[1].strip('\r')
    updateStatus = wafRuleUpdate.split("\n")[9].split()[2].strip('\r')
    updateTime1 = wafRuleUpdate.split("\n")[11]
    updateYear = updateTime1.split()[7].strip('\r')
    updateMonth = updateTime1.split()[4]
    updateDate = updateTime1.split()[5]
    updateWeek = updateTime1.split()[3]
    updateTime = updateTime1.split()[6]
    wafRuleUpdate_to_mail = 'Show waf-rule update'+'\n'+ wafRuleUpdate
    content_text.append(wafRuleUpdate_to_mail)

    #get process
    pro0 = mydut.cmd('show process')
    pro1 = pro0.split('\n')
    Pid = []
    Process = []
    State = []
    Priority = []
    Cpu = []
    Memory = []
    Runtime = []
    # Fdnum = []
    for i in range(3,len(pro1)):
        Pid.append(pro1[i].split()[0])
        Process.append(pro1[i].split()[1])
        State.append(pro1[i].split()[2])
        Priority.append(pro1[i].split()[3])
        Cpu.append(pro1[i].split()[4])
        Memory.append(pro1[i].split()[5])
        Runtime.append(pro1[i].split()[6])
        # Fdnum.append(pro1[i].split()[7])
    proAlert = []
    pidAlert = []
    statAlert = []
    priorAlert = []
    cpuAlert = []
    memAlert = []
    runAlert = []
    AlertList = ['Show higher Memory and CPU processes:']
    for j in range(len(Cpu)):
        if float(Cpu[j]) > 0.1 and float(Memory[j]) > 0.1:
            proAlert.append(Process[j])
            pidAlert.append(Pid[j])
            statAlert.append(State[j])
            priorAlert.append(Priority[j])
            cpuAlert.append(Cpu[j])
            memAlert.append(Memory[j])
            runAlert.append(Runtime[j])
            AlertList.append('Pid:'+Pid[j]+' Process:'+Process[j]+' State:'+State[j]+' Priority:'+Priority[j]+' Cpu:'+Cpu[j]+' Memory:'+Memory[j]+' Runtime:'+Runtime[j])
        else:
            print "No process exceeded"
    content_text = content_text + AlertList

    # get console errorlog
    consoleErr1 = mydut.cmd('show tech-support console')
    if len(consoleErr1) ==0 or consoleErr1.strip()=='':
        print 'Nothing in console errorlog '
    else :
        consoleErr = consoleErr1.split('----')[0]
        consoleErr_to_mail = 'Show tech-support console: ' + '\n' + consoleErr
        content_text.append(consoleErr_to_mail)
    wafErr = mydut.cmd('show tech-support waf errorlog | exclude upstream ')
    if len(wafErr) ==0 or wafErr.strip()=='':
        print 'Nothing in waf errorlog '
    else :
        wafErr_to_mail = 'Show waf errorlog: ' + '\n' + wafErr
        content_text.append( wafErr_to_mail)

    # get mongo
    # 获取昨天的时间戳
    date = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    timestring = date + ' 00:00:00'
    time_strptime = time.strptime(timestring, '%Y-%m-%d %H:%M:%S')
    time_mktime = time.mktime(time_strptime)
    time_stamp = int(time_mktime)
    topNum1 = 100
    topNum2 = 50
    topNum3 = 10
    # mongo 下查找某一天top50的client的hit_count的命令
    client_ip = mydut.mongo(
        'db.web_security_log_client_ip_severity_1d.aggregate([{"$match":{"time":{"$eq": %d}}},{$group : {_id : "$client_ip", hit_count:{$sum : "$hit_count"}}},{"$sort":{"hit_count" : -1}},{"$limit" : %d}])' % (
            time_stamp, topNum1))
    clientIP_to_mail = 'Show client ip of top 100 :' + '\n' + client_ip
    content_text.append(clientIP_to_mail)
    ip_list = []
    line_list = client_ip.split('\n')
    #取出IP list，为取每个IP对应的防护规则的hit-count做准备
    for each_ip in line_list:
        ip = re.findall(r'(?<![\.\d])(?:\d{1,3}\.){3}\d{1,3}(?![\.\d])', each_ip)
        if ip:
            ip_list.append(ip[0])
    print ip_list

    # mongo 下查找某一天所有防护类型的hit_count的命令
    pro_type = mydut.mongo(
        'db.web_security_log_protection_type_action_1d.aggregate([{"$match":{"time":{"$eq":%d}}},{$group : {_id : "$protection_type", hit_count:{$sum : "$hit_count"}}}])' % time_stamp)
    proType_to_mail = 'Show protection_type  :' + '\n' + pro_type
    content_text.append(proType_to_mail)

    # mongo 下查找前一天，top100的规则ID的hit-count的命令
    ruleID = mydut.mongo(
        'db.web_security_log_protection_type_rule_id_1d.aggregate([{$match:{time : {$eq:%d}}},{$group:{_id:"$rule_id",hit_count:{$sum:"$hit_count"}}},{$sort:{"hit_count":-1}},{$limit:%d}])' % (
            time_stamp, topNum2))
    ruleID_to_mail = 'Show rule ID of top 100  :' + '\n' + ruleID
    content_text.append(ruleID_to_mail)

    # mongo 下查找前一天top10的clientIP，每条IP对应的防护类型的hit-countde命令
    if len(ip_list)>10:
        ip_list = ip_list[:10]
    for ip in ip_list:
        ip_pro = mydut.mongo(
            'db.web_security_log_client_ip_protection_type_1d.aggregate([{"$match":{"time":{$eq:%d},"client_ip":"%s"}},{"$group":{"_id":{"protection_type":"$protection_type"},"hit_count":{$sum:"$hit_count"}}},{"$sort":{"hit_count":-1}}])' % (
                time_stamp, ip))
        ipPro_to_mail = 'The protection_type of %s : ' % ip + '\n' + ip_pro
        content_text.append(ipPro_to_mail)

    # get Coredump
    dutCoredump = mydut.shell('ls /flash/core -l')
    mydut.shell('exit')
    print '********************* ' + dutCoredump
    if len(dutCoredump) ==0 or dutCoredump.strip( )=='':
        print 'No coredump exists '
    else:
        coredump_to_mail = 'Show Coredump list:  ' + '\n ' + dutCoredump
        content_text.append(coredump_to_mail)

    # send email
    content = '\n'.join(content_text)
    status = "Get device info Success!"
    res = 'beta@testsite.com'
    #MAIL = Send_mail(res, dutName, status, content)
    #MAIL = Send_mail(res, dutName, status)
    MAIL = Send_mail(res, thisDevice, status)
    MAIL.send_mail()
    taskCls.update(task_id, status=TASK_FINISH, result=TASK_PASS, result_info='Task is successfully!')

except Exception,e:
    print e
    print 'get device info failed!'
    taskCls.update(task_id,status=TASK_FINISH,result=TASK_FAIL,result_info='Get device info failed!')
    status_info='Get device info failed!'
    # MAIL = Send_mail(dutOwner,dutName,status_info)
    # MAIL.send_mail()
