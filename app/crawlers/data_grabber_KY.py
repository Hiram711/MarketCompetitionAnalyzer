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

'''
we use the following codes to try our best to imitate a normal visit
usage:
    data_grabber_ky('昆明','上海','2018-10-31',proxy='http://118.190.95.35:9001')
'''


def data_grabber_ky(dept, arv, flight_date, proxy=None, executable_path=r'D:\chromedriver_win32\chromedriver.exe',
                    headless=True):
    # define the driver
    options = Options()
    options.headless = headless
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)

    try:
        driver = webdriver.Chrome(chrome_options=options, executable_path=executable_path)
        driver.implicitly_wait(10)  # define implicitly wait time
        driver.get('http://www.airkunming.com/')

        # wait for the page load
        try:
            WebDriverWait(driver, 20, 0.5).until(
                EC.presence_of_element_located((By.LINK_TEXT, '搜索航班')))
        finally:
            print('Elements Loaded.')

        # fill in the dept airport
        action1 = ActionChains(driver)  # define action chains
        dep_city = driver.find_element_by_id('orgCityLabel')
        action1.move_to_element(dep_city).click(dep_city).perform()  # imitate the mouse move and click action
        dep_city.clear()
        dep_city.send_keys(dept)
        dep_city.send_keys(Keys.ENTER)

        # fill in the arrive airport
        arv_city = driver.find_element_by_id('dstCityLabel')
        arv_city.send_keys(arv)
        arv_city.send_keys(Keys.ENTER)

        # fill in the dept date
        action2 = ActionChains(driver)
        dep_date = driver.find_element_by_id('leaveDate')
        action2.move_to_element(dep_date).click(dep_date).perform()
        js = "var q=document.getElementById(\"leaveDate\");q.value=\"" + flight_date + "\";"
        driver.execute_script(js)

        # click blank to close leaveDate form
        action_blank = ActionChains(driver)
        blank = driver.find_element_by_link_text('国内机票')
        # print("--------blank--------" + blank.get_attribute('href'))
        action_blank.move_to_element(blank).click(blank).perform()
        # action_blank.move_by_offset(10, 10).click().perform()
        # print("--------blank click--------")

        # submit to query
        action3 = ActionChains(driver)
        submit = driver.find_element_by_link_text('搜索航班')
        action3.move_by_offset(0, 0).click().move_to_element(submit).click(submit).perform()

        # switch to the new window
        all_windows = driver.window_handles
        current_window = driver.current_window_handle
        for i in all_windows:
            if i != current_window:
                driver.switch_to.window(i)

        try:
            WebDriverWait(driver, 20, 0.5).until(EC.presence_of_element_located((By.CLASS_NAME, 'leaveFlight')))
        finally:
            print('New window''s elements Loaded.')

    finally:
        soup = BeautifulSoup(driver.page_source, 'html5lib')
        driver.quit()  # make sure the webdriver closed after use

    '''
    # 直接从页面进行解析
    fileName = 'KY_昆明-成都-2019-01-10.htm'
    filePath = 'D:/tmp/c/' + fileName
    html_file = open(filePath, 'r', encoding='utf-8')
    html_handle = html_file.read()
    soup = BeautifulSoup(html_handle, 'html5lib')
    '''

    # find all flights by class element
    l_flt = soup.find_all(class_='tt-de-node cf')
    l_price = soup.find_all(class_='tt-de-plusbox')
    result = []
    for i, flt in enumerate(l_flt):
        # summary title
        company = flt.find(class_='tt-de-air').find('strong').text
        fltno = flt.find(class_='f24').text

        # summary info
        dpt = flt.find_all(class_='tt-de-a2')[1].find_all('p')[1].text.strip()
        dptTime = flt.find_all(class_='tt-de-a2')[1].find('strong').text.strip()
        mid = ''  # 没有经停航线
        is_direct = flt.find_all(class_='tt-de-a3')[0].find_all('p')[1].text.strip().replace('-', '')
        arrv = flt.find_all(class_='tt-de-a2')[2].find_all('p')[1].text.strip()
        arvTime = flt.find_all(class_='tt-de-a2')[2].find('strong').text.strip().replace('\n', '').replace(' ', '')
        # 飞行时间
        flt_tm = flt.find_all(class_='tt-de-a3')[0].find_all('p')[0].text.strip().replace('\n', '').replace(' ', '')
        airplane_type = flt.find_all(class_='tt-de-a2')[0].find_all('p')[1].text.replace('机型', '').strip()

        # price detail
        price_list_meta = l_price[i].find_all(class_='cf')
        price_list = []
        for price_row in price_list_meta:
            price_class1 = price_row.find('strong').text.replace('\n', '').replace(' ', '')
            price_class = price_row.find_all('span')[0].text.replace('\n', '').replace(' ', '')
            d = price_row.find_all('span')[2].text.replace('\n', '').replace(' ', '').replace('折', '')
            discount = price_row.find_all('span')[2].text.replace('\n', '').replace(' ', '').replace('折', '')
            price_info = price_row.find(class_='f24 yellow2').text.replace('\n', '').replace(' ', '').replace('¥', '')\
                .replace(',', '')
            price_list.append((price_class1, price_class, discount, price_info))
            # print('-------price_list----:',price_list)

        # output
        result.append(
            dict(company=company, fltno=fltno, airplane_type=airplane_type, dpt=dpt, mid=mid, is_direct=is_direct,
                 dptTime=dptTime,arvTime=arvTime, arrv=arrv, flt_tm=flt_tm,  price_list=price_list))
    return result


if __name__ == '__main__':
    result = data_grabber_ky('昆明', '成都', '2019-01-10')
    for i in result:
        print(i)
