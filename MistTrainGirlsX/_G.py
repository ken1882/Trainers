import requests
import sys
from datetime import datetime,timedelta
from time import sleep,gmtime,strftime
from random import randint

def format_curtime():
  return datetime.strftime(datetime.now(), '%H:%M:%S')

def log_info(*args):
  print(f"[{format_curtime()}] [INFO]:", *args)

def log_error(*args):
  print(f"[{format_curtime()}] [ERROR]:", *args)

def uwait(sec):
  sleep(sec + randint(0,8) / 10)

def is_response_ok(res):
  print(res)
  if res.status_code != 200:
    log_error(f"An error occurred during sending request:\n{res}\n{res.json()}\n\n")
    return False
  print(res.json())
  print('\n')
  return True

def jpt2localt(jp_time):
  '''
  Convert Japanese timezone (GMT+9) datetime object to local timezone
  '''
  time_jp = +9
  time_local = int(strftime("%z", gmtime())) // 100
  delta = time_jp - time_local
  return jp_time - timedelta(hours=delta)


Session = requests.Session()
Session.headers = {
  'Authorization': sys.argv[1]
}
