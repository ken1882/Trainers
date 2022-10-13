from time import sleep
from _G import log_debug,log_error,log_info,log_warning, lwait

import _G
import utils
import stage
import graphics
import Input
import position

LastStage = None
def wait_until_stage(*t_stages):
  global LastStage
  stg = None
  while not stg or stg not in t_stages:
    sleep(1)
    stg = stage.get_current_stage()
    if LastStage != stg:
      log_info(f"Current stage: {stg}")
      LastStage = stg
    yield

def deploy_teams(locations):
  for pos,idx in locations:
    Input.click(*pos)
    yield from wait_until_stage('CombatPartySelect')
    sleep(1)
    Input.click(*position.COMBAT_PARTY_DEPLOY)
    yield from lwait(2)

def supply_position(pos):
  Input.click(*pos)
  sleep(0.1)
  Input.click(*pos)
  yield from wait_until_stage('CombatPartyPanel')
  Input.click(*position.COMBAT_PARTY_SUPPLY)
  yield from lwait(1)

def retret_position(pos):
  Input.click(*pos)
  sleep(0.1)
  Input.click(*pos)
  yield from wait_until_stage('CombatPartyPanel')
  Input.click(*position.COMBAT_PARTY_RETRET)
  yield from lwait(1.5)
  Input.click(*position.COMBAT_PARTY_RETRET_CONFIRM)
  yield from lwait(1)

def plan_mode(locations):
  locations.insert(0, position.COMBAT_PLAN_MODE)
  for pos in locations:
    if len(pos) == 2:
      Input.click(*pos)
      sleep(0.5)
    elif len(pos) == 4:
      pass # TODO: dragging
  
  yield from lwait(1)

def wait_until_turn_end():
  global LastStage
  stg = None
  cnt = 0
  while True:
    sleep(1)
    stg = stage.get_current_stage()
    if LastStage != stg:
      log_info(f"Current stage: {stg}")
      LastStage = stg
    if stg == 'CombatPlayerTurnEnd':
      cnt += 1
      if cnt > 3:
        break
    else:
      cnt = 0
    yield
  
def restart_combat():
  Input.click(*position.COMBAT_STOP)
  yield
  sleep(1.5)
  Input.click(*position.COMBAT_RETRY)
  yield
  sleep(0.5)

def dismental_chars():
  yield from wait_until_stage('SceneFactory')
  # 2 stars
  Input.click(*position.DISMENTAL_CHARS)
  yield from lwait(3)
  Input.click(*position.DISMENTAL_AUTO)
  yield from lwait(1.5)
  Input.click(*position.DISMENTAL_AUTO)
  yield from lwait(2)
  Input.click(*position.DISMENTAL_START)
  yield from lwait(2)
  # 3 stars
  Input.click(*position.DISMENTAL_CHARS)
  yield from lwait(2)
  seq = [
    position.FILTER_CHAR,
    position.FILTER_STAR_3,
    position.FILTER_CONFIRM
  ]
  for p in seq:
    Input.click(*p)
    sleep(0.5)
  for p in position.DISMENTAL_POS:
    Input.click(*p)
    sleep(0.5)
  seq = [
    position.FILTER_CHAR,
    position.FILTER_RESET
  ]
  for p in seq:
    Input.click(*p)
    sleep(0.5)
  
  yield from lwait(1)
  Input.click(*position.DISMENTAL_AUTO)
  yield from lwait(2)
  Input.click(*position.DISMENTAL_START)
  yield from lwait(1)
  Input.click(*position.DISMENTAL_CONFIRM)
  yield from lwait(1)
  