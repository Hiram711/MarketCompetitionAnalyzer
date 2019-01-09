#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from app.utils import getPinyin

options = Options()
options.headless = False
driver = webdriver.Chrome(chrome_options=options, executable_path=r'D:\chromedriver_win32\chromedriver.exe')
driver.get('http://www.sichuanair.com//')
wait = WebDriverWait(driver, 20)
dep_input = wait.until(
    EC.presence_of_element_located((By.ID, 'Search-OriginDestinationInformation-Origin-location_input_location')))
arv_input = wait.until(
    EC.presence_of_element_located((By.ID, 'Search-OriginDestinationInformation-Destination-location_input_location')))
date_picker = wait.until(
    EC.presence_of_element_located((By.NAME, 'Search/DateInformation/departDate_display')))

dep_input.click()
city_index = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.select_results .hotCity .title .col')))
alphabet = getPinyin('昆明')
if 'f' >= alphabet >= 'a':
    target_city_index = city_index[1]
elif 'g' >= alphabet >= 'j':
    target_city_index = city_index[2]
elif 'n' >= alphabet >= 'k':
    target_city_index = city_index[3]
elif 'w' >= alphabet >= 'p':
    target_city_index = city_index[4]
elif 'z' >= alphabet >= 'x':
    target_city_index = city_index[5]

target_city_index.click()
city_list = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.select_results .hotCity .city li')))
for i in city_list:
    if i.text == '昆明':
        i.click()
        break

arv_input.click()
city_index = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.select_results .hotCity .title .col')))
alphabet = getPinyin('青岛')
if 'f' >= alphabet >= 'a':
    target_city_index = city_index[1]
elif 'g' >= alphabet >= 'j':
    target_city_index = city_index[2]
elif 'n' >= alphabet >= 'k':
    target_city_index = city_index[3]
elif 'w' >= alphabet >= 'p':
    target_city_index = city_index[4]
elif 'z' >= alphabet >= 'x':
    target_city_index = city_index[5]

target_city_index.click()
city_list = wait.until(
    EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.select_results .hotCity .city li')))
for i in city_list:
    if i.text == '青岛':
        i.click()
        break

date_picker.send_keys(Keys.CONTROL, 'a')
date_picker.send_keys(Keys.BACKSPACE)
date_picker.send_keys('2019-02-16')
btn = driver.find_element(By.CSS_SELECTOR, '.ui-state-active, .ui-widget-content .ui-state-active')
btn.click()

driver.execute_script('submitForm();')
tb_head = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, '.tbh-section')))

soup = BeautifulSoup(driver.page_source, 'html5lib')
print(soup.prettify())
