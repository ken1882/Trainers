import sys
sys.path.append('./lib')
import _G, const, util, Input
import PIL.ImageGrab

key_cooldown = 0
running      = True
FPS          = (1 / 120)
Mode         = 0
out_cnt      = 0
out_cache    = []
      
def start():
  global running, FPS
  util.init()
  while running:
    util.get_app_rect()
    Input.clear_cache()
    Input.update()
    update_main()
    util.wait(FPS)

def update_main():
  global key_cooldown, running, out_cache, Mode
  if key_cooldown > 0:
    key_cooldown -= 1
    return
  # Stop program when press F9
  if Input.is_trigger(Input.keymap.kF9, False):
    running = False
    print("\n")
    for s in out_cache:
      print(s, end=' ')
  elif Input.is_trigger(Input.keymap.kMOUSE2, False) or Input.is_trigger(Input.keymap.kCONTROL, False):
    if Mode == 0:
      process_mouse_pixel()

def process_mouse_pixel():
  global key_cooldown
  pos, colors = getMousePixel()
  print(pos, end=' ', flush=True)
  out_cache.append(colors)
  key_cooldown = 30

def getMousePixel(mx=None, my=None):
  if not mx and not my:
    mx, my = util.get_cursor_pos(False)
  r,g,b = getPixel(mx, my)
  offset = const.AppOffset
  mx = mx - _G.AppRect[0] - offset[0]
  my = my - _G.AppRect[1] - offset[1]
  return ["({}, {}),".format(mx, my), "({}, {}, {}),".format(r,g,b)]

def getPixel(x=None, y=None):
  if x and y:
    return PIL.ImageGrab.grab().load()[x, y]
  return PIL.ImageGrab.grab().load()

start()