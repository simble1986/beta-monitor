# !/usr/bin/env python
# encoding: utf-8
#
# Author: bqi
#

from flask_script import Manager
from app.app import *

manager = Manager(app)

if __name__ == '__main__':

    manager.run()
