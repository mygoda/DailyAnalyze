# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from os.path import join
from ConfigParser import ConfigParser


config = ConfigParser()
config.readfp(open(join(__path__[0], 'default.cfg')))


