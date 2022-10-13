from time import sleep
from copy import copy
from _G import log_debug,log_error,log_info,log_warning, lwait

import _G
import utils
import stage
import graphics
import Input
import position
import player, action
Counter = 0

DEPLOY_POSITION = [
  [(497, 323), 1],
  [(725, 151), 2]
]

PLAN_LOCATIONS = [
  (500, 320),
  (494, 146),(710, 1)
]

def edit_swap_party():
  Input.click(*DEPLOY_POSITION[0][0])
  yield from action.wait_until_stage('CombatPartySelect')
  
  Input.click(*position.COMBAT_PARTY_EDIT)
  yield from action.wait_until_stage('PartyEdit')
  yield from lwait(1)

  fn  = player.get_party_member(0)
  dst = 'sop2'
  if fn == 'sop2':
    dst = 'hk416'
  
  yield from player.swap_member_async(fn, dst)
  yield from lwait(1)
  Input.click(*position.GENERAL_BACK)



def main(cnt):
  global Counter
  Counter = cnt
  log_info(f"Start interation #{cnt+1}")
  yield from action.wait_until_stage('CombatPrepare')
  yield from edit_swap_party()
  yield from action.wait_until_stage('CombatPrepare')
  yield from action.deploy_teams(DEPLOY_POSITION)
  Input.click(*position.COMBAT_START)
  yield from lwait(3)
  yield from action.wait_until_stage('CombatPlayerPhase', 'CombatFullInventory')
  stg = stage.get_current_stage()
  if stg == 'CombatFullInventory':
    # Input.click(*position.FULL_BAG_DISMENTAL)
    # yield from action.dismental_chars()
    _G.FlagRunning = False
    return

  yield from action.supply_position(DEPLOY_POSITION[1][0])
  yield from action.retret_position(DEPLOY_POSITION[1][0])
  yield from action.plan_mode(copy(PLAN_LOCATIONS))
  Input.click(*position.COMBAT_TURN_END)
  yield from action.wait_until_turn_end()
  yield from action.restart_combat()
  yield from lwait(3)
  