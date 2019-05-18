import G, util, const

ColorRange = 25

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

def get_current_stage():
  if is_stage_slime():
    return "Slime mini game"
  return None
