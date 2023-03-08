#!/usr/bin/env python

import sys
from datetime import date
from cdrouter import CDRouter
from cdrouter.configs import Config
from cdrouter.configs import ConfigsService
from cdrouter.configs import Testvar


base = "http://broadbandlab.ddns.net:81"
token = "d1b9f0dd"

c = CDRouter(base, token=token)

cfg_default = c.configs.get("1072")
print(cfg_default.name)

cs = ConfigsService(c)

testvar1 = cs.get_testvar("1072", "wanVlanId").value
print(testvar1)

tv = cs.get_testvar("1072", "wanVlanId")
tv.value = "2000"
print(tv.value)

c.configs.edit_testvar("1072", Testvar(name='wanVlanId', value="2000"))

testvar1 = cs.get_testvar("1072", "wanVlanId").value
print(testvar1)
