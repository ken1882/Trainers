import PIL.ImageGrab, json
import win32api, win32con
import os, time

PWD      = os.path.dirname(os.path.realpath(__file__))
Filename = PWD + '\\easy.json'

button_pos = [1280, 1045]

# position of play again button
replay_pos = [ 85, 50]

# delay time between each click
click_delay = 5

# delay time after play again hit
replay_delay = 5

flag_running = True

with open(Filename, 'r') as file:
  data = json.load(file)
data['0000000000'] = []

def getScreenPixel(x, y):
  if x and y:
    return PIL.ImageGrab.grab().load()[x, y]
  return PIL.ImageGrab.grab().load()

# determine the whether is light or shadow tile
def determine_color(rgb):
  ss = sum(rgb)
  if ss < 300:
    return 0
  return 1

def click(x, y):
  win32api.SetCursorPos((x,y))
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
  win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

def update_keystate():
  global flag_running
  if win32api.GetAsyncKeyState(win32con.VK_F9):
    flag_running = False

def solve():
  click(*button_pos)
  update_keystate()
  
def replay():
  click(*replay_pos)
  update_keystate()

def main_loop():
  solve()
  time.sleep(click_delay)
  replay()
  time.sleep(replay_delay)
  update_keystate()

while flag_running:
  main_loop()
  time.sleep(replay_delay)