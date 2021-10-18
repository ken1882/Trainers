from _G import *
import combat, discord
from stage import StageStatus
import game

ATYPE_NONE     = 0
ATYPE_SLASH    = 1
ATYPE_PIERCE   = 2
ATYPE_BLUDGEON = 3
ATYPE_SLASH_CHAR    = '刃'
ATYPE_PIERCE_CHAR   = '貫'
ATYPE_BLUDGEON_CHAR = '衝'

def find_floor_sid(n):
  key = f"試練の塔 {n}"
  return next((k for k,p in StageStatus.items() if key in p[1]), None)

def get_stage_weakness(sid):
  data = game.get_quest(sid)
  rec_str = data['RecommendOffenceAttribute']
  if ATYPE_SLASH_CHAR in rec_str:
    return ATYPE_SLASH
  elif ATYPE_PIERCE_CHAR in rec_str:
    return ATYPE_PIERCE
  elif ATYPE_BLUDGEON_CHAR in rec_str:
    return ATYPE_BLUDGEON
  return ATYPE_NONE

def main():
  start_n = int(input("Enter starting floor: "))
  end_n   = int(input("Enter ending floor (0 means util complete or defeat): "))
  cur_n   = start_n
  pids    = []
  print("General-purpose Party:")
  pids.append(combat.process_partyid_input())
  print("Slashing dedicated Party:")
  pids.append(combat.process_partyid_input())
  print("Piericing dedicated Party:")
  pids.append(combat.process_partyid_input())
  print("Bludgeoning dedicated Party:")
  pids.append(combat.process_partyid_input())
  rid = combat.process_rentalid_input()
  sid = find_floor_sid(cur_n)
  rpn = get_stage_weakness(sid)
  discord.update_status(sid)
  while sid in StageStatus:
    log_info(f"Challenging floor#{cur_n}")
    log_info(f"Using team#{pids[rpn]} weakness: ({rpn})")
    victory = combat.start_battle_process(sid, pids[rpn], rid)
    if not victory:
      log_info("Stop challenge due to defeated")
      break
    cur_n += 1
    if end_n and cur_n > end_n:
      log_info("Destination floor reached")
      break
    sid = find_floor_sid(cur_n)
    rpn = get_stage_weakness(sid)
    log_info(f"Floor#{cur_n-1} cleared")
    uwait(1)
    if _G.Throttling:
      uwait(1)


if __name__ == '__main__':
  game.init()
  main()