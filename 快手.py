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

headers = {'User-Agent': agent.get_user_agents()}


class showpng(Thread):
    def __init__(self, data):
        Thread.__init__(self)
        self.data = data

    def run(self):
        img = Image.open(BytesIO(self.data))
        img.show()


def islogin(session):
    try:
        session.cookies.load(ignore_discard=True)
    except Exception:
        pass
    loginurl = session.post("https://cp.kuaishou.com/rest/pc/authority/account/current", json={"kuaishou.web.cp.api_ph": "2ab04b8a59d843e385faa6a4965f0836f53f"}, verify=False, headers=headers).json()
    if loginurl['result'] == 1:
        print('Cookies值有效，无需扫码登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False


def kslogin():
    if not os.path.exists('kscookies.txt'):
        with open("kscookies.txt", 'w') as f:
            f.write("")
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='kscookies.txt')
    session, status = islogin(session)
    if not status:
        loginurl = 'https://id.kuaishou.com/rest/c/infra/ks/qr/start'
        urldata = session.post(loginurl, data={"sid": "kuaishou.web.cp.api"}, headers=headers).json()
        testpng = base64.b64decode(urldata['imageData'])
        token = urldata['qrLoginToken']
        Signat = urldata['qrLoginSignature']
        t = showpng(testpng)
        t.start()
        tokenurl = 'https://id.kuaishou.com/rest/c/infra/ks/qr/scanResult'
        while 1:
            tokendate = session.post(tokenurl, data={"qrLoginToken": token, "qrLoginSignature": Signat}, headers=headers).json()
            if tokendate['result'] == 707:
                print('登录二维码已过期，请重新运行！')
            if tokendate['result'] == 1:
                date = session.post('https://id.kuaishou.com/rest/c/infra/ks/qr/acceptResult', data={"qrLoginToken": token, "qrLoginSignature": Signat, "sid": "kuaishou.web.cp.api"}, headers=headers)
                date1 = session.post('https://id.kuaishou.com/pass/kuaishou/login/qr/callback', data={"qrToken": date.json()['qrToken'], "sid": "kuaishou.web.cp.api"}, headers=headers)
                session.post('https://www.kuaishou.com/account/login/api/verifyToken', json={"authToken": date1.json()['kuaishou.web.cp.api.at'], "sid": "kuaishou.web.cp.api"}, headers=headers)
                print('已确认，登录成功！')
                break
            time.sleep(3)
        session.cookies.save()
    return session


if __name__ == '__main__':
    kslogin()
