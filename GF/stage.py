import G, util, const

ColorRange = 25
CurStage   = -1
LastFrameCount = -1

def flush():
  global LastFrameCount, CurStage
  CurStage = -1
  LastFrameCount = -1

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

def is_stage_ok(sid=-1):
  global LastFrameCount, CurStage
  if LastFrameCount != G.FrameCount:
    return False
  return CurStage == sid

def is_stage_main_menu():
  if is_stage_ok(0):
    return True
  return is_pixel_match(const.StageMainMenuPixel, const.StageMainMenuColor)

def is_stage_achievement():
  if is_stage_ok(1):
    return True
  return is_pixel_match(const.StageAchievementPixel, const.StageAchievementColor)

def is_stage_backup_ok():
  if is_stage_ok(2):
    return True
  return is_pixel_match(const.StageBackupCompletePixel, const.StageBackupCompleteColor)

def is_stage_autocombat_ok():
  if is_stage_ok(3):
    return True
  return is_pixel_match(const.StageAutoCombatCompletePixel, const.StageAutoCombatCompleteColor)

def is_stage_combat_selection():
  if is_stage_ok(4):
    return True
  return is_pixel_match(const.StageCombatSelectionPixel, const.StageCombatSelectionColor)

def is_stage_profile():
  if is_stage_ok(5):
    return True
  return is_pixel_match(const.StageProfilePixel, const.StageProfileColor)

def is_stage_combat_setup():
  if is_stage_ok(6):
    return True
  return is_pixel_match(const.StageCombatSetupPixel, const.StageCombatSetupColor)

def is_stage_autocombat_again():
  if is_stage_ok(7):
    return True
  return is_pixel_match(const.StageAutoCombatAgainPixel, const.StageAutoCombatAgainColor)

def autocombat_reward_ok():
  if is_stage_autocombat_ok():
    return True
  if is_stage_backup_ok():
    return True
  if is_stage_main_menu():
    return True
  if is_stage_combat_selection():
    return True
  if is_stage_autocombat_again():
    return True
  return False

def is_stage_like():
  if is_stage_ok(8):
    return True
  return is_pixel_match(const.StageVisitLikePixel, const.StageVisitLikeColor)

def get_stage_cache(sid):
  if LastFrameCount != G.FrameCount:
    cache_stage(sid)
  return CurStage

def cache_stage(sid):
  global LastFrameCount, CurStage
  if LastFrameCount != G.FrameCount:
    LastFrameCount = G.FrameCount
    CurStage = sid

StageMap = {
  0: is_stage_main_menu,
  1: is_stage_achievement,
  2: is_stage_backup_ok,
  3: is_stage_autocombat_ok,
  4: is_stage_combat_selection,
  5: is_stage_profile,
  6: is_stage_combat_setup,
  7: is_stage_autocombat_again,
  8: is_stage_like,
}

def update():
  global CurStage, LastFrameCount
  LastFrameCount = G.FrameCount
  CurStage = -1
  for sid, func in StageMap.items():
    if func():
      CurStage = sid
      break

def get_current_stage():
  global CurStage, LastFrameCount
  if is_stage_main_menu():
    return "Main Menu"
  elif is_stage_achievement():
    return "Achievement"
  elif is_stage_backup_ok():
    return "Backup complete"
  elif is_stage_autocombat_ok():
    return "Auto-combat completed"
  elif is_stage_combat_selection():
    return "Combat Selection"
  elif is_stage_profile():
    return "Profile"
  elif is_stage_combat_setup():
    return "Combat Setup"
  elif is_stage_like():
    return "Visit friend like"
  return None
