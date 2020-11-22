#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Author: Bo Qi

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine, text, and_, desc
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import time

database = 'mysql+mysqldb://beta:beta@127.0.0.1:3306/beta_monitor?charset=utf8'

Base = declarative_base()
engine = create_engine(database)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autocommit=True)
session = Session()

def createAll():
    Base.metadata.create_all(engine)


DEPLOY_IN_LINE = 1
DEPLOY_TAP = 2

ADMIN_STATUS_UP = 1
ADMIN_STATUS_DOWN = 0

SUPER_ADMIN_ID = 1
SUPER_ADMIN_NAME = 'admin'
SUPER_ADMIN_FULLNAME = 'superAdmin'
SUPER_ADMIN_PWD = 'admin'

DEFAULT_MAIL_USER = "englab"

TASK_START_NOW = 1

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


# Define the SQL tables
class hsBase(object):
    """Beta Database tables Base, init the id"""
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)


class hs_users(UserMixin, hsBase, Base):
    """Owners table"""
    name = Column(String(15), nullable=False)
    fullname = Column(String(15), nullable=True)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(30), nullable=True)
    avatar = Column(String(30), nullable=True)
    group = Column(Integer)  # 1 means admin; 2 means user
    projects = relationship("hs_projects")
    devices = relationship("hs_devices")
    setting = relationship("hs_setting", uselist=False)
    log = relationship("hs_loggings")
    task_current = relationship("hs_tasks_current")
    task_history = relationship("hs_tasks_history")

    @property
    def password(self):
        return getattr(self, 'password_hash')
       # raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class hs_projects(hsBase, Base):
    """Project table"""
    name = Column(String(15), nullable=False)
    #owner = Column(String(30), nullable=True)
    desc = Column(String(200))
    devices = relationship("hs_devices")
    create_time = Column(Integer)
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"))


class hs_devices(hsBase, Base):
    """Device table
    hs_devices table record the basic information for a device
    All changes from the WebUI
    """
    name = Column(String(30))
    desc = Column(String(200))
    ip = Column(String(32))
    #owner = Column(String(30))
    sn = Column(String(20))
    os = Column(String(20))
    user = Column(String(20))
    password = Column(String(20))
    ssh = Column(Boolean)
    ssh_port = Column(Integer)
    telnet = Column(Boolean)
    telnet_port = Column(Integer)
    rest_api = Column(Boolean)
    rest_url = Column(String(50))
    #deploy = Column(Integer)
    admin_status = Column(Integer, nullable=False)
    daily_report = Column(Integer, nullable=False)
    create_time = Column(Integer)
    update_time = Column(Integer)
    status = relationship("hs_devices_status")
    cur_status = relationship("hs_devices_current_status")
    detail = relationship("hs_devices_detail")
    cur_task_id = relationship("hs_tasks_current")
    tasks_id = relationship("hs_tasks_history")
    follower = relationship("hs_rss")
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"))
    pid = Column("pid", Integer, ForeignKey("hs_projects.id"))


class hs_devices_current_status(hsBase, Base):
    """
    hs_devices_current_status used to record the current status of the device
    The item created when create a new device and updated by the script.
    """
    status = Column(Integer)
    status_info = Column(String(200))
    plat_license = Column(Integer)
    uptime = Column(Integer)  # record the uptime to check if the DUT was reboot
    coredumps = Column(String(500))  # record the coredump filename list
    version = Column(String(20))
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))


class hs_devices_status(hsBase, Base):
    """
    hs_devices_status used to record the device status
    This table created during create a new device, but updated from the script.
    """
    status = Column(Integer)
    status_info = Column(String(200))
    plat_license = Column(Integer)
    uptime = Column(Integer)  # record the uptime to check if the DUT was reboot
    coredumps = Column(String(500))  # record the coredump filename list
    version = Column(String(20))
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))


class hs_devices_detail(hsBase, Base):
    """
    hs_devices_detail: record the dynamic datas of the devices
    All changes from the script
    """
    cpu = Column(Integer)
    dcpu = Column(Integer)
    mem = Column(Integer)
    dmem = Column(Integer)
    sess = Column(Integer)
    create_time = Column(Integer)
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))


class hs_rss(hsBase, Base):
    mail = Column(String(100))
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))
    user_id=Column("user_id", Integer,ForeignKey("hs_users.id"))


class hs_tasks_current(hsBase, Base):
    """table for current tasks"""
    create_time = Column(Integer)
    start_time = Column(Integer)
    schedule_time = Column(Integer)
    update_time = Column(Integer)
    status = Column(Integer)
    result = Column(Integer)
    result_info = Column(String(200))
    task_type = Column(Integer)
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))
    log = Column(String(50))
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"))


class hs_tasks_history(hsBase, Base):
    """table for task history"""
    start_time = Column(Integer)
    end_time = Column(Integer)
    result = Column(Integer)
    result_info = Column(String(200))
    task_type = Column(Integer)
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))
    log = Column(String(50))
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"))


class hs_mails(hsBase, Base):
    host = Column(String(100))
    username = Column(String(100))
    password = Column(String(100))
    sender = Column(String(100))
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"),
                     nullable=False)

class hs_setting(hsBase, Base):
    """table for setting"""
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"), nullable=False)
    scantime = Column(Integer)
    dailyrepotime = Column(Integer)
    theme = Column(String(100))


class hs_loggings(hsBase, Base):
    user_id = Column("user_id", Integer, ForeignKey("hs_users.id"), nullable=False)
    create_time = Column(Integer)
    level_name = Column(String(20))
    message = Column(String(255))
    mod_name = Column(Integer)
    operation = Column(Integer)


def create_table(table_name, id, **kwargs):
    item = eval(table_name+'()')
    if "create_time" not in kwargs or not kwargs["create_time"]:
        kwargs["create_time"] = int(time.time())

    for i in kwargs:
        if i in dir(item) and isinstance(getattr(item, i), type(None)):
            setattr(item, i, kwargs[i])
    try:
        session.add(item)
        session.flush()
        return True
    except:
        return False

def update_table(table_name, id, **kwargs):
    item = eval(table_name+'()')
    if "update_time" not in kwargs or not kwargs["update_time"]:
        kwargs["update_time"] = int(time.time())

    item.id = id

    for i in kwargs:
        if i in dir(item) and isinstance(getattr(item, i), type(None)):
            setattr(item, i, kwargs[i])
    try:
        session.merge(item)
        session.flush()
        return True
    except:
        return False


# Basic operation for databases
class betaBase(object):

    def __init__(self):
        self.tname = ""

    def get(self, limit=0, offset=0):
        """
        Get items from the table
        :param limit: limit of get
        :param offset: offset
        :return: list of the table or None
        """
        try:
            items = []
            for i in session.query(eval(self.tname)).all():
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

    def count(self):
        """
        Get the count of the table
        :return: count of the items
        """
        try:
            return session.query(eval(self.tname)).count()
        except:
            return 0

    def all(self):
        """
        Get all items
        :return: object of the table
        """
        return self.get()

    def create(self, **kwargs):
        pass

    def update(self, **kwargs):
        pass

    def delete(self, id):
        """
        Delete one item
        :param id: the id of the item
        :return: True for success or False for fail
        """
        try:
            item = session.query(eval(self.tname)).get(id)
            session.delete(item)
            return True
        except:
            return False

    def deletes(self, ids):
        """
        Delete a list items
        :param ids: a id list of the item
        :return: True for success of False for fail
        """
        try:
            for i in ids:
                item = session.query(eval(self.tname)).get(i)
                session.delete(item)
            return True
        except:
            return False

    # def getIDByName(self, name):
    #     try:
    #         return session.query(eval(self.tname)).filter_by(name=name).one().id
    #     except:
    #         return 0
    #
    # def getNameByID(self, id):
    #     try:
    #         return session.query(eval(self.tname)).filter_by(id=id).one().name
    #     except:
    #         return None

    # def getObjByName(self, name):
    #     """ 暂用名 """
    #     try:
    #         return session.query(eval(self.tname)).filter_by(name=name).one()
    #     except:
    #         return None

    def getItemByID(self, id):
        """
        Get the column by the id
        :param id: id of the item
        :return: dict of the item or None
        """
        try:
            items = []
            for i in session.query(eval(self.tname)).filter_by(id=id).all():
                tmpDict = {}
                for j in i.__dict__.keys():
                    if j.startswith("_"):
                        continue
                    else:
                        tmpDict[j] = i.__dict__[j]
                items.append(tmpDict)
            return items[0]
        except:
            return None

    # def getItemsByDid(self, device_id):
    #     try:
    #         items = []
    #         for i in session.query(eval(self.tname)).filter_by(device_id=device_id).all():
    #             tmpDict = {}
    #             for j in i.__dict__.keys():
    #                 if j.startswith("_"):
    #                     continue
    #                 else:
    #                     tmpDict[j] = i.__dict__[j]
    #             items.append(tmpDict)
    #         return items
    #     except:
    #         return None
