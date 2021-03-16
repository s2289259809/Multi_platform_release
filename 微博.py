# -*- coding: utf-8 -*-
import json
import re
import agent
from threading import Thread
import time
import requests
from io import BytesIO
import http.cookiejar as cookielib
from PIL import Image
import os

requests.packages.urllib3.disable_warnings()

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36', 'Referer': "https://weibo.com/"}


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
    loginurl = session.get(
        "https://account.weibo.com/set/aj/iframe/schoollist?province=11&city=&type=1&_t=0&__rnd={}".format(
            int(time.time() * 1000)), headers=headers).json()['code']
    if loginurl == '100000':
        print('Cookies值有效，无需扫码登录！')
        return session, True
    else:
        print('Cookies值已经失效，请重新扫码登录！')
        return session, False


def wblogin():
    if not os.path.exists('wbcookies.txt'):
        with open("wbcookies.txt", 'w') as f:
            f.write("")
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar(filename='wbcookies.txt')
    session, status = islogin(session)
    if not status:
        loginurl = 'https://login.sina.com.cn/sso/qrcode/image?entry=weibo&size=180&callback=STK_{}'
        texturl = session.get(loginurl.format(int(time.time() * 1000), headers=headers)).text
        xx = re.search("window.STK_\d+.\d+ && STK_\d+.\d+\(?", texturl)
        x = json.loads(texturl.strip().lstrip(xx.group()).rstrip(");"))
        qrid = x['data']['qrid']
        image = x['data']['image']
        imageurl = session.get('https:' + image, headers=headers).content
        t = showpng(imageurl)
        t.start()
        qridurl = 'https://login.sina.com.cn/sso/qrcode/check?entry=weibo&qrid={}&callback=STK_{}'
        while 1:
            dateurl = session.get(qridurl.format(qrid, int(time.time() * 1000), headers=headers)).text
            xx = re.search("window.STK_\d+.\d+ && STK_\d+.\d+\(?", dateurl)
            x = json.loads(dateurl.strip().lstrip(xx.group()).rstrip(");"))
            retcode = x['retcode']
            if '50114001' in str(retcode):
                print('二维码未失效，请扫码！')
            elif '50114002' in str(retcode):
                print('已扫码，请确认！')
            elif '50114004' in str(retcode):
                print('二维码已失效，请重新运行！')
            elif '20000000' in str(retcode):
                alt = x['data']['alt']
                alturl = 'https://login.sina.com.cn/sso/login.php?entry=weibo&returntype=TEXT&crossdomain=1&cdult=3&domain=weibo.com&alt={}&savestate=30&callback=STK_{}'.format(
                    alt, int(time.time() * 100000))
                crossDomainUrl = session.get(alturl, headers=headers).text
                pp = re.search("STK_\d+\(?", crossDomainUrl)
                p = json.loads(crossDomainUrl.strip().lstrip(pp.group()).rstrip(");"))
                crossDomainUrlList = p['crossDomainUrlList']
                session.get(crossDomainUrlList[0], headers=headers)
                session.get(crossDomainUrlList[1] + '&action=login', headers=headers)
                session.get(crossDomainUrlList[2], headers=headers)
                session.get(crossDomainUrlList[3], headers=headers)
                # session.cookies.save('wbcookies1.txt')
                print('已确认，登录成功！')
                break
            else:
                print('其他情况', retcode)
            time.sleep(5)
        session.cookies.save()
    return session


if __name__ == '__main__':
    wblogin()
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar('wbcookies1.txt')
    session.cookies.load(ignore_discard=True)
    # session.cookies.load('wbcookies1.txt')
    session.get(url='https://weibo.com/3154059850/profile?profile_ftype=1&is_all=1#_0', headers=headers)
    url = "https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=1615792663411"

    payload = 'location=v6_content_home&text=123&appkey=&style_type=1&pic_id=&tid=&pdetail=&mid=&isReEdit=false&rank=0&rankid=&module=stissue&pub_source=main_&pub_type=dialog&isPri=0&_t=0'

    response = session.post(url=url, headers=headers, data=payload)
    # response = session.get( url='https://weibo.com/3154059850/profile?rightmod=1&wvr=6&mod=personnumber&is_all=1', headers=headers)
    #
    print(response.text)
