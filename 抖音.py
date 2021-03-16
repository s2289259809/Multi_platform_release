# -*- coding: utf-8 -*-
import base64
import agent
from threading import Thread
import time
import requests
from io import BytesIO
import http.cookiejar as cookielib
from PIL import Image
import os

requests.packages.urllib3.disable_warnings()

headers = {'User-Agent': agent.get_user_agents(), 'Referer': "https://creator.douyin.com/"}

#为确保打开二维码还能继续运行
class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        img = Image.open(BytesIO(self.data))
        img.show()

#判断cookies值是否失效
def islogin(session):
    loginurl = "https://creator.douyin.com/web/api/media/user/info/"
    try:
        session.cookies.load(ignore_discard=True)
    except Exception:
        pass
    response = session.get(loginurl, verify=False, headers=headers)
    if response.json()['status_code'] == 0:
        print('Cookies值有效，无需扫码登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False

#获取cookies值
def dylogin():
    #将获取的cookies值进行文本保存
    if not os.path.exists('cookies.txt'):
        with open("cookies.txt", 'w') as f:
            f.write("")
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='cookies.txt')
    session, status = islogin(session)
    if not status:
        loginurl = "https://sso.douyin.com/get_qrcode/?next=https:%2F%2Fcreator.douyin.com%2Fcontent%2Fmanage&aid=2906&service=https:%2F%2Fcreator.douyin.com&is_vcd=1&fp=kj5j6uhv_tvKYUFA0_qzgZ_4l9c_9Amt_DCywEfwbVFCJ"
        urldata = session.get(loginurl, headers=headers).json()
        testpng = base64.b64decode(urldata['data']['qrcode'])
        t = showpng(testpng)
        t.start()
        token = urldata['data']['token']
        tokenurl = 'https://sso.douyin.com/check_qrconnect/?next=https:%2F%2Fcreator.douyin.com%2Fcontent%2Fmanage&token={}&service=https:%2F%2Fcreator.douyin.com%2F%3Flogintype%3Duser%26loginapp%3Ddouyin%26jump%3Dhttps:%2F%2Fcreator.douyin.com%2Fcontent%2Fmanage&correct_service=https:%2F%2Fcreator.douyin.com%2F%3Flogintype%3Duser%26loginapp%3Ddouyin%26jump%3Dhttps:%2F%2Fcreator.douyin.com%2Fcontent%2Fmanage&aid=2906&is_vcd=1&fp=kj5j6uhv_tvKYUFA0_qzgZ_4l9c_9Amt_DCywEfwbVFCJ'.format(
            token)
        while 1:
            qrcodedata = session.get(tokenurl, headers=headers).json()
            if qrcodedata['data']['status'] == "1":
                print('二维码未失效，请扫码！')
            elif qrcodedata['data']['status'] == "2":
                print('已扫码，请确认！')
            elif qrcodedata['data']['status'] == "5":
                print('二维码已失效，请重新运行！')
            if qrcodedata['data']['status'] == "3":
                print('已确认，登录成功！')
                session.get(qrcodedata['data']['redirect_url'], headers=headers)
                break
            time.sleep(5)
        session.cookies.save()
    return session


if __name__ == '__main__':
    dylogin()

