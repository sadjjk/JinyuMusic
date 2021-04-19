# 已废弃 不需要登录获取Cookies

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import json
import os

PHONE_NUMBER = 'xxxx'
PASSWORD = 'XXX'

if __name__ == '__main__':

    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migu_cookies')
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://music.migu.cn/v3')
    actions = ActionChains(driver)
    touxiang = driver.find_element_by_xpath('//div[@id="J-user-info"]//img[@class="default-avatar"]')
    actions.move_to_element(touxiang).perform()
    denglu = driver.find_element_by_xpath('//div[@class="user-info-action"]/a[@id="J-popup-login"]')
    denglu.click()
    driver.switch_to.frame('loginIframe53645')
    mimadenglu = driver.find_element_by_xpath(
        '//div[@class="form-login J_FormLogin formLoginW"]//li[@class="accountLg"]')
    mimadenglu.click()

    shouji1 = driver.find_element_by_xpath('//*[@id="J_AccountPsd"]')
    shouji1.send_keys(PHONE_NUMBER)

    mima = driver.find_element_by_xpath(
        '//div[@class="form-item"]/input[@class="txt J_NoTip J_DelectIcon J_PwPsd"]')
    mima.send_keys(PASSWORD)

    submit = driver.find_element_by_xpath('/html/body/div[2]/div[1]/form[2]/div/div[5]/input')
    submit.click()

    time.sleep(2)

    cookies = driver.get_cookies()
    cookies_dict = {}
    for i in cookies:
        cookies_dict[i['name']] = i['value']
    with open(file_path, 'w') as f:
        f.write(json.dumps(cookies_dict))

    print('Cookies保存成功')
