import requests
import time
import json
import sys
import datetime
import re
import os
import pytz
from io import StringIO
sys.path.append("auto-actions/function/v2ex")
from serverchan_sdk import sc_send; 

if os.environ['SendKey'] != "":
    SEND_KEY = os.environ['SendKey']

if os.environ.get('V2EX_COOKIE'):
    V2EX_COOKIE = os.environ['V2EX_COOKIE']

# initialize the notification class
def notify(title, msg):
    # Server酱
    if SEND_KEY:
        response = sc_send(SEND_KEY, title, msg, {"tags": "V2EX签到"})
        print(response)

# 初始化日志
sio = StringIO('WPS签到日志\n\n')
sio.seek(0, 2)  # 将读写位置移动到结尾
s = requests.session()
tz = pytz.timezone('Asia/Shanghai')
nowtime = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
sio.write("--------------------------" + nowtime + "----------------------------\n\n")


# 初始化变量
ckstatus = 0
signstatus = 0
notice = ""
once = None

# 定义请求头
header = {
    "Referer": "https://www.v2ex.com/mission",
    "Host": "www.v2ex.com",
    "user-agent": "Mozilla/5.0 (Linux; Android 10; Redmi K30) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.83 Mobile Safari/537.36",
    "cookie": f"'{V2EX_COOKIE}'"
}

# 获取once检查是否已签到
def check():
    global ckstatus, notice, once, signstatus
    try:
        url = "https://www.v2ex.com/mission/daily"
        res = requests.get(url, headers=header)
        reg1 = re.compile(r"需要先登录")
        if reg1.search(res.text):
            print("cookie失效")
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
                    print(f"获取成功 once:{once}")
    except Exception as err:
        print(err)

# 每日签到
def daily():
    global signstatus, notice, once
    try:
        url = f"https://www.v2ex.com/mission/daily/redeem?once={once}"
        res = requests.get(url, headers=header)
        reg = re.compile(r"已成功领取每日登录奖励")
        if reg.search(res.text):
            notice += "签到成功\n"
            signstatus = 1
        else:
            notice += "签到失败Cookie疑似失效\n"
            signstatus = 0
            print("签到失败Cookie疑似失效")
    except Exception as err:
        print(err)

# 查询余额
def balance():
    global notice
    try:
        url = "https://www.v2ex.com/balance"
        res = requests.get(url, headers=header)
        reg = re.compile(r"\d+?\s的每日登录奖励\s\d+\s铜币")
        match = reg.search(res.text)
        if match:
            print(match.group(0))
            notice += match.group(0)
    except Exception as err:
        print(err)

# 签到主函数
def main():
    global once, signstatus
    try:
        if not V2EX_COOKIE:
            print("你的cookie呢!!!")
            sio.write("获取V2EX数据失败, cookie未定义\n")
            notify(title="V2EX签到失败", msg="获取V2EX数据失败, cookie未定义")
            return
        check()
        if once and signstatus == 0:
            daily()
            balance()
            if signstatus == 0:
                print("签到失败Cookie疑似失效")
        print(notice)
        if SEND_KEY:
            # 假设notify是自定义通知模块，这里需实现具体逻辑
            notify(title="V2ex自动签到", msg=notice)
            pass
    except Exception as err:
        print(err)

if __name__ == '__main__':
    main()