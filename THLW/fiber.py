import enum
from numpy import gradient
from win32gui import ExtCreatePen
import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
import combat
import utils

def start_walkstage_fiber():
  while True:
    yield
    if stage.is_stage('StageSelect'):
      news = graphics.find_object('newstage.png')
      if not news:
        log_info("No new stage, abort")
        break
      new_stage = news[0]
      Input.rclick(new_stage[0]+150, new_stage[1]+50)
      for _ in range(6):
        wait(0.5)
        yield
    elif stage.is_stage('HelperSelect'):
      Input.rclick(477, 201)
      wait(2)
    elif stage.is_stage('CombatPrepare'):
      Input.rclick(824, 500)
      wait(3) 
    elif stage.is_stage('SceneStory'):
      Input.rclick(931, 45)
      wait(1)
      for _ in range(2):
        Input.rclick(609, 401)
        wait(1)
    elif stage.is_stage('CombatVictory'):
      Input.rclick(509, 401)
      wait(2)
      Input.rclick(882, 514)