# -*- coding: utf-8 -*-
import pickle
from urllib import parse
import re
import random
import agent
from threading import Thread
import time
import requests
from io import BytesIO
from PIL import Image
import os
requests.packages.urllib3.disable_warnings()
headers = {'User-Agent': agent.get_user_agents(), "Host": "ssl.ptlogin2.qq.com", 'Referer':'https://xui.ptlogin2.qq.com/'}

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
    loginurl = session.post('https://media.weishi.qq.com/media-api/getPersonalInfo?data=%7B%22personId%22%3A%221570763357553271%22%7D').json()
    if loginurl['code'] == 0:
        print('Cookies值有效，无需扫码登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False


def wslogin():
    # 写入
    session = requests.session()
    if not os.path.exists('wscookies.cookie'):
        with open('wscookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    # 读取
    session.cookies = pickle.load(open('wscookies.cookie', 'rb'))
    session, status = islogin(session)
    if not status:
        loginsig = session.get(
            'https://xui.ptlogin2.qq.com/cgi-bin/xlogin?appid=716027609&daid=383&style=33&theme=2&login_text=%E6%8E%88%E6%9D%83%E5%B9%B6%E7%99%BB%E5%BD%95&hide_title_bar=1&hide_border=1&target=self&s_url=https%3A%2F%2Fgraph.qq.com%2Foauth2.0%2Flogin_jump&pt_3rd_aid=1101083114&pt_feedback_link=https%3A%2F%2Fsupport.qq.com%2Fproducts%2F77942%3FcustomInfo%3D.appid1101083114')
        loginsig = loginsig.cookies.get_dict()['pt_login_sig']
        loginurl = session.get(
            'https://ssl.ptlogin2.qq.com/ptqrshow?appid=716027609&e=2&l=M&s=3&d=72&v=4&t={}&daid=383&pt_3rd_aid=1101083114'.format(
                random.random()), headers=headers)
        qrsig = loginurl.cookies.get_dict()['qrsig']
        # 方法1
        ptqrtoken = agent.ptqrtoken(qrsig)
        # 方法2
        # ptqrtoken = execjs.compile('''function s(t){for(var e=0,i=0,n=t.length;i<n;++i){e+=(e<<5)+t.charCodeAt(i)}return 2147483647&e};''').call('s', qrsig)
        tokenurl = 'https://ssl.ptlogin2.qq.com/ptqrlogin?u1=https%3A%2F%2Fgraph.qq.com%2Foauth2.0%2Flogin_jump&ptqrtoken={}&ptredirect=0&h=1&t=1&g=1&from_ui=1&ptlang=2052&action=0-0-{}&js_ver=21010623&js_type=1&login_sig={}&pt_uistyle=40&aid=716027609&daid=383&pt_3rd_aid=1101083114&'
        t = showpng(loginurl.content)
        t.start()
        while 1:
            tokendate = session.get(tokenurl.format(ptqrtoken, int(time.time() * 1000), loginsig), headers=headers)
            p = re.compile("ptuiCB\('(.*)','(.*)','(.*)','(.*)','(.*)',.*\)")
            ret = p.search(tokendate.text).groups()
            if ret[0] == "66":
                print('二维码未失效，请扫码！')
            elif ret[0] == "67":
                print('已扫码，请确认！')
            elif ret[0] == "65":
                print('二维码已失效，请重新运行！')
            if ret[0] == '0':
                print('已确认，登录成功！')
                ui = agent.guid()
                session.get(ret[2])
                p_skey = session.cookies.get('p_skey')
                g_tk = agent.get_g_tk(p_skey)
                payload = {'response_type': 'code', 'client_id': '1101083114',
                           'redirect_uri': 'https://h5.weishi.qq.com/weishi/account/login?r_url=http%3A%2F%2Fmedia.weishi.qq.com%2F&loginfrom=qc',
                           'scope': '', 'state': 'state', 'switch': '', 'from_ptlogin': '1', 'src': '1',
                           'update_auth': '1', 'openapi': '80901010', 'g_tk': g_tk,
                           'auth_time': int(time.time() * 1000), 'ui': ui}
                urlencode = parse.urlencode(payload)
                date = session.post('https://graph.qq.com/oauth2.0/authorize', data=urlencode).url
                pattern = re.compile(r'[A-Za-z0-9]{16,}')
                code = pattern.findall(date)[0]
                session.get(
                    'https://h5.weishi.qq.com/weishi/account/login?r_url=http%3A%2F%2Fmedia.weishi.qq.com%2F&loginfrom=qc&code={}&state=state'.format(
                        code))
                break
            time.sleep(3)
        with open('wscookies.cookie', 'wb') as f:
            pickle.dump(session.cookies, f)
    return session

if __name__ == '__main__':
    wslogin()


