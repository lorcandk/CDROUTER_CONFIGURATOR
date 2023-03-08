#!/usr/bin/env python

import sys
from datetime import date
from cdrouter import CDRouter
from cdrouter.configs import Config
from cdrouter.configs import ConfigsService


base = "http://broadbandlab.ddns.net:81"
token = "d1b9f0dd"

c = CDRouter(base, token=token)

cfg_default = c.configs.get("1072")
print(cfg_default.name)

cs = ConfigsService(c)

testvar1 = cs.get_testvar("1072", "wanVlanId").value
print(testvar1)

