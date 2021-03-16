import time

from requests.cookies import RequestsCookieJar
import json
import requests
import http.cookiejar as cookielib

headers = {
  'authority': 'weibo.com',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'x-requested-with': 'XMLHttpRequest',
  'sec-ch-ua-mobile': '?0',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  'content-type': 'application/x-www-form-urlencoded',
  'accept': '*/*',
  'origin': 'https://weibo.com',
  'sec-fetch-site': 'same-origin',
  'sec-fetch-mode': 'cors',
  'sec-fetch-dest': 'empty',
  'referer': 'https://weibo.com/u/3154059850/home?topnav=1&wvr=6&mod=logo',
  'accept-language': 'zh-CN,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7,en;q=0.6',
}

if __name__ == '__main__':
    session = requests.session()
    session.cookies = cookielib.LWPCookieJar('wbcookies1.txt')
    session.cookies.load(ignore_discard=True)
    # session.cookies.load('wbcookies1.txt')
    session.get(url='https://weibo.com/3154059850/profile?profile_ftype=1&is_all=1#_0',headers=headers)
    url = "https://weibo.com/aj/mblog/add?ajwvr=6&__rnd=1615792663411"

    payloa = 'location=v6_content_home&text=123&appkey=&style_type=1&pic_id=&tid=&pdetail=&mid=&isReEdit=false&rank=0&rankid=&module=stissue&pub_source=main_&pub_type=dialog&isPri=0&_t=0'

    response = session.post( url=url, headers=headers, data=payload)
    # response = session.get( url='https://weibo.com/3154059850/profile?rightmod=1&wvr=6&mod=personnumber&is_all=1', headers=headers)
    #
    print(response.text)

