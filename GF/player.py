from glob import glob
from time import sleep
from _G import log_debug,log_error,log_info,log_warning

import _G
import re
import utils
import graphics, stage
import Input
import position
import action

def swap_member_async(src, dst):
  log_info(f"Swapping {src} => {dst}")
  tpos = graphics.find_object(f"names/{src}.png")
  while not tpos:
    yield
    sleep(1)
    tpos = graphics.find_object(f"names/{src}.png")
  
  mx, my = tpos[0]
  Input.click(int(mx+35), int(my-40))
  
  yield from action.wait_until_stage('PartyMemberEdit')
  
  errcnt = 0
  tpos = None
  while not tpos:
    yield
    errcnt += 1
    sleep(1)
    tpos = find_member(dst)
    if errcnt > 10:
      raise RuntimeError(f"Unable to find member: {dst}")
  
  mx, my = tpos[0]
  Input.click(int(mx+35), int(my-40))

  yield from action.wait_until_stage('PartyEdit')

def get_party_member(index):
  images = glob('names/*.png')
  for img in images:
    pos = graphics.find_object(img)
    pos = pos[0] if pos else None
    if pos and \
      pos[0] >= position.FORMATION_NAME_RECT[index][0] and \
      pos[0] <= position.FORMATION_NAME_RECT[index][2]:
      return re.split(f"[\\\/]", img)[-1][:-4]
  return ''

def find_member(name):
  images = glob(f"names/{name}*.png")
  for img in images:
    pos = graphics.find_object(img)
    if pos:
      return pos
  return None