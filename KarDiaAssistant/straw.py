import const, util, action, G, stage, random

CDT = 10
ClickCD = [0, 0, 0]

def determine_jump():
  for i, pos in enumerate(const.StrawPathPos):
    if ClickCD[i] > 0:
      ClickCD[i] -= 1
    if ClickCD[i] == 0 and not stage.is_color_ok(util.getPixel(*pos), const.StrawPathColor[i]):
      action.random_click(*pos, G.DefaultRandRange / 2)
      ClickCD[i] = CDT

def is_stage_prepare():
  return stage.is_pixel_match(const.StageStrawPixel, const.StageStrawColor)

def is_stage_game():
  return stage.is_pixel_match(const.StageStrawGamePixel, const.StageStrawGameColor)

def is_game_over():
  return stage.is_pixel_match(const.StageStrawOverPixel, const.StageStrawOverColor)