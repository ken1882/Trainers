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
  a = is_pixel_match(const.StageMainMenuPixel, const.StageMainMenuColor)
  b = is_pixel_match(const.StageMainMenuPixelB, const.StageMainMenuColorB)
  return a or b

def is_stage_achievement():
  if is_stage_ok(1):
    return True
  return is_pixel_match(const.StageAchievementPixel, const.StageAchievementColor)

def is_stage_backup_ok():
  if is_stage_ok(2):
    return True
  a = is_pixel_match(const.StageBackupCompletePixel, const.StageBackupCompleteColor)
  b = is_pixel_match(const.StageBackupCompletePixelB, const.StageBackupCompleteColorB)
  return a or b

def is_stage_autocombat_ok():
  if is_stage_ok(3):
    return True
  for pix, col in zip(const.StageAutoCombatCompletePixel, const.StageAutoCombatCompleteColor):
    if is_pixel_match(pix, col):
      return True
  return False

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
  a = is_pixel_match(const.StageMaxDollReachedPixel, const.StageMaxDollReachedColor)
  b = is_pixel_match(const.StageMaxDollReachedPixelB, const.StageMaxDollReachedColorB)
  return a or b

def is_stage_enhance():
  if is_stage_ok(10):
    return True
  return is_pixel_match(const.StageDollEnhancePixel, const.StageDollEnhanceColor)

def is_stage_repair():
  if is_stage_ok(11):
    return True
  return is_pixel_match(const.StageRepairPixel, const.StageRepairColor)

def is_stage_combat_map():
  if is_stage_ok(18):
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

def is_stage_player_turn():
  if is_stage_ok(17):
    return True
  return is_pixel_match(const.StagePlayerTurnPixel, const.StagePlayerTurnColor)

def is_stage_combat_event():
  if is_stage_ok(12):
    return True
  a = is_pixel_match(const.StageCombatEventPixel, const.StageCombatEventColor)
  b = is_pixel_match(const.StageCombatEventPixelB, const.StageCombatEventColorB)
  return a or b

def is_stage_formation():
  if is_stage_ok(19):
    return True
  return is_pixel_match(const.StageFormationPixel, const.StageFormationColor)

def is_stage_formation_edit():
  if is_stage_ok(20):
    return True
  return is_pixel_match(const.StageFormationEditPixel, const.StageFormationEditColor)

def is_stage_annoucement():
  if is_stage_ok(21):
    return True
  return is_pixel_match(const.StageAnnoucementPixel, const.StageAnnoucementColor)

def is_stage_reward():
  if is_stage_ok(22):
    return True
  return is_pixel_match(const.StageRewardPixel, const.StageRewardColor)

def is_stage_desktop():
  if is_stage_ok(23):
    return True
  return is_pixel_match(const.StageDesktopPixel, const.StageDesktopColor)

def is_engine_starting():
  if is_stage_ok(24):
    return True
  return is_pixel_match(const.StageEngineStartingPixel, const.StageEngineStartingColor)

def is_connection_timeout():
  if is_stage_ok(25):
    return True
  a = is_pixel_match(const.StageConnectionTimeoutPixel, const.StageConnectionTimeoutColor)
  b = is_pixel_match(const.StageConnectionTimeoutPixelB, const.StageConnectionTimeoutColorB)
  return a or b

def is_stage_team_selected():
  if is_stage_ok(26):
    return True
  return is_pixel_match(const.StageTeamSelectedPixel, const.StageTeamSelectedColor)

def is_stage_retire():
  if is_stage_ok(27):
    return True
  return is_pixel_match(const.StageRetirePixel, const.StageRetireColor)

def is_stage_game_events():
  if is_stage_ok(28):
    return True
  return is_pixel_match(const.StageGameEventsPixel, const.StageGameEventsColor)

def is_stage_event_level_selection():
  if is_stage_ok(29):
    return True
  return is_pixel_match(const.StageEventLevelPixel, const.StageEventLevelColor)

def is_force_replaced_checked():
  util.flush_screen_cache()
  return is_pixel_match(const.ForceReplaceCheckedPixel, const.ForceReplaceCheckedColor)

def get_stage_cache(sid):
  if LastFrameCount != G.FrameCount:
    cache_stage(sid)
  return CurStage

def cache_stage(sid):
  global LastFrameCount, CurStage
  if LastFrameCount != G.FrameCount:
    LastFrameCount = G.FrameCount
    CurStage = sid

def is_nextclick_needed():
  if G.ActionFiber or G.LaterFiber:
    return False
  Fmethods = [
    is_stage_combat_event, is_stage_engaging, is_stage_neutralized,
    is_stage_team_selected, is_stage_loading
  ]
  for method in Fmethods:
    if method():
      return False
  return True

def is_in_battle():
  methods = [
    is_stage_combat_event, is_stage_engaging, is_stage_victory, 
    is_stage_neutralized, is_stage_combat_map
  ]
  for method in methods:
    if method():
      return True
  return False

def is_resources_checking_stage():
  if is_stage_repair():
    return True
  if is_stage_combat_selection():
    return True
  if is_stage_formation():
    return True

def detect_player_turn():
  for pix, col in zip(const.StagePlayerTurnDetectorPixels, const.StagePlayerTurnDetectorColors):
   if is_pixel_match(pix, col):
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
  17: is_stage_player_turn,
  18: is_stage_combat_map,

  19: is_stage_formation,
  20: is_stage_formation_edit,

  21: is_stage_annoucement,
  22: is_stage_reward,

  23: is_stage_desktop,
  24: is_engine_starting,
  25: is_connection_timeout,

  26: is_stage_team_selected,
  27: is_stage_retire,

  28: is_stage_game_events,

  29: is_stage_event_level_selection,
}

def update():
  global CurStage, LastFrameCount
  if G.AppHwnd == 0:
    print("App not yet ready")
    LastFrameCount = -1
    return
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
  elif is_stage_player_turn():
    return "Player turn"
  elif is_stage_combat_map():
    return "Combat Map"  
  elif is_stage_loading():
    return "Loading"
  elif is_stage_victory():
    return "Victory"
  elif is_stage_engaging():
    return "Engaging"
  elif is_stage_neutralized():
    return "Enemy Neutralized"
  elif is_stage_formation():
    return "Formation"
  elif is_stage_formation_edit():
    return "Formation Edit"
  elif is_stage_annoucement():
    return "Annoucement"
  elif is_stage_game_events():
    return "Game Events Board"
  elif is_stage_reward():
    return "Reward"
  elif is_stage_desktop():
    return "Desktop"
  elif is_engine_starting():
    return "Engine Starting"
  elif is_connection_timeout():
    return "Connection Timeout"
  elif is_stage_team_selected():
    return "Team selected"
  elif is_stage_retire():
    return "Retire"
  elif is_stage_event_level_selection():
    return "Event Levels"
  return None

def is_correct_level_selected():
  try:
    pix, col = const.LevelSelectedPixel[G.GrindLevel], const.LevelSelectedColor[G.GrindLevel]
  except KeyError:
    print("Warning: {} has no level selection check!".format(G.GrindLevel))
    return True
  return is_pixel_match(pix, col)

def is_ammo_enough():
  for pix, col in zip(const.MainGunnerAmmoPixel, const.MainGunnerAmmoColor):
    print(pix)
    a, b = util.getPixel(*pix), col
    print(is_color_ok(a, b), a, b)
    if is_color_ok(util.getPixel(*pix), col):
      return True
  return False