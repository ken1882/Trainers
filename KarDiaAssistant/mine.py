import G, const, util, action, stage, Input
from G import uwait

VK_RBUTTON = 0x2

def update():
  if len(G.OreLocation) < 2:
    print("Press mouse-right button to record mine position and start position")
    if Input.is_trigger(VK_RBUTTON):
      pos = util.get_app_cursor_pos()
      G.OreLocation.append(pos)
      if len(G.OreLocation) == 1:
        print("Recorded Ore position:", pos)
      else:
        print("Recorded start button position:", pos)
  elif stage.is_stage_mine():
    action.random_click(*G.OreLocation[0])
    uwait(0.5)
    action.random_click(*G.OreLocation[1])
    uwait(0.5)
  return True
