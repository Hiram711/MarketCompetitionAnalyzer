#!/usr//bin/env/python3
# -*- coding:utf-8 -*-
__author__ = 'bill'

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import re

'''
we use the following codes to try our best to imitate a normal visit
usage:
    data_grabber_ky('昆明','上海','2018-10-31',proxy='http://118.190.95.35:9001')
'''


def save(filename, contents):
    fh = open(filename, 'w', encoding='utf-8')
    fh.write(contents)
    fh.close()


def data_grabber_cz(dept, arv, flight_date, proxy=None, executable_path=r'D:\chromedriver_win32\chromedriver.exe',
                    headless=False):
    # define the driver
    options = Options()
    options.headless = headless
    driver = webdriver.Chrome(chrome_options=options, executable_path=executable_path)
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)

    try:
        driver.implicitly_wait(10)  # define implicitly wait time
        driver.get('http://www.csair.com/')

        # wait for the page load
        try:
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.LINK_TEXT, '立即查询')))
        finally:
            print('Elements Loaded.')

        # fill in the dept airport
        action1 = ActionChains(driver)  # define action chains
        dep_city = driver.find_element_by_id('fDepCity')
        action1.move_to_element(dep_city).click(dep_city).perform()  # imitate the mouse move and click action
        dep_city.clear()
        dep_city.send_keys(dept)
        dep_city.send_keys(Keys.ENTER)

        # fill in the arrive airport
        arv_city = driver.find_element_by_id('fArrCity')
        arv_city.send_keys(arv)
        time.sleep(2)
        arv_city.send_keys(Keys.ENTER)
        time.sleep(2)

        # fill in the dept date
        action2 = ActionChains(driver)
        dep_date = driver.find_element_by_id('fDepDate')
        action2.move_to_element(dep_date).click(dep_date).perform()
        # dep_date.send_keys(Keys.CONTROL, 'a')
        # dep_date.send_keys(Keys.BACKSPACE)
        # dep_date.send_keys('2018-11-03')
        js = "var q=document.getElementById(\"fDepDate\");q.value=\"" + flight_date + "\";"
        print(js)
        driver.execute_script(js)
        time.sleep(1)
        # print("--------dep_date--------", dep_date.get_attribute('value'))
        action2.move_by_offset(1, 1).click()

        # click blank to close leaveDate form

        # submit to query
        action3 = ActionChains(driver)
        submit = driver.find_element_by_link_text('立即查询')
        action3.move_by_offset(0, 0).click().move_to_element(submit).click(submit).perform()

        # switch to the new window
        all_windows = driver.window_handles
        current_window = driver.current_window_handle
        for i in all_windows:
            if i != current_window:
                driver.switch_to.window(i)

        try:
            WebDriverWait(driver, 30, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'zls-flight-cell')))
        finally:
            print('New windows elements Loaded.')

    finally:
        soup = BeautifulSoup(driver.page_source, 'html5lib')

    '''
    # 直接从页面进行解析
    fileName = 'KY_昆明-成都-2019-01-10.htm'
    filePath = 'D:/tmp/c/' + fileName
    html_file = open(filePath, 'r', encoding='utf-8')
    html_handle = html_file.read()
    soup = BeautifulSoup(html_handle, 'html5lib')
    '''

    # find all flights by class element
    l_flt = soup.find_all(class_='zls-flight-cell')
    result = []
    try:
        for i, flt in enumerate(l_flt):
            # summary title
            company = '南方航空'
            fltno = re.findall(r'[A-Z]{2}[0-9]{4}', flt.find(class_='zls-flgno-info').text)[0]

            # share info
            share_str = flt.find(class_='zls-flgno-info').span
            is_shared = ''
            share_company = ''
            share_flight_no = ''
            if share_str is not None:
                is_shared = share_str.text
                share_company = re.findall(r'[^\x00-\xff]+', share_str.get('data-share'))[0]
                share_flight_no = re.findall(r'([^##]+)$', share_str.get('data-share'))[0]

            # summary info
            dpt = flt.find_all(class_='zls-flplace')[0].text.strip()
            dptTime = re.findall(r'[0-9]{2}[:][0-9]{2}', flt.find_all(class_='zls-flgtime-dep')[0].text.strip())[0]

            # 经停： 万州、中转，如果同时有经停、中转，则经停在第一个
            mid_str = flt.find(class_='zls-trans')
            mid = ''
            # 类型：空值、经停：xx、中转
            is_direct = '直飞'
            # 经停
            if mid_str is not None and '经停' in mid_str.text:
                mid = mid_str.text.replace(' ', '')  # re.findall(r'([^：]+)$', mid_str.text)[0].replace(' ', '')
                is_direct = re.findall(r'[^\x00-\xff]{2}', mid_str.text)[0]
            elif mid_str is not None:
                is_direct = flt.find(class_='transicon tooltip-trigger').text.replace(' ', '')
                mid = '中转：'+mid_str.text.replace(' ', '')  # 中转城市

            arrv = flt.find_all(class_='zls-flplace')[1].text.strip()
            arvTime = re.findall(r'[0-9]{2}[:][0-9]{2}', flt.find_all(class_='zls-flgtime-arr')[0].text.strip())[0]
            # 飞行时间
            flt_tm = flt.find(class_='zls-flg-time').text.replace('h', '小时').replace('m', '分钟').\
                replace('H', '小时').replace('M', '分钟')
            airplane_type = flt.find(class_='zls-flgplane').text.strip()

            # price detail
            price_list = []
            price_list_meta = flt.find_all(class_='zls-cabin-cell')
            for j, price_label in enumerate(price_list_meta):
                # if the label is blank, break
                if price_label.text == '':
                    continue  # 跳出本次循环

                # click price detail
                action = ActionChains(driver)
                detail_label = driver.find_elements_by_class_name('zls-flight-cell')[i].\
                    find_elements_by_class_name('zls-cabin-cell')[j]
                action.move_to_element(detail_label).click(detail_label).perform()

                # get the detail text
                price_soup = BeautifulSoup(driver.page_source, 'html5lib')
                price_list_htm = price_soup.find_all(class_='zls-flight-cell')[i].find_all(class_='zls-price-cell')
                for price_row in price_list_htm:
                    price_class1 = str(j)+price_row.find(class_='cabin-name').text  # j：0头等舱，1公务舱，2明珠经济舱,3经济舱
                    price_class = price_row.find(class_='cabin-other').find_all('li')[0].text.replace(' ', '')
                    discount = price_row.find(class_='cabin-other').find_all('li')[1].text.replace(' ', '')
                    if '全价' in discount:
                        discount = 10
                    elif '折' in discount:
                        discount = discount.replace('折', '')
                    else:
                        discount = ''
                    price_str = price_row.find(class_='cabin-price-info').text.replace('¥', '')
                    price_info = re.findall(r'[0-9]{1,}[.]{0,1}[0-9]*', price_str)[0]

                    price_list.append((price_class1, price_class, discount, price_info))
                    # print('-------price_list----:', price_list)

            # output
            result.append(
                dict(company=company, fltno=fltno, airplane_type=airplane_type, dpt=dpt, mid=mid, is_direct=is_direct,
                     dptTime=dptTime, arvTime=arvTime, arrv=arrv, flt_tm=flt_tm,  is_shared=is_shared,
                     share_company=share_company, share_flight_no=share_flight_no, price_list=price_list))

    except Exception as e:
        print('grab fail:', e)
    finally:
        driver.quit()  # make sure the webdriver closed after use
        return result


if __name__ == '__main__':
    result = data_grabber_cz('昆明', '西双版纳', '2019-01-15')
    print('get result')
    for i in result:
        print(i)
