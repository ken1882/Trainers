import _G,stage
import os
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
import utils
import math
import win32con
from datetime import datetime, timedelta

def get_map_type():
  ss = utils.ocr_rect(position.MapTypeRect, fname='maptype.png')
  return ss.lower() if ss else 'valley'

def change_map():
  Input.click(1199, 528)
  wait(0.5)
  Input.click(1178, 667)
  wait(2)

def save_map(seed):
  map = get_map_type()
  path = f"{_G.DCTmpFolder}/{map}"
  utils.ensure_dir_exist(path + '/')
  img = graphics.take_snapshot((448, 195, 1075, 822))
  with open(f"{path}/{seed}.jpg", 'wb') as f:
    img.save(f, format='JPEG')
  return map

def wait_for_load():
  while stage.is_stage('MiniMapLoading'):
    yield
    wait(1)
  wait(1)

def input_seed(seed):
  mx, my = position.MapSeedInput
  Input.click(mx, my)
  wait(0.1)
  for ch in str(seed):
    Input.trigger_key(ord(ch))
    yield
    wait(0.1)
  Input.click(mx, my-40)
  wait(1)

def start_mapping_fiber():
  seed = 4
  target_map = 'sanctuary'
  map = ''
  while True:
    yield
    yield from input_seed(seed)
    yield from wait_for_load()
    map = save_map(seed)
    seed += 1
    if map != target_map:
      change_map()
      yield from wait_for_load()
      map = save_map(seed)

def start_loot_fiber():
  try:
    for icon in ['iplus', 'isell']:
      icon = f"objs/{icon}.png"
      if not os.path.exists(icon):
        raise RuntimeError(f"Icon {icon} does not exists")
      depth = 0
      while _G.FlagWorking:
        ar = graphics.find_object(icon, threshold=0.8)
        if 'sell' in icon:
          ar = [p for p in ar if abs(p[0] - 1030) < 80]
          ar = ar[1:]
        if not ar:
          break
        for i, pos in enumerate(ar):
          x, y = pos
          Input.key_down(win32con.VK_LSHIFT)
          for _ in range(min(10, depth**2)):
            Input.click(x+8, y+8)
            yield
          wait(0.03)
        depth += 1
  finally:
    Input.key_up(win32con.VK_LSHIFT)

def get_warnings():
  ret = []
  text = utils.ocr_rect((1450, 47,1731, 166), fname=f"notifications.png", lang='eng', config='').lower()
  if 'curs' in text:
    ret.append("raid")
  return ret

def dismiss_notifications():
  for x,y in graphics.find_object('objs/dismiss.png'):
    Input.click(x,y)
    uwait(0.1)
  Input.set_cursor_pos(500,500)

def start_autohandle_fiber():
  while _G.FlagWorking:
    try:
      if stage.is_stage('NewSettler'):
        Input.click(753, 842)
      else:
        warns = get_warnings()
        if "raid" in warns:
          log_info("Cannot handle raid, request human takeover")
          _G.FlagWorking = _G.FlagRunning = False
          return
        dismiss_notifications()
        Input.click(1375, 20) # normal speed/unpause
    except Exception as err:
      utils.handle_exception(err)
    for _ in range(100):
      wait(0.1)
      yield