from threading import Thread
import re
import pickle
import os.path
import sys
sys.path.append('./lib')

import _G, const, util, Input, pixel
import pos

SavedDragonArchiveName = "DVMsaved.dat"
saved_dragons = []

def start():
  util.init()
  
  if _G.AppHwnd == 0:
    print("App not found, aborting")
    return exit()

  util.activate_window(_G.AppHwnd)
  while _G.Flags['running']:
    main_loop()

def main_loop():
  util.uwait(_G.UpdateDuration, False)
  
  update_basic()
  _G.CurScriptTick += 1
  _G.FrameCount += 1
  if _G.CurScriptTick >= _G.ScriptUpdateTime:
    _G.CurScriptTick = 0
    if not _G.Flags['paused']:
      update_script()
      Input.clear_cache()

def update_basic():
  update_input()

def update_input():
  Input.update()
  # pause program
  if Input.is_trigger(Input.keymap.kF8, True):
    _G.Flags['paused'] ^= True
    print(f"Paused: {_G.Flags['paused']}")
  
  # terminate program
  elif Input.is_trigger(Input.keymap.kF9, True):
    _G.Flags['running'] = False

def update_script():
  util.get_app_rect()

def load_archive():
  global saved_dragons
  if os.path.exists(SavedDragonArchiveName):
    with open(SavedDragonArchiveName, 'rb') as fp:
      saved_dragons = pickle.load(fp)
      if not saved_dragons:
        saved_dragons = []

def save_archive():
  global saved_dragons
  with open(SavedDragonArchiveName, 'wb') as fp:
    pickle.dump(saved_dragons, fp)

def transform_ocr_result(text):
  return text[:-1] if text[-1] == 'L' else text

def save_stage_images(filename):
  stage_name = ['baby', 'junior', 'adult']
  for i, sname in enumerate(stage_name):
    Input.random_click(*pos.DragonStagePos[i])
    util.wait(0.1)
    img = util.print_window(imobj=True, canvas_only=True)
    util.save_image(img, f"{filename}{i}.png", "PNG")
    util.wait(0.5)

def process_element_image(filename):
  ele_name = ['earth', 'water', 'fire', 'light', 'dark']
  availables = pixel.is_pixels_match(pos.ElementsAvailablePos, 
    pos.ElementsAvailableColor, indr=True)
  
  if _G.Flags['log-level'] > 0:
    print(f"Elements: {availables}")

  for i, ename in enumerate(ele_name):
    if not availables[i]:
      continue
    Input.random_click(*pos.ElementsChangePos[i])
    util.wait(1.2)
    save_stage_images(filename + str(i))

def get_dragon_info():
  global saved_dragons
  name = util.read_app_text(*pos.DragonNameRect, dtype='alpha')
  name = transform_ocr_result(name)
  print(name)
  
  if name in saved_dragons:
    print("Dragon already saved")
    return False
  
  saved_dragons.append(name)
  filename = f"dragon/{name}_"
  process_element_image(filename)

  return True

util.init()
util.ensure_dir_exists("dragon/")
load_archive()
exists_cnt = 0
while exists_cnt < 10:
  util.flush()
  util.get_app_rect()
  if not get_dragon_info():
    exists_cnt += 1
  Input.random_click(*pos.NextDragonPos)
  util.wait(1.5)
  save_archive()