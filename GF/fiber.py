from glob import glob
import _G, stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
import importlib
from random import randint
from utils import ocr_rect
import re
import battle

files = glob('battle/*.py')
for lib in files:
  lib = re.split(r"[\\\/]", lib)[-1]
  libn = f"battle.{lib[:-3]}"
  log_info(f"{libn} imported")
  importlib.import_module(libn)

def start_combat_fiber():
  _n = int(_G.ARGV.repeats) if _G.ARGV.repeats else 0x7fffffff
  _t = _G.ARGV.target
  target = None
  if not _t:
    log_info("Not target given")    
    return False

  target = next((getattr(battle, st) for st in dir(battle) if st == _t), None)
  if not target:
    log_info(f"Battle `{_t}` not found")
    return False
  
  for i in range(_n):
    yield from target.main(i)