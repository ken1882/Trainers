import _G
from _G import wait, uwait
import stage, utils, graphics, Input, position
import os
from glob import glob
import logging
import re
from datetime import datetime,timedelta

logging.basicConfig(level=logging.INFO)

GiftCount = 14

GiftPos = {
  'bond_zero_hole': (70, 138),
  'exchange': (68, 174),
  'gift_tile': (1188, 642),
  'basic_plus': (1200, 141),
  'basic_plus_check': (1210, 136),
  'gift_submit': (1080, 654),
  'confirm_gift': (756, 565),
  'bond_level_next': (650, 600),
  'staff_unlock_next': (650, 685),
  'story_skip': (546, 490),
  'ability_detail': (756, 543),
  'top_left_back': (48, 36),
  'next_character': (619, 412),
}

def _wait(sec):
  wait(sec)
  yield

def _click(pos, delay=0.3):
  Input.click(*pos, app_offset=True)
  yield from _wait(delay)

def _wait_until_stage(stg, timeout=30, interval=0.2):
  steps = int(timeout / interval)
  for _ in range(steps):
    if stage.is_stage(stg):
      return True
    yield from _wait(interval)
  _G.log_warning(f"Timed out waiting for stage: {stg}")
  return False

def _wait_until_any_stage(stgs, timeout=30, interval=0.2):
  steps = int(timeout / interval)
  for _ in range(steps):
    cur = stage.get_current_stage()
    if cur in stgs:
      return cur
    yield from _wait(interval)
  _G.log_warning(f"Timed out waiting for any stage: {stgs}")
  return None

def _pixel_sum(pos):
  return sum(graphics.get_pixel(*pos))

def _is_bond_zero():
  try:
    return int(utils.ocr_rect((45, 110, 95, 165), 'ocr_bond.png', zoom=4, num_only=True)) == 0
  except Exception as err:
    _G.log_warning(f"Failed to OCR 絆 level: {err}")
    return False

def _is_basic_plus_enabled():
  return _pixel_sum(GiftPos['basic_plus_check']) > 450

def _select_next_zero_bond_character(max_depth=30):
  for _ in range(max_depth):
    if not (yield from _wait_until_stage('CharacterDetail')):
      return False
    if _is_bond_zero():
      return True
    _G.log_info("絆 level is not 0, moving to next character")
    yield from _click(GiftPos['next_character'], 0.1)
  _G.log_warning("No 絆 level 0 character found")
  return False

def _open_gift_panel():
  yield from _click(GiftPos['exchange'], 0.1)
  if not (yield from _wait_until_stage('ExchangePage')):
    return False
  yield from _click(GiftPos['gift_tile'], 0.1)
  return (yield from _wait_until_stage('GiftPanel'))

def _select_basic_giftboxes():
  for i in range(GiftCount):
    if not _is_basic_plus_enabled():
      _G.log_warning(f"Basic giftbox stock is below {GiftCount}; aborting")
      return False
    yield from _click(GiftPos['basic_plus'], 0.12)
  return True

def _clear_gift_aftermath(max_depth=12):
  for _ in range(max_depth):
    cur = yield from _wait_until_any_stage((
      'CharacterDetail',
      'StoryPrompt',
      'AbilityUnlock',
      'StaffScene',
      'GiftPanel',
      'ExchangePage',
    ), timeout=10)
    if cur == 'CharacterDetail':
      return True
    if cur == 'StoryPrompt':
      yield from _click(GiftPos['story_skip'], 0.1)
    elif cur == 'AbilityUnlock':
      yield from _click(GiftPos['ability_detail'], 0.1)
    elif cur == 'StaffScene':
      yield from _click(GiftPos['top_left_back'], 0.1)
    elif cur in ('GiftPanel', 'ExchangePage'):
      yield from _click(GiftPos['top_left_back'], 0.1)
    else:
      return False
  return stage.is_stage('CharacterDetail')

def start_gift_fiber(max_depth=120):
  giftboxes_selected = False
  gift_confirmed = False
  returned_to_detail = False
  searched_characters = 0

  for _ in range(max_depth):
    cur = stage.get_current_stage()

    if cur is None:
      yield from _wait(0.2)
      continue

    if not stage.is_stage(cur):
      yield from _wait(0.2)
      continue

    if cur == 'CharacterDetail':
      if gift_confirmed:
        returned_to_detail = True
        break

      if _is_bond_zero():
        _G.log_info("Opening gift panel")
        yield from _click(GiftPos['exchange'], 0.2)
      else:
        searched_characters += 1
        if searched_characters >= 30:
          _G.log_warning("No 絆 level 0 character found")
          return
        _G.log_info("絆 level is not 0, moving to next character")
        yield from _click(GiftPos['next_character'], 0.2)

    elif cur == 'ExchangePage':
      yield from _click(GiftPos['gift_tile'], 0.2)

    elif cur == 'GiftPanel':
      if gift_confirmed:
        yield from _click(GiftPos['top_left_back'], 0.5)
      elif not giftboxes_selected:
        if not (yield from _select_basic_giftboxes()):
          yield from _click(GiftPos['top_left_back'], 0.5)
          return
        giftboxes_selected = True
        _G.log_info(f"Selected {GiftCount} basic giftboxes")
      else:
        yield from _click(GiftPos['gift_submit'], 0.2)

    elif cur == 'GiftConfirm':
      yield from _click(GiftPos['confirm_gift'], 0.2)
      gift_confirmed = True
      _G.log_info("Gift confirmed")

      while stage.get_current_stage() != 'CharacterDetail':
        yield from _click(GiftPos['top_left_back'], 0.5)

    else:
      _G.log_warning(f"Unhandled gift flow stage: {cur}")
      yield from _wait(0.5)

  if returned_to_detail:
    _G.log_info("Gift flow returned to character detail")
  else:
    _G.log_warning("Gift flow reached max depth")
