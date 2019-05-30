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

def is_maxdoll_reached():
  if is_stage_ok(9):
    return True
  return is_pixel_match(const.StageMaxDollReachedPixel, const.StageMaxDollReachedColor)

def is_stage_enhance():
  if is_stage_ok(10):
    return True
  return is_pixel_match(const.StageDollEnhancePixel, const.StageDollEnhanceColor)

def is_stage_repair():
  if is_stage_ok(11):
    return True
  return is_pixel_match(const.StageRepairPixel, const.StageRepairColor)

def is_stage_combat_map():
  if is_stage_ok(17):
    return True
  return is_pixel_match(const.StageCombatMapPixel, const.StageCombatMapColor)

def is_stage_loading():
  if is_stage_ok(13):
    return True
  return is_pixel_match(const.StageLoadingPixel, const.StageLoadingColor)

def is_stage_victory():
  if is_stage_ok(14):
    return True
  return is_pixel_match(const.StageVictoryPixel, const.StageVictoryColor)

def is_stage_engaging():
  if is_stage_ok(15):
    return True
  for pixs, clrs in zip(const.StageEngagingPixels, const.StageEngagingColors):
    if is_pixel_match(pixs, clrs):
      return True
  return False

def is_stage_neutralized():
  if is_stage_ok(16):
    return True
  return is_pixel_match(const.StageNeutralizedPixel, const.StageNeutralizedColor)

def is_stage_enemy_turn():
  if is_stage_ok(18):
    return True
  return is_pixel_match(const.StageEnemyTurnPixel, const.StageEnemyTurnColor)

def is_stage_combat_event():
  if is_stage_ok(12):
    return True
  a = is_pixel_match(const.StageCombatEventPixel, const.StageCombatEventColor)
  b = is_pixel_match(const.StageCombatEventPixelB, const.StageCombatEventColorB)
  return a or b

def get_stage_cache(sid):
  if LastFrameCount != G.FrameCount:
    cache_stage(sid)
  return CurStage

def cache_stage(sid):
  global LastFrameCount, CurStage
  if LastFrameCount != G.FrameCount:
    LastFrameCount = G.FrameCount
    CurStage = sid

def is_in_battle():
  methods = [
    is_stage_combat_event, is_stage_engaging, is_stage_victory, 
    is_stage_neutralized, is_stage_combat_map, is_stage_enemy_turn,
  ]
  for method in methods:
    if method():
      return True
  return False

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
  9: is_maxdoll_reached,
  10: is_stage_enhance,
  11: is_stage_repair,
  13: is_stage_loading,
  14: is_stage_victory,
  15: is_stage_engaging,
  16: is_stage_neutralized,

  12: is_stage_combat_event,
  17: is_stage_combat_map,
  18: is_stage_enemy_turn,
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
  elif is_maxdoll_reached():
    return "Max doll reached"
  elif is_stage_enhance():
    return "Enhance"
  elif is_stage_autocombat_again():
    return "Auto-combat again"
  elif is_stage_repair():
    return "Repair"
  elif is_stage_combat_event():
    return "Combat Event"
  elif is_stage_combat_map():
    return "Combat Map"
  elif is_stage_enemy_turn():
    return "Enemy turn"
  elif is_stage_loading():
    return "Loading"
  elif is_stage_victory():
    return "Victory"
  elif is_stage_engaging():
    return "Engaging"
  elif is_stage_neutralized():
    return "Enemy Neutralized"
  return None
