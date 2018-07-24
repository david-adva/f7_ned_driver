#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-07-24 20:35:31
# @Author  : Your Name (you@example.org)
# @Link    : http://example.org
# @Version : $Id$

import time
from selenium import webdriver

my_web = webdriver.Firefox()
my_web.get("https://www.google.com")


def get_wait_time(driver, wait_value, ele):
    if wait_value:
        driver.implicitly_wait(wait_value)

    start = time.time()
    try:
        driver.find_element_by_id(ele)
    except Exception:
        pass
    print(str(int(time.time() - start)))
