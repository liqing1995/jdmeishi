import re
import time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo

from config import *


client= pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

browser = webdriver.Chrome()
wait = WebDriverWait(browser, 300)


'''def login():
    browser.get(
        'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9QlW8bO&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F')
    browser.implicitly_wait(30)
    submit = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_QRCodeLogin > div.login-links > a.forget-pwd.J_Quick2Static'))
    )
    submit.click()
    ursename = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#TPL_username_1"))
    )
    ursename.send_keys("")
    password = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#TPL_password_1"))
    )
    password.send_keys("")
    logins = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_SubmitStatic"))
    )
    input = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#q"))
    )
    input.send_keys('美食')
    submit.click()
'''


def search():
    try:
        browser.get('https://www.jd.com/')
        # 缓冲
        # browser.implicitly_wait(30)
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#key'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#search > div > div.form > button > i"))
        )
        input.send_keys(KEYWOED)
        submit.click()
        total = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > em:nth-child(1) > b"))
        )
        time.sleep(100)
        get_products()
        return total.text
    except TimeoutException:
        # pass
        return search()  # 从新请求一次


def next_page(page_number):
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#J_bottomPage > span.p-skip > input'))
        )
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#J_bottomPage > span.p-skip > a"))
        )
        input.clear()
        input.send_keys(page_number)
        submit.click()
        wait.until(
            EC.text_to_be_present_in_element((By.CSS_SELECTOR, "#J_bottomPage > span.p-num > a.curr"), str(page_number))
        )
        time.sleep(100)
        get_products()
    except TimeoutException:
        next_page(page_number)


def get_products():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#J_goodsList .gl-warp .gl-item")))
    html = browser.page_source
    doc = pq(html)
    items = doc('#J_goodsList .gl-warp .gl-item').items()
    for item in items:

        product = {
            'image': item.find('.p-img  .img').attr('source-data-lazy-img'),
            'href': item.find('.p-img  ._blank  .a').attr.href,
            'price': item.find('.p-price').text(),
            'title': item.find('.p-name').text(),
            'shop': item.find('.p-shop').text(),
            'commit': item.find('.p-commit').text()[:-3]
        }
        print(product)
        save_to_mongo(product)


def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print('储存到MONGODB成功 ', result)
    except Exception:
        print('储存到MONGODB失败', result)


def main():
    try:
        total = search()
        total = int(re.compile('(\d+)').search(total).group(1))
        for i in range(2, total + 1):
            time.sleep(100)
            next_page(i)
    except Exception:
        print('出错啦')
    finally:
        browser.close()


if __name__ == '__main__':
    main()
