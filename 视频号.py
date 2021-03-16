# -*- coding: utf-8 -*-
import pickle
import agent
from threading import Thread
import time
import requests
from io import BytesIO
import os
from PIL import Image
import qrcode
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
    loginurl = session.post("https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_finder_list", data={"timestamp":int(time.time()*1000),"_log_finder_id":'null',"rawKeyBuff":'null'}, headers=headers).json()
    if loginurl['errCode'] == 0:
        print('Cookies值有效，',loginurl['data']['finderList'][0]['nickname'],'，已登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False


def sphlogin():
    # 写入
    session = requests.session()
    if not os.path.exists('sphcookies.cookie'):
        with open('sphcookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    # 读取
    session.cookies = pickle.load(open('sphcookies.cookie', 'rb'))
    session, status = islogin(session)
    if not status:
        loginurl = 'https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_login_code'
        urldata = session.post(loginurl, data={"timestamp":int(time.time() * 1000), "_log_finder_id": 'null', "rawKeyBuff": 'null'}, headers=headers).json()
        token = urldata['data']['token']
        pngurl = 'https://channels.weixin.qq.com/mobile/confirm.html?token={}'.format(token)
        qr = qrcode.QRCode()
        qr.add_data(pngurl)
        img = qr.make_image()
        a = BytesIO()
        img.save(a, 'png')
        png = a.getvalue()
        a.close()
        t = showpng(png)
        t.start()
        tokenurl = 'https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_login_status?token={}&timestamp={}'
        while 1:
            dataurl = session.post(tokenurl.format(token, int(time.time() * 1000)), headers=headers).json()
            if '0' in str(dataurl['data']['status']):
                print('二维码未失效，请扫码！')
            elif '5' in str(dataurl['data']['status']):
                print('已扫码，请确认！')
            elif '1' in str(dataurl['data']['status']):
                url = session.post('https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_finder_list', data={"timestamp": time.time() * 1000, "_log_finder_id": 'null', "rawKeyBuff": 'null'}, headers=headers).json()
                session.post('https://channels.weixin.qq.com/cgi-bin/mmfinderassistant-bin/auth/auth_set_finder', data={"finderUsername": url['data']['finderList'][0]['finderUsername'], "timestamp": int(time.time() * 1000), "_log_finder_id": 'null', "rawKeyBuff": 'null'}, headers=headers)
                print('已确认，登入成功！')
                break
            else:
                print('其他：', dataurl)
            time.sleep(2)
        with open('sphcookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    return session

if __name__ == '__main__':
    sphlogin()

