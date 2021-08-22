import win32api,win32con,ctypes
import Input
import _G
import time

BASE_INTERVAL_TIME = 0.1

def move_left(duration):
  try:
    win32con.VK_LEFT
    Input.key_down(win32con.VK_LEFT)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_LEFT)
    yield

def move_right(duration):
  try:
    Input.key_down(win32con.VK_RIGHT)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_RIGHT)
    yield

def move_up(duration):
  try:
    Input.key_down(win32con.VK_UP)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_UP)
    yield

def move_down(duration):
  try:
    Input.key_down(win32con.VK_DOWN)
    times = int(duration / (BASE_INTERVAL_TIME + _G.FPS))
    for _ in range(times):
      time.sleep(BASE_INTERVAL_TIME)
      yield
  finally:
    Input.key_up(win32con.VK_DOWN)
    yield