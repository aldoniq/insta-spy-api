import json
import re
import requests
from bs4 import BeautifulSoup

from datetime import datetime


    
def getCookies(cookie_jar, domain):
    cookie_dict = cookie_jar.get_dict(domain=domain)
    found = ['%s=%s' % (name, value) for (name, value) in cookie_dict.items()]
    return ';'.join(found)

def authInsta(username: str, password: str) -> dict:
    link = 'https://www.instagram.com/accounts/login/'
    login_url = 'https://www.instagram.com/accounts/login/ajax/'

    res = {}
    time = int(datetime.now().timestamp())

    payload = {
        'username': username,
        'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{time}:{password}',  # <-- note the '0' - that means we want to use plain passwords
        'queryParams': {},
        'optIntoOneTap': 'false'
    }

    with requests.Session() as s:
        r = s.get(link)
        csrf = re.findall(r"csrf_token\":\"(.*?)\"",r.text)[0]
        r = s.post(login_url,data=payload,headers={
            "user-agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36",
            "x-requested-with": "XMLHttpRequest",
            "referer": "https://www.instagram.com/accounts/login/",
            "x-csrftoken":csrf
        })
        print(r.status_code)
        print(r.text)
        cookit = getCookies(r.cookies, ".instagram.com")
        usrid = json.loads(r.text)['userId']
        res['cookies'] = cookit
        res['id'] = usrid
        print(cookit)
        print(usrid)

    return res




def getId(username: str, cookies: str) -> str:
    print(username)
    res = ''
    getIdUrl = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    
    r = requests.get(getIdUrl,headers={
            "authority": "i.instagram.com",
            "method": "GET",
            "path": f"/api/v1/users/web_profile_info/?username={username}",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "macOS",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Mobile/15D100 Instagram 37.0.0.9.96 (iPhone7,2; iOS 11_2_6; pt_PT; pt-PT; scale=2.34; gamut=normal; 750x1331)",
            "cookie": cookies
        })
    print(r.status_code)
    if r.status_code == 404:
        res = None
    elif r.status_code == 200:
        
        if json.loads(r.text)['data']['user'] is None:
            res = None
        else:
            res = json.loads(r.text)['data']['user']['id']

    return res


def getStories(user: str, cookies: str) -> str:
    res = {}
    getStoryUrl = f"https://i.instagram.com/api/v1/feed/user/{user}/story/"

    r =  requests.get(getStoryUrl,headers={
            "authority": "i.instagram.com",
            "method": "GET",
            "path": f"/api/v1/feed/user/{user}/story/",
            "scheme": "https",
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "sec-ch-ua": '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "macOS",
            "user-agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 11_2_6 like Mac OS X) AppleWebKit/604.5.6 (KHTML, like Gecko) Mobile/15D100 Instagram 37.0.0.9.96 (iPhone7,2; iOS 11_2_6; pt_PT; pt-PT; scale=2.34; gamut=normal; 750x1331)",
            "cookie": cookies
        })
    response = json.loads(r.text)['reel']
    if response:
        res["user"] = {
            "username" : response["user"]["username"],
            "photo": response["user"]["profile_pic_url"] or None,
        }
        res["stories"] = []
        for i in response['items']:
            if 'video_versions' in i:
                for j in i['video_versions']:
                    if j['type'] == 101:
                        res['stories'].append(j['url'])
                        break
            else:
                res["stories"].append(i['image_versions2']['candidates'][0]['url'])

        return res
    else:
        return {}
