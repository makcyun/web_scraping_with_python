
"""
模拟登录的几种方法
https://blog.csdn.net/hui1788/article/details/79944102

1 POST 直接请求，较麻烦

2 先登录获取cookie，get 请求，最方便

3 selenium 输入账号密码，比较慢

"""

def method1():
    import requests

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }

    data = {
        'identity': 'irw27812@awsoo.com',
        'password': 'test2018',
    }
    url = 'https://www.itjuzi.com/user/login?redirect=&flag=&radar_coupon='

    session = requests.Session()
    session.post(url, headers=headers, data=data)
    response = session.get('http://radar.itjuzi.com/investevent', headers=headers)

    print(response.status_code)
    print(response.text)

"""


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# method2
"""
import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    'Cookie':'_ga=GA1.2.1593763832.1537967405; gr_user_id=dbcfdc03-7797-4da5-977b-29efb03b47c2; MEIQIA_EXTRA_TRACK_ID=19gP05ZILu5SO9KSt4Dy6fBVQPz; acw_tc=76b20f4815407722861481456ecdee420103495231bd76dce3f6fcded878c8; _gid=GA1.2.456657790.1540772307; Hm_lvt_1c587ad486cdb6b962e94fc2002edf89=1540089239,1540104038,1540213198,1540772308; MEIQIA_VISIT_ID=1CE6Dj0otMoirY1t8rnGzE8H47O; gr_session_id_eee5a46c52000d401f969f4535bdaa78=0a27f831-57b5-4a97-a64a-d2f04dc7d140; gr_session_id_eee5a46c52000d401f969f4535bdaa78_0a27f831-57b5-4a97-a64a-d2f04dc7d140=true; session=429b5f2eff16369e4243ab58741e7e370221530d; identity=fru68354%40nbzmr.com; remember_code=I0iyUGuvfW; unique_token=655841; Hm_lpvt_1c587ad486cdb6b962e94fc2002edf89=1540780178'
}

session = requests.Session()
response = session.get('http://radar.itjuzi.com/investevent', headers=headers)

print(response.status_code)
print(response.text)

"""
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# method3
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

browser = webdriver.Chrome()
browser.maximize_window()  # 最大化窗口
wait = WebDriverWait(browser, 10)

def login():
    browser.get('https://www.itjuzi.com/user/login')
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="create_account_email"]')))
    input.send_keys('irw27812@awsoo.com')
    input = wait.until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="create_account_password"]')))
    input.send_keys('test2018')
    submit = wait.until(EC.element_to_be_clickable(
        (By.XPATH, '//*[@id="login_btn"]')))
    submit.click()
    get_page_index()

def get_page_index():
    browser.get('http://radar.itjuzi.com/investevent')
    try:
        print(browser.page_source)  # 查看网页源码
    except Exception as e:
        print(str(e))

login()

"""