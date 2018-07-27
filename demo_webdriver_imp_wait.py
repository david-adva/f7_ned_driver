#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2018-07-24 20:35:31
# @Author  : David Deng (ddengca@gmail.org)
# @Link    : http://example.org
# @Version : $Id$

'''
This script examines the effect of webdriver.implicity_wait()
'''

import time
import sys
from selenium import webdriver


def get_wait_time(driver, wait_value, ele):
    print('Using implicitly_wait(). Start to tick...')
    start = time.time()
    try:
        driver.implicitly_wait(wait_value)
        driver.find_element_by_id(ele)
    except Exception:
        pass
    end = time.time()
    print('Time passed are %i seconds!\n' % int(end - start))


def true_wait(driver, wait_value, ele):
    print('Using time.sleep(). Start to tick...')
    start = time.time()
    try:
        time.sleep(wait_value)
        driver.find_element_by_id(ele)
    except Exception:
        pass
    end = time.time()
    print('Time passed are %i seconds!\n' % int(end - start))


def main():
    try:
        my_web = webdriver.Firefox()
        my_web.get("https://www.google.com")

        while True:
            mode = input(
                "Pick the waiting mode, 'S' for sleep, " +
                "'I' for implicitly_wait: ")
            my_wait = input(
                "Input the wait time in seconds (ctrl-c to exit): ")
            my_id = input(
                "Input the ID of the element to search, e.g. 'main': ")

            if mode == 'S':
                true_wait(my_web, my_wait, my_id)
            elif mode == 'I':
                get_wait_time(my_web, my_wait, my_id)

    except KeyboardInterrupt:
        print('\nExit on KeyboardInterrupt!')
        my_web.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
