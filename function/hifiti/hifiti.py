import requests
import re,sys
import os
from serverchan_sdk import sc_send; 
sys.path.append("auto-actions/function/hifiti")


# get os environ
SEND_KEY = os.environ.get('SENDKEY')
HIFITI_BBS_Token = os.environ.get('HIFITI_BBS_TOKEN')

# initialize the notification
def notify(title, msg):
    """Send notification using serverchan."""
    if SEND_KEY:
        sc_send(sendkey=SEND_KEY,title=title, desp=msg, options={"tags": "Hifiti签到"})
    else:
        print(f"Title: {title}\nMessage: {msg}")

# Initialize session
s = requests.session()
host = "www.hifiti.com"
# Define headers
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
    "Host": f"{host}",
    "Referer": f"https://{host}/"
}
s.headers.update(headers)
s.cookies.update({'bbs_token': f"{HIFITI_BBS_Token}"})

# Utility function to check session and balance
def check_and_balance():
    """Utility function to create a session with headers."""
    try:
        print("Checking session and balance...")
        response = s.get(f"https://{host}/my.htm", headers=headers)
        if response.status_code == 200 and "个人资料" in response.text:
            pattern = r'<em style="color: #f57e42;font-style: normal;font-weight: bolder;">(.*?)</em>'  # <p.*?>(.*?)</p>
            match = re.search(pattern, response.text, re.DOTALL)
            print(match.group(1) if match else "No match found.")
            return (match.group(1), True) if match else (None, False)
        else:
            print("Failed to create session or invalid cookie.")
            return (None, False)
    except Exception as e:
        print(f"Error during session creation: {e}")
        return (None, False)

# Check-in function
def check_in():
    """Check-in function."""
    try:
        print("Performing check-in...")
        response = s.post(f"https://{host}/sg_sign.htm")
        if "今天已经签过啦！" in response.text:
            print("今日已签到!!!")
            return "今日已签到!!!"
        if response.status_code == 200:
            # print("Check-in response:", response.text)
            print("Check-in successful.")
            return "Check-in successful."
        else:
            print("Check-in failed.")
            return "Check-in failed."
    except Exception as e:
        print("Hifiti Check-in Error", str(e))
        return f"Check-in error: {e}"

# Main function to perform Hifiti sign-in
def main():
    """Main function to perform Hifiti sign-in."""
    print("Starting Hifiti sign-in process...")

    if not HIFITI_BBS_Token:
        print("你的cookie呢!!!\n获取HIFITI数据失败, HIFITI_BBS_Token未定义\n")
        notify(title="HIFITI签到失败", msg="获取HIFITI数据失败, HIFITI_BBS_Token未定义")
        return
    
    balance, status = check_and_balance()
    if status:
        print(f"Balance: {balance}")
        message = f"Check-in before balance: {balance}\n"
        result = check_in()
        message +=f"{result}\n"
        balance, status = check_and_balance()
        if status:
            message += f"Balance after check-in: {balance}\n"
        else:
            message += "Failed to retrieve balance after check-in.\n"
        notify("Hifiti automatic check-in success", message)
    else:
        notify("Hifiti automatic check-in error", "Failed to retrieve balance or invalid cookie.")


if __name__ == "__main__":
    main()