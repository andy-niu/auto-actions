import requests, json,time,hashlib,os, sys
from serverchan_sdk import sc_send
sys.path.append("auto-actions/function/v2ex")

# zdm_cookie
SMZDM_COOKIE = os.getenv("SMZDM_COOKIE")
SEND_KEY = os.environ.get('SENDKEY')

# initialize the notification
def notify(title, msg):
    """Send notification using serverchan."""
    if SEND_KEY:
        sc_send(sendkey=SEND_KEY,title=title, desp=msg, options={"tags": "Hifiti签到"})
    else:
        print(f"Title: {title}\nMessage: {msg}")

def checkin():
  try:
    if SMZDM_COOKIE is None:
      print("没有填写SMZDM_COOKIE，跳过签到")
      notify("什么值得买签到失败","没有填写SMZDM_COOKIE，跳过签到")
      return
    
    print(f'开始签到')
    ts =int(round(time.time() * 1000))
    url = 'https://user-api.smzdm.com/robot/token'
    headers = {
        'Host': 'user-api.smzdm.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'{SMZDM_COOKIE}',
        'User-Agent': 'smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp',
    }
    data={
        "f":"android",
        "v":"10.4.1",
        "weixin":1,
        "time":ts,
        "sign":hashlib.md5(bytes(f'f=android&time={ts}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',encoding='utf-8')).hexdigest().upper()
    }
    html = requests.post(url=url, headers=headers, data=data)
    result = html.json()
    #print(f'获取result成功: {result}')
    token= result['data']['token']

    Timestamp =int(round(time.time() * 1000))
    data={
        "f":"android",
        "v":"10.4.1",
        "sk":"ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L",
        "weixin":1,
        "time":Timestamp,
        "token":token,
        "sign":hashlib.md5(bytes(f'f=android&sk=ierkM0OZZbsuBKLoAgQ6OJneLMXBQXmzX+LXkNTuKch8Ui2jGlahuFyWIzBiDq/L&time={Timestamp}&token={token}&v=10.4.1&weixin=1&key=apr1$AwP!wRRT$gJ/q.X24poeBInlUJC',encoding='utf-8')).hexdigest().upper()
    }
    url = 'https://user-api.smzdm.com/checkin'
    url2 = 'https://user-api.smzdm.com/checkin/all_reward'
    headers = {
        'Host': 'user-api.smzdm.com',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': f'{SMZDM_COOKIE}',
        'User-Agent': 'smzdm_android_V10.4.1 rv:841 (22021211RC;Android12;zh)smzdmapp',
    }
    html = requests.post(url=url, headers=headers, data=data)
    html2 = requests.post(url=url2, headers=headers, data=data)
    result = json.loads(html.text)['error_msg']
    result2 = json.loads(html2.text)
    print(result)
    print(result2)
    
    print(f'签到成功')
    notify("什么值得买签到成功",f"签到结果: {result}, 额外奖励: {result2}")

  except Exception as e:
    print(f"获取SMZDM_COOKIE失败，跳过签到: {e}")
    notify("什么值得买签到失败",f"获取SMZDM_COOKIE失败，跳过签到: {e}")
    return
  

def main():
  checkin()


if __name__ == "__main__":
  main()