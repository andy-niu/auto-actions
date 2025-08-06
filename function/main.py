# 修复相对导入问题，使用绝对导入
from hifiti.hifiti import main as hifiti_checkin
from v2ex.v2ex import main as v2ex_checkin
from smzmd.smzdm import main as smzdm_checkin

def main():
  print(f"<---------- hifiti 签到开始 ---------->")
  hifiti_checkin()
  print(f"<---------- hifiti 签到结束 ---------->") 
  print("\n")
  print(f"<---------- v2ex 签到开始 ---------->")
  v2ex_checkin()
  print(f"<---------- v2ex 签到结束 ---------->")
  print("\n")
  print(f"<---------- smzdm 签到开始 ---------->")
  smzdm_checkin()
  print(f"<---------- smzdm 签到结束 ---------->")
  print("→→→→→→→→→→→ Task END ←←←←←←←←←←")

if __name__ == '__main__':
  main()