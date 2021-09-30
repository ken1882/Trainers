import _G,stage,utils,position
from _G import uwait

def is_battle_ended():
  stg = stage.get_current_stage()
  if 'BattleEnd' in stg:
    return True
  return False

def start_combat():
  while not is_battle_ended():
    stg = stage.get_current_stage()
    while not stg == 'CombatPlayerTurn':
      uwait(0.5)
      yield
    

def process_heuristics():
  pass

def process_actions():
  pass

def determine_actions():
  pass

def use_skill():
  pass

def use_magia():
  pass

def select_disks():
  pass

def determine_disks():
  pass

def determine_taget():
  pass

def select_target():
  pass

def use_connection():
  pass

def determine_connection():
  pass