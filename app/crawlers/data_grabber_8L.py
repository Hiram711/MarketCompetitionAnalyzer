#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

'''
we use the following codes to try our best to imitate a normal visit
usage:
    data_grabber_mu('昆明','上海','2018-10-31',proxy='http://118.190.95.35:9001')
'''


def data_grabber_8l(dept, arv, flight_date, proxy=None, executable_path=r'D:\chromedriver_win32\chromedriver.exe',
                    headless=True):
    # define the driver
    options = Options()
    options.headless = headless
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)

    try:
        driver = webdriver.Chrome(chrome_options=options, executable_path=executable_path)
        driver.get('http://www.luckyair.net/')

        # wait for the page load
        try:
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.ID, 'depcity_m')))  # wait for page loading
        finally:
            print('Elements Loaded.')

        # close the notice dialog
        action1 = ActionChains(driver)  # define action chains
        close_btn = driver.find_element_by_id('reload')
        action1.move_to_element(close_btn).click(close_btn).perform()

        # fill in the dept airport
        dep_city = driver.find_element_by_id('orgCity_m')
        dep_city.clear()
        dep_city.send_keys(dept)
        time.sleep(1)  # wait for js running
        dep_city.send_keys(Keys.ENTER)

        # fill in the arrive airport
        arv_city = driver.find_element_by_id('depcity_m')
        arv_city.send_keys(arv)
        time.sleep(1)
        arv_city.send_keys(Keys.ENTER)

        # fill in the dept date
        action2 = ActionChains(driver)
        dep_date = driver.find_element_by_id('flightDate')
        action2.move_to_element(dep_date).click(dep_date).perform()
        dep_date.send_keys(Keys.CONTROL, 'a')
        dep_date.send_keys(Keys.BACKSPACE)
        dep_date.send_keys(flight_date)

        # submit to query
        action3 = ActionChains(driver)
        close_cookie_notice = driver.find_element_by_css_selector('.notice-cookie ._close-icon')
        submit = driver.find_element_by_id('submitSearch')
        action3.move_by_offset(0, 0).click().move_to_element(close_cookie_notice).click().move_to_element(
            submit).click().perform()

        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'pri')))
        finally:
            print('New page''s elements Loaded.')

        driver.execute_script("return getFlightB2C('2018-11-28');")

    finally:
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        driver.quit()  # make sure the webdriver closed after use


if __name__ == '__main__':
    data_grabber_8l('昆明', '上海', '2018-11-22', headless=False)
