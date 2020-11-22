#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
from random import randint, choice
from db.db import *
import smtplib
from yagmail.sender import SMTPBase

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

class mySMTP(SMTPBase, object):

    """
        从yagmail继承，主要修改了原库强制加密，增加了登录验证失败后继续尝试发邮件功能
        例:
            s = mySMTP(user, password, smtp.126.com)
            s.send(to, subject, contents)
            contents是一个列表，可以包含txt、html正文及附件
    """

    def __init__(
        self,
        user=None,
        password=None,
        host="smtp.gmail.com",
        port=None,
        smtp_starttls=None,
        smtp_ssl=False,
        smtp_set_debuglevel=0,
        smtp_skip_login=False,
        encoding="utf-8",
        oauth2_file=None,
        soft_email_validation=True,
        no_encrypt=True,
        **kwargs
    ):
        super(mySMTP, self).__init__(user,
                                         password,
                                         host,
                                         port,
                                         smtp_starttls,
                                         smtp_ssl,
                                         smtp_set_debuglevel,
                                         smtp_skip_login,
                                         encoding,
                                         oauth2_file,
                                         soft_email_validation,
                                         no_encrypt=no_encrypt,
                                         **kwargs)
        self.port = str(port) if port is not None  else "25" if no_encrypt else "465" if smtp_ssl else "587"
        self.no_encrypt = no_encrypt
        self.kwargs = kwargs

    @property
    def connection(self):
        if self.no_encrypt:
            return smtplib.SMTP
        else:
            return smtplib.SMTP_SSL if self.ssl else smtplib.SMTP

    @property
    def starttls(self):
        if self.no_encrypt:
            return False
        elif self.smtp_starttls is None:
            return False if self.ssl else True
        return self.smtp_starttls

    def login(self):
        if self.oauth2_file is not None:
            self._login_oauth2(self.credentials)
        else:
            self._login(self.credentials)

    def send(self, to=None,
             subject=None,
             contents=None,
             attachments=None,
             cc=None,
             bcc=None,
             preview_only=False,
             headers=None,
            ):
        if to:
            # send_flag用来区分验证错误和其他异常，验证错误后仍尝试发送邮件
            send_flag = 1
            try:
                self.login()
            except smtplib.SMTPAuthenticationError, e:
                self.log.error(e)
                self.log.error('Igonre Auth Error and try to send mail...')
            except smtplib.SMTPException, e:
                self.log.error(e)
                send_flag = 0
            finally:
                if send_flag:
                    recipients, msg_astring = self.prepare_send(
                        to, subject, contents, attachments, cc, bcc, headers
                    )
                    if preview_only:
                        return (recipients, msg_astring)
                    return self._attempt_send(recipients, msg_astring)
        else:
            self.log.error('Receiver is empty, quit')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def apm2int(hour, minu, apm):
    """将am/pm时间转成整数
       12:00 am -> 0
       1:00 am -> 3600
       2:30 pm -> 52200
    """
    result = 0
    if apm == 'am':
        result = hour%12*60*60+minu*60
    elif apm == 'pm':
        result = (hour%12+12)*60*60+minu*60
    return result


def int2apm(time_int):
    """将整数转成am/pm时间
       0 -> 12:00 am
       3600 -> 1:00 am
       52200 -> 2:30 pm
    """
    result = ()
    time_int = time_int/60
    if time_int >=0 and time_int <= 3540:
        minu = time_int%60
        hour = (time_int-minu)/60
        if hour==0:
            hour = 12
            apm = 'am'
        elif hour>0 and hour<12:
            apm = 'am'
        elif hour==12:
            apm = 'pm'
        elif hour>12 and hour<=23:
            hour = hour-12
            apm='pm'
    result = (hour, minu, apm)
    return result



def create_table():

    """ Create related tables in database """

    createAll()

def create_data(project_num, device_num, owner_num):

    """ Create db table and insert random data for test """

    period_num = 144 #(10min一个周期，共144周期即一天)
    all_projects = ['project_%s'%i for i in range(project_num)]
    all_devices = ['device_%s'%i for i in range(device_num)]
    all_owners = ['owner_%s'%i for i in range(owner_num)]
    all_ips = ['10.180.10.%s'%i for i in range(device_num)]

    # create tables
    createAll()

    # insert project data
    bp = betaProject()
    for i in all_projects:
        bp.create(name=i, owner=choice(all_owners), desc='This is a test sample of project %s'%i)

    # insert device data
    bd = betaDevice()
    for i, d in enumerate(all_devices):
        bd.create(name=d, desc='This is a test sample of device %s'%d, ip=all_ips[i], owner=choice(all_owners), user='test')

    # insert device detail
    bdd = betaDeviceDetail()
    yestd_time = int(time.time()-86400)
    for i, d in enumerate(all_devices):
        for t in range(period_num):
            bdd.create(device_id=i+1, cpu=randint(1, 100), mem=randint(1, 100), sess=randint(100,10000), ctime=yestd_time+600*t)


if __name__ == '__main__':
    # todo: issue for getDetailByDevice
    now = int(time.time())
    data = betaDeviceDetail().getDetailByDevice(device_id=int(sys.argv[1]), start_time=now-86400, end_time=now)
    r = agg_data(data, start_time=now-86400, end_time=now, period=3600)
    print 'Output: \n', r
    print 'Done, time cost: %s'%(time.time()-now)
