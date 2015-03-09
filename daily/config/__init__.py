# -*- coding: utf-8 -*-
# __author__ = chenchiyuan

from __future__ import division, unicode_literals, print_function
from os.path import join
from ConfigParser import ConfigParser

try:
    from server import ConfigOverride
except ImportError:
    ConfigOverride = []

config = ConfigParser()
config.readfp(open(join(__path__[0], 'default.cfg')))

for(section, option, value) in ConfigOverride:
    config.set(section, option, value)


