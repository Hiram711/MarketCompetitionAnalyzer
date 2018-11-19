#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'Hiram Zhang'
import re

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


def data_grabber_mu(dept, arv, flight_date, proxy=None, executable_path=r'D:\chromedriver_win32\chromedriver.exe',
                    headless=True):
    # define the driver
    options = Options()
    options.headless = headless
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)

    try:
        driver = webdriver.Chrome(chrome_options=options, executable_path=executable_path)
        driver.implicitly_wait(10)  # define implicitly wait time
        driver.get('http://www.ceair.com/')

        # wait for the page load
        try:
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.ID, 'btn_flight_search')))  # wait for page loading
        finally:
            print('Elements Loaded.')

        # fill in the dept airport
        action1 = ActionChains(driver)  # define action chains
        dep_city = driver.find_element_by_id('label_ID_0')
        action1.move_to_element(dep_city).click(dep_city).perform()  # imitate the mouse move and click action
        dep_city.clear()
        dep_city.send_keys(dept)
        dep_city.send_keys(Keys.ENTER)

        # fill in the arrive airport
        arv_city = driver.find_element_by_id('label_ID_1')
        arv_city.send_keys(arv)
        arv_city.send_keys(Keys.ENTER)

        # fill in the dept date
        action2 = ActionChains(driver)
        dep_date = driver.find_element_by_id('depDt')
        action2.move_to_element(dep_date).click(dep_date).perform()
        dep_date.send_keys(Keys.CONTROL, 'a')
        dep_date.send_keys(Keys.BACKSPACE)
        dep_date.send_keys(flight_date)

        # submit to query
        action3 = ActionChains(driver)
        submit = driver.find_element_by_id('btn_flight_search')
        action3.move_by_offset(0, 0).click().move_to_element(submit).click(submit).perform()

        # switch to the new window
        all_windows = driver.window_handles
        current_window = driver.current_window_handle
        for i in all_windows:
            if i != current_window:
                driver.switch_to.window(i)

        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'summary')))
        finally:
            print('New window''s elements Loaded.')

    finally:
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        driver.quit()  # make sure the webdriver closed after use

    l_flt = soup.find_all('article', class_='flight')
    result = []
    for flt in l_flt:
        # summary title
        company = flt.select_one('.summary .title').find_all('span')[0].string
        fltno = re.findall(r'[A-Z]{2}[0-9]+', flt.select_one('.summary .title').get_text())[0]

        # summary info
        dpt = flt.select_one('.summary .info .airport.r').get_text()
        mid = flt.select_one('.summary .info .mid .zz').get_text()
        is_direct = flt.select_one('.summary .info .mid .zzjtzd').get_text()
        arrv = flt.select('.summary .info .airport')[1].get_text()
        flt_tm = flt.select_one('.summary').dfn.get_text()

        # detail
        luxury_price = flt.select_one('.detail .head.cols-3 .luxury').get_text()
        economy_price = flt.select_one('.detail .head.cols-3 .economy').get_text()
        member_price = flt.select_one('.detail .head.cols-3 .member').get_text()

        # body
        airplane_type = flt.select_one('.body .flight-details ul.detail-info li .d-4 .popup.airplane').attrs['acfamily']
        price_list_meta = flt.select('.body .product-list dl')
        price_list = []
        for price_row in price_list_meta:
            price_class1 = price_row.parent.attrs['data-type']
            price_class = price_row.find_all('dt')[0].get_text()
            price_info = price_row.select_one('dd.p-p').get_text()
            price_list.append((price_class1, price_class, price_info))

        # output
        result.append(
            dict(company=company, fltno=fltno, airplane_type=airplane_type, dpt=dpt, mid=mid, is_direct=is_direct,
                 arrv=arrv, flt_tm=flt_tm, luxury_price=luxury_price, economy_price=economy_price,
                 member_price=member_price, price_list=price_list))

    return result


if __name__ == '__main__':
    result = data_grabber_mu('昆明', '上海', '2018-11-13')
    for i in result:
        print(i)
