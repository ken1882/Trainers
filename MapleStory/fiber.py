from time import sleep
import win32con
import _G
from _G import uwait
import Input
import Arcana_UpperPath,StarryOcean4
import skill
from utils import spawn_childproc

def start_click_fiber():
  cnt = int(_G.ConsoleArgv.ntimes)
  for _ in range(cnt):
    Input.click()
    uwait(0.1)
    Input.click()
    uwait(0.03)
    yield

def start_starry_ocean():
  name = 'macro_main'
  spawn_childproc(name, StarryOcean4.start_main)
  _G.MainChild = _G.ChildProcess[name]
  _G.MainChildPipe = _G.ChildPipe[name]
  _G.MainChildName = name
  print("Chlid proc started")

def start_reincarnation_helper(bod=True, fire=False):
  hour = 60 * 60 * 4
  interval = 60
  skill.FireStarter.apply_cd()
  if bod:
    print('Auto BOD on')
  if fire:
    print('Auto fire on')
  for i in range(hour // interval):
    sleep(2)
    if bod:
      print(f"Use BOD #{i+1}")
      skill.BreathOfDivinity.use()
    if i % 5 == 0:
      sleep(0.3)
      print(f"Place monument #{(i // 5)+1}")
      skill.Reincarnation.use()
    if fire and skill.FireStarter.is_ready():
      sleep(1)
      print('Ignite incendiary')
      skill.FireStarter.use()
      skill.FireStarter.apply_cd()
    sleep(interval)
    

def start_alter_helper():
  while True:
    Input.update()
    sleep(_G.FPS)
    if Input.is_trigger(win32con.VK_NUMPAD9):
      break
    elif Input.is_trigger(win32con.VK_NUMPAD0):
      kp = Input.get_keybd_pair(_G.MAPLE_KEYCODE['SPACE'])
      for _ in range(30):
        for event in kp:
          Input.SendInput(event)

def start_test_fiber():
  pass