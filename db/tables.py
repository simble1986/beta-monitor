from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, BLOB
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .base import hsBase, Base


class hs_projects(hsBase, Base):
    """Project table"""
    name = Column(String(15), nullable=False)
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
    os = Column(String(20))
    user = Column(String(20))
    password = Column(String(20))
    ssh = Column(Boolean)
    ssh_port = Column(Integer)
    telnet = Column(Boolean)
    telnet_port = Column(Integer)
    admin_status = Column(Integer, nullable=False)
    daily_report = Column(Integer, nullable=False)
    weekly_report = Column(Boolean)
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


class hs_device_baseinfo(hsBase, Base):
    uptime = Column(Integer)
    version = Column(String(20))
    status = Column(Integer)
    status_info = Column(String(200))
    coredumps = Column(String(500))
    device_id = Column("device_id", Integer, ForeignKey("hs_devices.id"))


class hs_devices_resource(hsBase, Base):
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


class hs_device_logs(hsBase, Base):
    type = Column(Integer)
    logs = Column(BLOB())


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