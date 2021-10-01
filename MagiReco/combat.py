import _G,stage,utils,position
from _G import uwait
import Input
from random import randint

ActionQueue = []

def is_battle_ended():
  stg = stage.get_current_stage()
  if stg and 'BattleEnd' in stg:
    return True
  return False

def start_combat():
  global ActionQueue
  while not is_battle_ended():
    stg = ''
    while not stg == 'CombatPlayerTurn':
      if is_battle_ended():
        break
      _G.log_info("Current stage:", stg, '; waiting for player turn')
      for _ in range(5):
        uwait(0.1)
        yield
      stg = stage.get_current_stage()
    if is_battle_ended():
      break
    _G.log_info("Player turn started")
    ActionQueue.clear()
    determine_actions()
    yield from process_actions()
    for _ in range(3):
      uwait(0.3)
      yield

def determine_actions():
  disks = determine_disks()
  for di in disks:
    ActionQueue.append(('disk', di))

def determine_disks():
  global ActionQueue
  disks = stage.get_disks()
  cnt = [0,0,0]
  ov3_type = '' # type >= 3
  for d in disks:
    for i,t in enumerate(_G.DiskTypes):
      if d == t:
        cnt[i] += 1
        if cnt[i] >= 3:
          ov3_type = t
  ret = []
  if ov3_type:
    for i,d in enumerate(disks):
      if d == ov3_type:
        ret.append(i)
    return ret # should contain 3 disk with same type
  
  # take blast,charge,accele
  for i,d in enumerate(disks):
    if d == _G.DiskTypes[1]:
      ret.append(i)
  for i,d in enumerate(disks):
    if d == _G.DiskTypes[2]:
      ret.append(i)
  for i,d in enumerate(disks):
    if d == _G.DiskTypes[0]:
      ret.append(i)
  return ret[:3]

def process_actions():
  global ActionQueue
  _G.log_info("Action Queue:", ActionQueue)
  for action in ActionQueue:
    _type, _arg = action
    print(_type, _arg)
    if _type == 'disk':
      Input.rmoveto(*position.DiskIcons[_arg])
      uwait(0.3)
      Input.click()
      uwait(0.1)
      yield
    else:
      pass
    for _ in range(5):
      uwait(0.05)
      yield

def process_heuristics():
  pass

def use_skill():
  pass

def use_magia():
  pass

def select_disks():
  pass

def determine_taget():
  pass

def select_target():
  pass

def use_connection():
  pass

def determine_connection():
  pass