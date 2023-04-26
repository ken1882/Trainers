import win32api,win32con,ctypes
import Input
import _G
import time
import multiprocessing
from multiprocessing import Process,Pipe
import skill

BASE_INTERVAL_TIME = 0.1
DIR_LEFT  = 1
DIR_RIGHT = 2

def move_left_async(duration):
  try:
    Input.key_down(win32con.VK_LEFT)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_LEFT)
    yield

def move_right_async(duration):
  try:
    Input.key_down(win32con.VK_RIGHT)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_RIGHT)
    yield

def move_up_async(duration):
  try:
    Input.key_down(win32con.VK_UP)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    print(duration, times)
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_UP)
    yield

def move_down_async(duration):
  try:
    Input.key_down(win32con.VK_DOWN)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_DOWN)
    yield

def jump_down_async():
  try:
    Input.key_down(win32con.VK_DOWN)
    time.sleep(BASE_INTERVAL_TIME)
    yield
    jump()
    time.sleep(BASE_INTERVAL_TIME)
    yield
  finally:
    Input.key_up(win32con.VK_DOWN)


def move_left(duration):
  try:
    Input.key_down(win32con.VK_LEFT)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
  finally:
    Input.key_up(win32con.VK_LEFT)

def move_right(duration):
  try:
    Input.key_down(win32con.VK_RIGHT)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
  finally:
    Input.key_up(win32con.VK_RIGHT)

def move_up(duration):
  try:
    Input.key_down(win32con.VK_UP)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
  finally:
    Input.key_up(win32con.VK_UP)

def move_down(duration):
  try:
    Input.key_down(win32con.VK_DOWN)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
  finally:
    Input.key_up(win32con.VK_DOWN)

def jump_down():
  try:
    Input.key_down(win32con.VK_DOWN)
    time.sleep(0.1)
    jump()
    time.sleep(0.3)
  finally:
    Input.key_up(win32con.VK_DOWN)

def interact():
  for event in Input.get_keybd_pair(_G.MAPLE_KEYCODE['SPACE']):
    Input.SendInput(event)

def enter():
  for event in Input.get_keybd_pair(_G.MAPLE_KEYCODE['ENTER']):
    Input.SendInput(event)

def blink_left():
  try:
    Input.key_down(win32con.VK_LEFT)
    time.sleep(0.08)
    skill.Teleport.use()
    time.sleep(0.05)
  finally:
    Input.key_up(win32con.VK_LEFT)

def blink_right():
  try:
    Input.key_down(win32con.VK_RIGHT)
    time.sleep(0.08)
    skill.Teleport.use()
    time.sleep(0.05)
  finally:
    Input.key_up(win32con.VK_RIGHT)

def blink_up():
  try:
    Input.key_down(win32con.VK_UP)
    time.sleep(0.08)
    skill.Teleport.use()
    time.sleep(0.05)
  finally:
    Input.key_up(win32con.VK_UP)

def blink_down():
  try:
    Input.key_down(win32con.VK_DOWN)
    time.sleep(0.08)
    skill.Teleport.use()
    time.sleep(0.05)
  finally:
    Input.key_up(win32con.VK_DOWN)

def jump():
  for event in Input.get_keybd_pair(_G.MAPLE_KEYCODE['ALT']):
    Input.SendInput(event)
    time.sleep(0.05)

def double_jumpup(dir=0):
  eves = list(Input.get_keybd_pair(win32con.VK_UP))
  try:
    Input.SendInput(eves[0])
    Input.key_down(win32con.VK_UP)
    time.sleep(0.1)
    jump()
    if dir == DIR_LEFT:
      Input.trigger_key(win32con.VK_LEFT)
    elif dir == DIR_RIGHT:
      Input.trigger_key(win32con.VK_RIGHT)
    time.sleep(0.2)
    jump()
    time.sleep(1)
  finally:
    Input.key_up(win32con.VK_UP)
    Input.SendInput(eves[1])

def eldas_spring():
  eves = list(Input.get_keybd_pair(win32con.VK_DOWN))
  try:
    Input.SendInput(eves[0])
    Input.key_down(win32con.VK_DOWN)
    time.sleep(0.1)
    skill.EldasFall.use()
    time.sleep(0.5)
  finally:
    Input.key_up(win32con.VK_DOWN)
    Input.SendInput(eves[1])