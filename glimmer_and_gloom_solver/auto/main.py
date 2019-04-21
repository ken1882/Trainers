import PIL.ImageGrab, json
import win32api, win32con
import os, time

PWD      = os.path.dirname(os.path.realpath(__file__))
Filename = PWD + '\\easy.json'

# position of tiles, index:
#...0...1...2
#.3...4...5...6
#...7...8...9
grid_pos = [
  [ 385,  460],
  [ 525,  460],
  [ 670,  460],
  [ 315,  585],
  [ 455,  585],
  [ 600,  585],
  [ 740,  585],
  [ 380,  700],
  [ 530,  700],
  [ 670,  700]
]

# position of play again button
replay_pos = [ 830, 875]

# delay time between each click
click_delay = 0.5

# delay time after play again hit
replay_delay = 1.2

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
  key = ""
  for pos in grid_pos:
    key += str(determine_color(getScreenPixel(*pos)))
  print("{} => {}".format(key, data[key]))
  for pos in data[key]:
    click(*grid_pos[pos])
    update_keystate()
    if not flag_running:
      return 
    time.sleep(click_delay)
  
def replay():
  click(*replay_pos)
  update_keystate()
  if not flag_running:
    return 

def main_loop():
  solve()
  time.sleep(replay_delay)
  replay()
  update_keystate()

while flag_running:
  main_loop()
  time.sleep(replay_delay)