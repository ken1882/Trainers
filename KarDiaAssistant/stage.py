import G, util, const

ColorRange = 25

def any_pixel_match(pix, col, inverse=False):
  for pos in pix:
    tx, ty = pos
    ok = is_color_ok(util.getPixel(tx, ty), col)
    if G.FlagDebug:
      print(ok, ok ^ inverse)
    if ok ^ inverse:
      return True
  return False

def is_color_ok(cur, target):
  for c1,c2 in zip(cur,target):
    if G.FlagDebug and G.FlagVerbose:
      print('-'*10)
      print(c1, c2)
    if abs(c1 - c2) > ColorRange:
      return False
  return True

def is_pixel_match(pix, col):
  for i, j in zip(pix, col):
    tx, ty = i
    if not is_color_ok(util.getPixel(tx, ty), j):
      return False
  return True

def is_stage_slime():
  return is_pixel_match(const.StageSlimePixel, const.StageSlimeColor)

def is_stage_minigames():
  a = is_pixel_match(const.StageMiniGameSelectionPixel, const.StageMiniGameSelectionColor)
  b = is_pixel_match(const.StageMiniGameSelectedPixel, const.StageMiniGameSelectedColor)
  return a or b

def has_event():
  return is_pixel_match(const.EventPixel, const.EventColor)

def is_stage_map():
  # todo
  return False

def is_stage_loot():
  return is_pixel_match(const.StageLootPixel, const.StageLootColor)

def is_battle_end():
  a = is_pixel_match(const.StageBattleLostPixel, const.StageBattleLostColor)
  b = is_pixel_match(const.StageBattleEndPixel, const.StageBattleEndColor)
  return a or b

def is_stage_level():
  return is_pixel_match(const.StageLevelPixel, const.StageLevelColor)

def is_stage_battle():
  return is_pixel_match(const.StageBattlePixel, const.StageBattleColor)

def is_stage_levelup():
  return is_pixel_match(const.StageLevelupPixel, const.StageLevelupColor)

def is_no_stamina():
  return is_pixel_match(const.StageNoStaminaPixel, const.StageNoStaminaColor)

def is_stage_mine():
  return is_pixel_match(const.StageMinePixel, const.StageMineColor)

def is_stage_farm():
  return is_pixel_match(const.StageFarmPixel, const.StageFarmColor)

def is_stage_loading():
  return is_pixel_match(const.StageLoadingPixel, const.StageLoadingColor)

def is_stage_disconnected():
  return is_pixel_match(const.StageNoInternetPixel, const.StageNoInternetColor)

def is_battle_ready():
  return is_stage_battle() and is_pixel_match(const.BattleReadyPixel, const.BattleReadyColor)

def is_stage_pudding():
  return is_pixel_match(const.StagePuddingPixel, const.StagePuddingColor)

def is_pudding_token_enough():
  return is_color_ok(util.getPixel(*const.PuddingTokenPixel), const.PuddingTokenColor)

def get_current_stage():
  if is_no_stamina():
    return "No Stamina!"
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
  elif is_stage_mine():
    return "Mine"
  elif is_stage_loading():
    return "Loading"
  elif is_stage_slime():
    return "Slime mini game"
  elif is_stage_minigames():
    return "Minigame selection"
  elif is_stage_pudding():
    return "Pudding slime garden"
  return None
