from _G import *
import combat, discord
from stage import StageStatus


def find_floor_sid(n):
  key = f"試練の塔 {n}"
  return next((k for k,p in StageStatus.items() if key in p[1]), None)

def main():
  start_n = int(input("Enter starting floor: "))
  end_n   = int(input("Enter ending floor (0 means util complete or defeat): "))
  cur_n = start_n
  pid = combat.process_partyid_input()
  rid = combat.process_rentalid_input()
  sid = find_floor_sid(cur_n)
  discord.update_status(sid)
  while sid in StageStatus:
    log_info(f"Challenging floor#{cur_n}")
    victory = combat.start_battle_process(sid, pid, rid)
    if not victory:
      log_info("Stop challenge due to defeated")
      break
    cur_n += 1
    if end_n and cur_n > end_n:
      log_info("Destination floor reached")
      break
    sid = find_floor_sid(cur_n)
    log_info(f"Floor#{cur_n-1} cleared")
    uwait(1)
    if Throttling:
      uwait(1)


if __name__ == '__main__':
  main()