import _G,stage,utils,position
from _G import uwait, log_info
import Input
from random import randint

ActionQueue = []

def is_battle_ended():
  stg = stage.get_current_stage()
  if stg == 'MirrorDefeat' or stg == 'MirrorVicotry':
    mx,my = position.GeneralNext
    Input.rmoveto(mx, my-300, rrange=30)
    uwait(0.1)
    Input.click()
  elif stg and 'BattleEnd' in stg:
    log_info("Battle ended")
    return True
  return False

def start_combat():
  global ActionQueue
  while not is_battle_ended():
    stg = ''
    while not stg == 'CombatPlayerTurn':
      if is_battle_ended():
        break
      log_info("Current stage:", stg, '; waiting for player turn')
      for _ in range(5):
        uwait(0.1)
        yield
      stg = stage.get_current_stage()
    if is_battle_ended():
      break
    log_info("Player turn started")
    ActionQueue.clear()
    determine_actions()
    yield from process_actions()
    for _ in range(3):
      uwait(0.3)
      yield

def determine_actions():
  determine_magia()
  # determine_connection()
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
  
  priority = [
    2, # Charge
    1, # Blast
    0, # Accele
  ]
  for p in priority:
    for i,d in enumerate(disks):
      if d == _G.DiskTypes[p]:
        ret.append(i)
  return ret[:3]

'''
Action List:
'disk', (int)index
'connection', (int)disk_index, (list<int*>)companion_position
'magia', (int)index
'skill', (int)index
'''
def process_actions():
  global ActionQueue
  log_info("Action Queue:", ActionQueue)
  for action in ActionQueue:
    _type, _arg = action
    print(_type, _arg)
    if _type == 'disk':
      Input.rmoveto(*position.DiskIcons[_arg])
      uwait(0.1)
      Input.click()
      uwait(0.1)
      yield
    else:
      pass
    for _ in range(5):
      uwait(0.05)
      yield

def determine_connection():
  global ActionQueue
  availble = []
  for i,pixstr in enumerate(position.ConnectionAvailable):
    if stage.check_pixels(pixstr):
      availble.append(i)
  log_info("Available connection:", availble)
  if not availble:
    return
  for index in availble:
    Input.rmoveto(*position.DiskIcons[index])
    uwait(0.3)
    yield
    Input.mouse_down(app_offset=False)
    uwait(0.3)
    companions = stage.get_connection_targets()
    log_info("Connection companions:", companions)
    Input.mouse_up(app_offset=False)
    ActionQueue.append(('connection', index, companions))
    uwait(0.3)
    yield

def use_connection(didx, fidx):
  '''
  didx - Disk index
  fidx - Formation index
  '''
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

def determine_magia():
  pass