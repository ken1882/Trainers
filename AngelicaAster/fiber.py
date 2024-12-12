from time import sleep
import win32con,win32api
import _G, utils
from random import sample
from _G import uwait, rwait
import Input
import stage, position, graphics

def start_refight_fiber():
  n = _G.ARGV.repeats
  n = n if n > 0 else 9999
  while n >= 0:
    n -= 1
    _G.log_info(f"Refights left: {n}")
    uwait(1)
    yield
    while not stage.is_stage('CombatVictory'):
      uwait(1)
      yield
    Input.rclick(*position.Refight)
    yield from rwait(3)

def start_mdlpusher_fiber():
  while True:
    if utils.is_focused():
      Input.rclick(*sample(position.MdlPusherPosList, 1)[0])
    yield

def start_minigame_drop_fiber():
  while True:
    yield
    if not utils.is_focused():
      continue
    if stage.is_stage('MinigameDropEnd'):
      uwait(1)
      Input.rclick(452, 601)
      yield from rwait(1)
      continue
    Input.rclick(635, 161)