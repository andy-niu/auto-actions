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
V2EX_TOKEN = os.environ.get('V2EX_COOKIE')

# initialize the notification
def notify(title, msg):
    """Send notification using serverchan."""
    if SEND_KEY:
        sc_send(sendkey=SEND_KEY,title=title, desp=msg, options={"tags": "Hifiti签到"})
    else:
        print(f"Title: {title}\nMessage: {msg}")

class V2EXClient:
    def __init__(self, token):
        self.token = token
        self.host = "www.v2ex.com"
        self.session = requests.session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Referer": f"https://{self.host}/mission/daily",
            "Host": f"{self.host}",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Connection": "keep-alive"
        }
        self.session.cookies.clear()

        # self.session.cookies.update({'A2': self.token})
        # self.session.cookies.update({'V2EX_LANG': 'zhcn'})
        
        # 解析并添加 Cookie
        cookies = {}
        for cookie in V2EX_TOKEN.split(';'):
            if cookie.strip():
                key, value = cookie.strip().split('=', 1)
                cookies[key] = value

        # 将解析后的 Cookie 添加到 Session
        self.session.cookies.update(cookies)
        
        self.once = None
        self.signstatus = 0
        self.notice = ""
        
        
    def check(self, sio):
        try:
            sio.write("Checking if already signed in...\n")
            url = f"https://{self.host}/mission/daily"
            res = self.session.get(url)
            reg1 = re.compile(r"需要先登录")
            if reg1.search(res.text):
                sio.write("cookie失效\n")
                self.notice += "cookie失效"
                return False
            else:
                reg = re.compile(r"每日登录奖励已领取")
                if reg.search(res.text):
                    self.notice += "今天已经签到过啦\n"
                    self.signstatus = 1
                else:
                    reg = re.compile(r"redeem\?once=(.*?)'")
                    match = reg.search(res.text)
                    if match:
                        self.once = match.group(1)
                        sio.write(f"获取成功 once:{self.once}\n")
            return True
        except Exception as err:
            sio.write(f"签到异常-check: {err}\n")
            return False

    def daily(self, sio):
        try:
            if not self.once:
                sio.write("未获取到once参数，无法签到\n")
                self.notice += "签到失败：未获取到once参数\n"
                return False
                 
            sio.write(f"Check-in with once: {self.once}\n")
            url = f"https://{self.host}/mission/daily/redeem?once={self.once}"
            sio.write(f"签到链接: {url}\n")
            res = self.session.get(url)
            reg = re.compile(r"已成功领取每日登录奖励")
            if reg.search(res.text):
                self.notice += "签到成功\n"
                self.signstatus = 1
                return True
            else:
                reg = re.compile(r"请重新点击一次以领取每日登录奖励")
                #print(f"签到失败: {res.text}")
                if reg.search(res.text):
                    self.notice += "Message提示：请重新点击一次以领取每日登录奖励\n"
                    sio.write("Message提示：请重新点击一次以领取每日登录奖励\n")
                else:
                    self.notice += "签到失败Cookie疑似失效\n"
                    sio.write("签到失败Cookie疑似失效\n")
            return False
        except Exception as err:
            sio.write(f"签到异常-daily: {err}\n")
            return False

    def balance(self, sio):
        try:
            sio.write("Checking balance...\n")
            url = f"https://{self.host}/balance"
            res = self.session.get(url)
            reg = re.compile(r"\d+?\s的每日登录奖励\s\d+\s铜币")
            match = reg.search(res.text)
            if match:
                sio.write(f"余额查询成功: {match.group(0)}\n")
                self.notice += match.group(0)
                return True
            else:
                sio.write("余额查询失败\n")
                self.notice += "余额查询失败\n"
                return False
        except Exception as err:
            sio.write(f"签到异常-balance: {err}\n")
            return False

# if V2EX_TOKEN:
#     print(f"token: {V2EX_TOKEN}")

# 签到主函数
def main():
    # 初始化日志
    sio = StringIO('签到日志\n')
    sio.seek(0, 2)  # 将读写位置移动到结尾
    tz = pytz.timezone('Asia/Shanghai')
    nowtime = datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
    sio.write("--------------------------" + nowtime + "----------------------------\n")

    try:
        if not V2EX_TOKEN:
            sio.write("你的cookie呢!!!\n获取V2EX数据失败, cookie未定义\n")
            notify(title="V2EX签到失败", msg="获取V2EX数据失败, cookie未定义")
            print(sio.getvalue())
            return

        # 创建V2EX客户端实例
        client = V2EXClient(V2EX_TOKEN)

        # 检查签到状态并获取once参数
        if not client.check(sio):
            notify(title="V2ex自动签到", msg=client.notice)
            print(sio.getvalue())
            return

        time.sleep(1)  # 等待1秒以确保请求完成

        # 如果未签到且获取到once参数，则执行签到
        if client.once and client.signstatus == 0:
            client.daily(sio)
            client.balance(sio)
            if client.signstatus == 0:
                sio.write("签到失败Cookie疑似失效\n")
                sio.write(f"headers: { str(client.session.headers) }\n")
                sio.write(f"cookie: { client.session.cookies.get_dict() }\n")

        sio.write(f"签到状态: {client.signstatus}\n消息: {client.notice}\n")
        notify(title="V2ex自动签到", msg=client.notice)

    except Exception as err:
        sio.write(f"签到异常-main: {err}\n")

    # 输出日志
    print(sio.getvalue())
    print("签到完成")


if __name__ == '__main__':
    main()
