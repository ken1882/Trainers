import _G
from _G import *
import combat, discord
from stage import StageData
import game
from Input import input
from combat import update_input

def main():
  sid = combat.process_stageid_input()
  end_n = int(input("Enter ending stage id (0 means util complete or defeat): "))
  pid = combat.process_partyid_input()
  rid = combat.process_rentalid_input()
  cur_n   = sid
  # end_n  += sid - 1
  discord.update_status(sid)
  while _G.FlagRunning:
    log_info(f"Challenging floor#{cur_n%100}")
    try:
      signal = combat.start_battle_process(sid, pid, rid)
    except (SystemExit, Exception) as err:
      handle_exception(err)
      break
    if signal != SIG_COMBAT_WON:
      log_info("Stop challenge due to defeated")
      break
    cur_n += 1
    if end_n and cur_n > end_n:
      log_info("Destination floor reached")
      break
    log_info(f"Floor#{sid%100} cleared")
    sid = cur_n
    update_input()
    uwait(1)
    if _G.Throttling:
      uwait(1)


if __name__ == '__main__':
  game.init()
  main()