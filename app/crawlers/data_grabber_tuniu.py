#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

options = Options()
options.headless = False
driver = webdriver.Chrome(chrome_options=options, executable_path=r'D:\chromedriver_win32\chromedriver.exe')
driver.get('http://flight.tuniu.com/')
