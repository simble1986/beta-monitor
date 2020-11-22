#!/usr/bin/env python
#-*- coding: utf-8 -*-
#
# Author: Bo Qi

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy import create_engine, text, and_, desc
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
import time

database = 'mysql+mysqldb://beta:beta@127.0.0.1:3306/beta_monitor?charset=utf8'
Base = declarative_base()
engine = create_engine(database)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine, autocommit=True)
session = Session()


def createAll():
    Base.metadata.create_all(engine)


# Define the SQL tables
class hsBase(object):
    """Beta Database tables Base, init the id"""
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    id = Column(Integer, primary_key=True)


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


# ==============================================================================
# Common Functions
# ==============================================================================
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
