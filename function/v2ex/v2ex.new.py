import requests
import sys,time
import datetime
import re
import os
import pytz
from io import StringIO
sys.path.append("auto-actions/function/v2ex")
from serverchan_sdk import sc_send; 

# get os environ
SEND_KEY = os.environ.get('SENDKEY')
V2EX_TOKEN = os.environ.get('V2EX_TOKEN')

# initialize the notification
def notify(title, msg):
    """Send notification using serverchan."""
    if SEND_KEY:
        sc_send(sendkey=SEND_KEY,title=title, desp=msg, options={"tags": "Hifiti签到"})
    else:
        print(f"Title: {title}\nMessage: {msg}")
<<<<<<< HEAD
if V2EX_TOKEN:
  print(f"token: {V2EX_TOKEN}")
=======

# if V2EX_TOKEN:
#   print(f"token: {V2EX_TOKEN}")
>>>>>>> 605bee83a002ca7c5e636a688efcf73723520ca1

# 初始化日志
sio = StringIO('签到日志\n')
sio.seek(0, 2)  # 将读写位置移动到结尾
s = requests.session()
tz = pytz.timezone('Asia/Shanghai')
nowtime = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
sio.write("--------------------------" + nowtime + "----------------------------\n")


# 初始化变量
ckstatus = 0
signstatus = 0
notice = ""
once = None


# Initialize session
s = requests.session()
host = "www.v2ex.com"
# Define headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Referer": f"https://{host}/mission/daily",
    "Host": f"{host}",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Connection": "keep-alive",
}
s.headers.update(headers)
s.cookies.update({'A2': f"{V2EX_TOKEN}"})
s.headers.update({'V2EX_LANG': 'zhcn'})


# 获取once检查是否已签到
def check():
    global ckstatus, notice, once, signstatus, s, host
    try:
        sio.write("Checking if already signed in...\n")
        url = f"https://{host}/mission/daily"
        res = s.get(url)
        reg1 = re.compile(r"需要先登录")
        if reg1.search(res.text):
            sio.write("cookie失效\n")
            ckstatus = 0
            notice += "cookie失效"
            if SEND_KEY:
                # 假设notify是自定义通知模块，这里需实现具体逻辑
                # notify("V2ex自动签到", notice)
                pass
            return
        else:
            reg = re.compile(r"每日登录奖励已领取")
            if reg.search(res.text):
                notice += "今天已经签到过啦\n"
                signstatus = 1
            else:
                reg = re.compile(r"redeem\?once=(.*?)'")
                match = reg.search(res.text)
                if match:
                    once = match.group(1)
                    sio.write(f"获取成功 once:{once}\n")
    except Exception as err:
      sio.write(f"签到异常-check: {err}\n")

# 每日签到
def daily():
    global signstatus, notice, once, s, host
    try:
        sio.write(f"Check-in in with once: {once}\n")
        url = f"https://{host}/mission/daily/redeem?once={once}"
        sio.write(f"签到链接: {url}\n")
        res = s.get(url)
        reg = re.compile(r"已成功领取每日登录奖励")
        if reg.search(res.text):
            notice += "签到成功\n"
            signstatus = 1
        else:
            reg = re.compile(r"请重新点击一次以领取每日登录奖励")
            if reg.search(res.text):
                notice += "Message提示：请重新点击一次以领取每日登录奖励\n"
                signstatus = 0
                sio.write("Message提示：请重新点击一次以领取每日登录奖励\n")
            else:
                notice += "签到失败Cookie疑似失效\n"
                signstatus = 0
                sio.write("签到失败Cookie疑似失效\n")
    except Exception as err:
      sio.write(f"签到异常-daily: {err}\n")

# 查询余额
def balance():
    global notice, s, host
    try:
        sio.write("Checking balance...\n")
        url = f"https://{host}/balance"
        res = s.get(url)
        reg = re.compile(r"\d+?\s的每日登录奖励\s\d+\s铜币")
        match = reg.search(res.text)
        if match:
            sio.write(f"余额查询成功: {match.group(0)}\n")
            notice += match.group(0)
        else:
            sio.write("余额查询失败\n")
            notice += "余额查询失败\n"
    except Exception as err:
      sio.write(f"签到异常-balance: {err}\n")

# 签到主函数
def main():
    global once, signstatus, s, host
    try:
        if not V2EX_TOKEN:
            sio.write("你的cookie呢!!!\n获取V2EX数据失败, cookie未定义\n")
            notify(title="V2EX签到失败", msg="获取V2EX数据失败, cookie未定义")
            # 返回前打印日志
            print(sio.getvalue())
            return
        check()
        time.sleep(1)  # 等待1秒以确保请求完成
        if once and signstatus == 0:
            daily()
            balance()
            if signstatus == 0:
                sio.write("签到失败Cookie疑似失效\n")
                sio.write(f"headers: { str(s.headers) }\n")
                sio.write(f"cookie: { s.cookies.get_dict() }\n")
        sio.write(f"签到状态: {signstatus}\n消息: {notice}\n")
        notify(title="V2ex自动签到", msg=notice)
        #print("Cookie:", s.cookies.get_dict())
        pass
    except Exception as err:
        sio.write(f"签到异常-main: {err}\n")

    # 输出日志
    print(sio.getvalue())
    print("签到完成")


if __name__ == '__main__':
    main()
