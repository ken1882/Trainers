from time import sleep
import win32con,win32api
import _G, utils
from random import sample
from _G import uwait, rwait
import Input
import stage, position, graphics
import audio

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

def start_fishing_fiber():
  while True:
    Input.rclick(1169, 379)
    yield from rwait(2)
    Input.rclick(616, 342)
    yield from rwait(3)
    audio.listen_fishing()
    Input.rclick(616, 342)
    if not stage.is_stage('FishingMind'):
      _G.log_info("Failed")
      yield from rwait(5)
      Input.rclick(616, 342)
      yield from rwait(3)
      continue
    _G.log_info("Success")
    yield from rwait(15)
    Input.rclick(616, 342)
    uwait(1)
