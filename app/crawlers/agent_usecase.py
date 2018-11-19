#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

'''we use the following codes to try our best to disguise ourselves'''
options = Options()
options.add_argument('--proxy-server=http://118.190.95.35:9001')

driver = webdriver.Chrome(chrome_options=options, executable_path=r'D:\chromedriver_win32\chromedriver.exe')

driver.get('http://httpbin.org/ip')
print(driver.page_source)
driver.quit()
