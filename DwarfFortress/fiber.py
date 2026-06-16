import _G
from _G import wait, uwait
import stage, utils, graphics, Input, position
import os
from glob import glob
import logging
import re
from datetime import datetime,timedelta

logging.basicConfig(level=logging.INFO)

def start_world_fiber():
  wt = 0.5
  while _G.FlagWorking:
    while not stage.is_stage('MainMenu'):
      wait(1)
      yield
    while stage.is_stage('MainMenu'):
      Input.click(954, 655)
      wait(1)
      yield
    for pos in (
      (938, 412), # create new world
      (1466, 1015),#(312, 104),(181, 589), # World Type
      (1594, 1020), (118, 970), # Mods
      ):
      Input.click(*pos)
      wait(wt)
      yield
    for _ in range(5):
      Input.click(817, 205)
      yield
      wait(0.1)
    Input.click(100, 100, mright=True)
    wait(wt)
    Input.click(1283, 1022) # create
    while not stage.is_stage('GenComplete'):
      wait(1)
      yield
    while stage.is_stage('GenComplete'):
      Input.click(364, 369)
      wait(1)
      yield

def start_click_fiber():
  for p1 in ((792, 159),(788, 205),(787, 252),(779, 302),(788, 346),(794, 393),(793, 444),):
    Input.click(*p1)
    wait(0.1)
    Input.click(*p1)
    for p2 in ((1122, 47),(1271, 43),(1417, 47),(1577, 47),):
      wait(0.1)
      Input.click(*p2)
      yield

def start_trade_fiber():
  while _G.FlagWorking:
    for pos in ((1569, 268),(1564, 317),(1565, 362),(1569, 412),(1567, 461),(1563, 513),(1565, 559),(1563, 608),(1567, 654),(1565, 696),(1559, 752),(1564, 800),(1559, 842),):
      Input.click(*pos)
      wait(0.03)
      yield
    Input.click(1612, 817)
    yield
    wait(0.1)
