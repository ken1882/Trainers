import _G
import game,combat
from stage import StageData

from _G import SIG_COMBAT_STOP
from _G import wait,uwait,log_info,log_error,log_warning,log_debug

ITER_TIMES = 1000

def process_next_stage(cur):
  flg_ret = False
  for k in StageData.keys():
    if flg_ret:
      return k
    if k == cur:
      flg_ret = True
  return 0

def main():
  start_n = 119038501
  end_n   = 119038302
  # end_n   = 101001302
  pid = combat.process_partyid_input()
  rental_id = combat.process_rentalid_input()
  sid = start_n
  n = ITER_TIMES
  combat.reset_final_report()
  while _G.FlagRunning:
    if _G.FlagPaused:
      while _G.FlagPaused:
        combat.update_input()
        wait(0.1)
      continue
    if n == 0:
      if sid == end_n:
        break
      combat.log_final_report()
      combat.reset_final_report()
      sid = process_next_stage(sid)
      n = ITER_TIMES
    rid = rental_id
    if rid == -1:
      rid = next(combat.RentalCycle)
    log_info(f"Starting {StageData[sid][-1]} of {ITER_TIMES - n +1} / {ITER_TIMES}")
    combat.StageId = sid
    combat.PartyId = pid
    combat.RentalUid = rid
    signal = combat.start_battle_process(sid, pid, rid)
    n -= 1
    log_info("Battle Ended")
    if signal == SIG_COMBAT_STOP:
      break
    uwait(1)
    if _G.Throttling:
      uwait(1)
    combat.update_input()
  combat.log_final_report()
  combat.reset_final_report()

if __name__ == '__main__':
  game.init()
  if not _G.ARGV.output:
    print("Missing output file")
  main()