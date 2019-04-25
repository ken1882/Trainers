import PIL.ImageGrab
import win32api, win32con
import util, const, action

ColorRange = 20

def is_color_ok(cur, target):
  for c1,c2 in zip(cur,target):
    if const.FlagDebug:
      print(c1, c2)
    if abs(c1 - c2) > ColorRange:
      return False
  return True

def is_pixel_match(pix, col):
  for i, j in zip(pix, col):
    if not is_color_ok(util.getPixel(*i), j):
      return False
  return True

def has_event():
  return is_pixel_match(const.EventPixel, const.EventColor)

def is_stage_map():
  return is_pixel_match(const.StageMapPixel, const.StageMapColor)

def is_stage_loot():
  return is_pixel_match(const.StageLootPixel, const.StageLootColor)

def is_battle_end():
  return is_pixel_match(const.StageBattleEndPixel, const.StageBattleEndColor)

def is_stage_level():
  return is_pixel_match(const.StageLevelPixel, const.StageLevelColor)

def is_stage_battle():
  return is_pixel_match(const.StageBattlePixel, const.StageBattleColor)

def is_stage_levelup():
  return is_pixel_match(const.StageLevelupPixel, const.StageLevelupColor)

def is_no_stamina():
  return is_pixel_match(const.StageNoStaminaPixel, const.StageNoStaminaColor)

def is_stage_boss():
  return is_pixel_match(const.StageBossPixel, const.StageBossColor)

def is_stage_shop():
  return is_pixel_match(const.StageShopPixel, const.StageShopColor)

def is_stage_shoplist():
  return is_pixel_match(const.StageShopListPixel, const.StageShopListColor)

def is_stage_no_ticket():
  return is_pixel_match(const.StageNoTicketPixel, const.StageNoTicketColor)

def is_stage_mine():
  return is_pixel_match(const.StageMinePixel, const.StageMineColor)

def is_stage_farm():
  return is_pixel_match(const.StageFarmPixel, const.StageFarmColor)

def is_stage_town():
  pass

def get_current_stage():
  if is_no_stamina():
    return ("No Stamina!")
  elif has_event():
    return "event"
  if is_stage_map():
    return "map"
  elif is_stage_level():
    return "level"
  elif is_stage_loot():
    return "loot"
  elif is_stage_battle():
    return "battle"
  elif is_battle_end():
    return "battle end"
  elif is_stage_levelup():
    return "Levelup"
  elif is_stage_boss():
    return "Boss"
  elif is_stage_shop():
    return "Shop"
  elif is_stage_shoplist():
    return "Shop List"
  elif is_stage_mine():
    return "Mine"
  return None
