import PIL.ImageGrab
import win32api, win32con, sys, time

key_cooldown = 0
running      = True
FPS          = (1 / 120)
Mode         = 0
out_cnt      = 0
out_cache    = []

def update_keystate():
  global key_cooldown, running, out_cache, Mode
  if key_cooldown > 0:
    key_cooldown -= 1
    return
  # Stop program when press F9
  if win32api.GetAsyncKeyState(win32con.VK_F9):
    running = False
    print("\n")
    for s in out_cache:
      print(s, end=' ')
  elif win32api.GetAsyncKeyState(win32con.VK_CONTROL) or win32api.GetAsyncKeyState(win32con.VK_RBUTTON):
    if Mode == 0:
      process_mouse_pixel()
    elif Mode == 1:
      process_screenshot()

def process_mouse_pixel():
  global key_cooldown
  pos, colors = getMousePixel()
  print(pos, end=' ', flush=True)
  out_cache.append(colors)
  key_cooldown = 30

def process_screenshot():
  global out_cnt
  img = PIL.ImageGrab.grab()
  img.save("_out{}.png".format(out_cnt))
  print("Saved to _out{}.png".format(out_cnt))
  out_cnt += 1

def update_main():
  pass

def getPixel(x=None, y=None):
  if x and y:
    return PIL.ImageGrab.grab().load()[x, y]
  return PIL.ImageGrab.grab().load()

def getMousePixel():
  mx, my = win32api.GetCursorPos()
  r,g,b = getPixel(mx, my)
  return ["[{}, {}],".format(mx, my), "({}, {}, {}),".format(r,g,b)]

def start():
  global running, FPS
  while running:
    update_keystate()
    update_main()
    time.sleep(FPS)

if '-p' in sys.argv:
  Mode = 1

if '-s' in sys.argv:
  start()
else:
  print(getMousePixel())