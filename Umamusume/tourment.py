import _G
import graphics
import util
import stage
import position
import Input

from _G import uwait

def start():
  while True:
    yield
    stg = stage.get_current_stage()
    if not stg:
      uwait(1)
      continue
    print(stg)
    if stg == 'TourmentPrepareList':
      Input.rmoveto(*position.TourmentFindMatch)
      uwait(0.3)
      Input.click()
    elif stg == 'TourmentPlayerList':
      Input.rmoveto(*position.TourmentPlayerListOk)
      uwait(0.3)
      Input.click()
      yield
      uwait(0.5)
      Input.rmoveto(*position.TourmentPlayerListOk)
      uwait(0.3)
      Input.click()
    elif stg == 'TourmentRacePrepare':
      yield from process_race()
      for _ in range(10):
        uwait(0.3)
        yield
    elif stg == 'TourmentRaceResult':
      Input.rmoveto(*position.TourmentResultOk)
      uwait(0.3)
      Input.click()
    elif stg == 'TourmentReward':
      break

def process_race():
  Input.rmoveto(*position.TourmentRaceStart)
  uwait(0.3)
  Input.click()
  yield
  while True:
    stg = stage.get_current_stage()
    uwait(1)
    yield
    if stg == 'TourmentRaceResult':
      break
    Input.rmoveto(*position.TourmentRaceSkip)
    uwait(1)
    Input.click()