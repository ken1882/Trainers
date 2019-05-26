import PIL.ImageGrab, argparse
import const, G, util, Input

key_cooldown = 0
running      = True
FPS          = (1 / 120)
Mode         = 0
out_cnt      = 0
out_cache    = []

parser = argparse.ArgumentParser()
Ptrue  = "store_true"
Pfalse = "store_false"
parser.add_argument("-s", "--start", action=Ptrue)
parser.add_argument("-p", "--picture", action=Ptrue)
parser.add_argument("-x", "--x-pos", type=int, default=-1)
parser.add_argument("-y", "--y-pos", type=int, default=-1)

def update_keystate():
  global key_cooldown, running, out_cache, Mode
  if key_cooldown > 0:
    key_cooldown -= 1
    return
  # Stop program when press F9
  if Input.is_trigger(Input.keymap.kF9):
    running = False
    print("\n")
    for s in out_cache:
      print(s, end=' ')
  elif Input.is_trigger(Input.keymap.kMOUSE2) or Input.is_trigger(Input.keymap.kCONTROL):
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

def getMousePixel(mx=None, my=None):
  if not mx and not my:
    mx, my = util.get_cursor_pos(False)
  r,g,b = getPixel(mx, my)
  offset = const.getAppOffset()
  mx = mx - G.AppRect[0] - offset[0]
  my = my - G.AppRect[1] - offset[1]
  return ["[{}, {}],".format(mx, my), "({}, {}, {}),".format(r,g,b)]

def start():
  global running, FPS
  while running:
    Input.clean_intern()
    Input.update()
    update_keystate()
    update_main()
    util.wait(FPS)

args = parser.parse_args() 

if args.picture:
  Mode = 1

util.find_app()

print("Offset:", const.getAppOffset())
if args.start:
  start()
else:
  x = args.x_pos if args.x_pos >= 0 else None
  y = args.y_pos if args.y_pos >= 0 else None
  print(getMousePixel(x, y))