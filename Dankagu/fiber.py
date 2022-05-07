import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
from utils import ocr_rect

def __start_autosong():
  while True:
    wait(1)
    yield
    stg = stage.get_current_stage()
    uwait(0.5)
    if not stg:
      continue
    if 'SongSelect' in stg:
      log_info("Select song")
      Input.click(*position.SongSelect)
    elif 'PartySelect' in stg:
      log_info("Select party")
      Input.click(*position.SongStart)
      uwait(2)
      Input.click(*position.ConfirmStart)
      log_info("Song started")
      for _ in range(8):
        yield
        uwait(0.5)
    elif 'SongClear' in stg:
      log_info("Song cleared")
      while True:
        stg = stage.get_current_stage()
        if stg in ('SceneLoading', 'SongSelect'):
          log_info("Stage completed")
          break
        Input.rclick(*position.ClearedOK)
        uwait(0.2)
        yield
        Input.rclick(*position.StoryUnlockNext)
        uwait(0.2)
        yield
        Input.rclick(*position.EventOK)
        uwait(0.2)
        yield

def start_auto_song_fiber():
  n = int(_G.ARGV.repeats or 0)
  if not n:
    while _G.FlagRunning:
      yield from __start_autosong()
  else:
    for _ in range(n):
      yield from __start_autosong()