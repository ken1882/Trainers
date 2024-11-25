import _G,stage
from _G import resume, resume_from, pop_fiber_ret, wait, uwait, log_info
import Input, position, graphics
from random import randint
import action, utils
import math
import win32con
from datetime import datetime, timedelta

TargetResources = None
def init_node():
  global TargetResources
  gt = _G.ARGV.gather_target
  if gt:
    candidate = [0, None]
    for iname in dir(position):
      if not iname.startswith('GT_'):
        continue
      r = utils.diff_string(iname, gt)
      if r > candidate[0]:
        candidate = [r, iname]
    TargetResources = getattr(position, candidate[1])
    _G.log_info("Gathering target set to:", candidate[1])

def get_nearest_node(nodes):
  cpos = stage.get_coord(force_correct=True)
  cur_node = min(
    nodes,
    key=lambda a: math.hypot(cpos[0]-a[0][0], cpos[1]-a[0][1])
  )
  return cur_node

def next_node(depth=0):
  global TargetResources
  cpos = stage.get_coord()
  cur_node = None
  while not cur_node:
    try:
      cur_node = get_nearest_node(TargetResources)
    except Exception as e:
      depth += 1
      _G.log_error("Unable to resolve coordinate:", e)
      _G.log_info("Retry, depth:",depth)
      if depth > 3:
        _G.log_error("Give up resolve coordinate")
        action.mount()
        return
  _G.log_info("Current nearest node:", cur_node[0])
  for mov in cur_node[1:]:
    k, v = mov
    if k == 'rotate':
      if v > 0:
        action.rotate_right(v)
      else:
        action.rotate_left(abs(v))
    elif k == 'forward':
      gap = 1
      times = v // gap
      Input.key_down(ord('W'))
      for _ in range(times):
        wait(gap)
        Input.trigger_key(win32con.VK_SPACE)
      wait(v-times*gap)
      Input.key_up(ord('W'))
      # action.move_forward(v)
    elif k == 'backward':
      action.move_backward(v)
    elif k == 'mount':
      action.mount()
      uwait(2.5)
    uwait(0.3)
    yield

def start_gather_fiber():
  last_dist = 0
  depth = 0
  idle_cnt = 0
  while True:
    action.target_object()
    yield
    if idle_cnt >= 10:
      action.rotate_right(0.1)
    if not stage.has_targeted_object():
      uwait(0.1)
      idle_cnt += 1
      continue
    idle_cnt = 0
    dist = stage.get_distance(fallback=99)
    last_dist = dist
    _G.log_info(f"Target detected, distance={dist}")
    action.lockon_target()
    uwait(0.3)
    action.auto_walk()
    while dist > 3.5:
      yield
      last_dist = dist
      dist = stage.get_distance(fallback=99)
      delta = abs(last_dist - dist)
      while delta > 20:
        _G.flush()
        dist = stage.get_distance(fallback=99)
        delta = abs(last_dist - dist)
        depth += 1
        if depth >= 10:
          depth = 0
          dist = 1
          break
      if delta == 0:
        depth += 1
        if depth >= 10:
          depth = 0
          dist = 1
      _G.log_info(f"Target detected, distance={dist}")
    _G.log_info("Start gathering")
    action.interact()
    uwait(2)
    action.interact()
    while stage.has_targeted_object():
      action.interact()
      uwait(2.5)
      yield
    _G.log_info("Gathering complete")
    uwait(3)
    if TargetResources:
      _G.log_info("Process to next node")
      yield from next_node()

def get_fish_brightness():
  sx, sy = position.FishRect[0], position.FishRect[1]
  ex, ey = position.FishRect[2], position.FishRect[3]
  cx, cy = sx, sy
  psum, pcnt = 0, 0
  step = 10
  while True:
    psum += sum(graphics.get_pixel(cx, cy, True)) / 3
    pcnt += 1
    cx += step
    if cx > ex:
      cy += step
      if cy >= ey:
        break
  return psum / pcnt

def is_fish_available():
  cx, cy = position.FishAvailable
  return sum(graphics.get_pixel(cx, cy, True)) / 3 > 80

def start_fish_fiber():
  MOV_TIMES = 30
  last_mov  = 0
  last_brg  = 255
  cnt       = 1
  pf_key    = _G.ARGV.patience_fishing
  flag_patience = False
  flag_mooch    = False
  try:
    times = int(_G.ARGV.repeats)
  except Exception:
    times = 0x7fffffff
  _G.log_info(f"Start fishing {cnt}/{times}")
  Input.trigger_key(ord('2'))
  wait(1)
  while times != 0:
    yield
    brg = get_fish_brightness()
    # print(last_brg, brg)
    if brg - last_brg > 15:
      _G.log_info("Pull line")
      if flag_patience and pf_key:
        vk = ord('5' if flag_mooch else pf_key)
        Input.trigger_key(vk)
      uwait(0.1)
      Input.trigger_key(ord('3'))
      while not is_fish_available():
        uwait(1)
      uwait(3)
      if cnt % MOV_TIMES == 0:
        _G.log_info("Switch position")
        action.quit_fishing()
        uwait(2)
        if last_mov:
          last_mov = 0
          action.move_left(2)
        else:
          last_mov = 1
          action.move_right(2)
        uwait(1)
      if stage.is_gp_half() and stage.is_thaliak_available():
        _G.log_info("Recover GP")
        Input.trigger_key(ord('R'))
        uwait(2)
      if stage.is_mooch_available():
        _G.log_info("Mooch")
        flag_mooch = True
        Input.trigger_key(ord('V'))
      elif cnt < times:
        if stage.is_gp_full():
          if pf_key:
            _G.log_info("Use Patience")
            Input.trigger_key(ord('E'))
            flag_patience = datetime.now()
          else:
            _G.log_info("Use Chum")
            Input.trigger_key(ord('Q'))
          uwait(2)
        cnt += 1
        if cnt >= times:
          break
        if flag_patience and datetime.now() < flag_patience+timedelta(seconds=60):
          _G.log_info("Patience activated, preferred hook key:", pf_key)
        else:
          flag_patience = None
        _G.log_info(f"Start fishing {cnt}/{times}")
        Input.trigger_key(ord('2'))
        flag_mooch = False
      uwait(2)
      brg = get_fish_brightness()
    last_brg = brg
  _G.log_info("End fishing")

def start_crafting_fiber():
  delta = int(_G.ARGV.crafting_delta)
  times = int(_G.ARGV.repeats)
  for i in range(times):
    _G.log_info(f"Start craft #{i+1}")
    for _ in range(3):
      action.interact()
      uwait(1)
    cp = mcp = int(_G.ARGV.crafting_cp)
    hp, mhp = 999,-1
    pp, mpp = 999,-1
    step = 0
    vene_step = 0
    nwaste_step = 0
    uwait(1)
    action.interact()
    seq = _G.ARGV.crafting_sequence
    if seq:
      seq = seq.upper()
      for ch in seq:
        uwait(3.5)
        yield
        _G.log_info("Sequential:", ch)
        Input.trigger_key(ord(ch))
      _G.log_info("Crafting complete")
      uwait(6.5)
      continue
    while True:
      step += 1
      uwait(3)
      yield
      hp = mhp if hp > mhp else hp
      cp = mcp if cp > mcp else cp
      _G.flush()
      _G.log_info(f"Step #{step}, CP: {cp}/{mcp}")
      if cp < mcp and stage.is_cp_recoverable():
        _G.log_info("Recover CP")
        Input.trigger_key(ord('E'))
        cp += 20
        continue
      if mhp == -1:
        php = stage.get_craft_durability()
        hp  = php[0]
        mhp = php[1]
      if mpp == -1:
        ppp = stage.get_craft_progress()
        pp  = ppp[0]
        mpp = ppp[1]
      _G.log_info(f"Durability: {hp}/{mhp}")
      if stage.is_durability_recoverable() and \
        mhp - hp >= 30 and \
        (nwaste_step < step or hp <= 5):
        _G.log_info("Recover durability")
        Input.trigger_key(ord('3'))
        cp -= 88
        hp += 30
        continue
      _G.log_info(f"Progress: {pp}/{mpp}")
      if mpp - pp > delta*3 and vene_step < step:
        _G.log_info("Veneration")
        cp -= 18
        Input.trigger_key(ord('T'))
        vene_step = step+4
        continue
      if step > nwaste_step and hp >= 25 and cp >= 56:
        _G.log_info("Waste not")
        Input.trigger_key(ord('R'))
        cp -= 56
        nwaste_step = step+4
        continue
      if pp+delta >= mpp or (step <= vene_step and pp+int(delta*1.5) >= mpp):
        if stage.is_max_hq() or step > nwaste_step and hp == 10 or hp <= 5:
          _G.log_info("Final progress")
          Input.trigger_key(ord('1'))
          hp -= 10 if step > nwaste_step else 5
          break
        else:
          if 18 <= cp and cp < 56 and hp <= 30:
            _G.log_info("Basic touch")
            cp -= 18
            Input.trigger_key(ord('2'))
          else:
            _G.log_info("Hasty touch")
            Input.trigger_key(ord('4'))
          hp -= 10 if step > nwaste_step else 5
          continue
      _G.log_info("Progress")
      Input.trigger_key(ord('1'))
      hp -= 10 if step > nwaste_step else 5
      pp += delta if step > vene_step else int(delta*1.5)
    _G.log_info("Crafting complete")
    uwait(5)
  uwait(1)
  Input.trigger_key(win32con.VK_ESCAPE)

def do_battle_rotation():
  Input.trigger_key(ord('1'))
  wait(1.6)

def start_combat_fiber():
  idle_cnt = 0
  oor_cnt  = 0
  flag_engaging = False
  if _G.ARGV.enable_rotation:
    _G.log_info("Idle camera rotation enable")
  while True:
    uwait(0.1)
    yield
    if not stage.is_enemy_targeted():
      action.target_enemy()
      idle_cnt += 1
      _G.log_info(f"No enemy detected, idle#{idle_cnt}")
      if _G.ARGV.enable_rotation and idle_cnt >= 10:
        idle_cnt = 0
        action.camera_right(0.5)
      continue
    idle_cnt = 0
    do_battle_rotation()
    flag_engaging = stage.is_enemy_awared()
    if not flag_engaging:
      _G.log_info("Target seems out of range")
      oor_cnt += 1
      if oor_cnt > 3:
        _G.log_info("Target OOR, switch target")
        oor_cnt = 0
        if _G.ARGV.enable_rotation:
          action.camera_right(0.3)
        action.target_enemy()
    else:
      _G.log_info("Engaging")
      oor_cnt = 0

def start_logout_gathering_fiber():
  target = _G.ARGV.gather_target
  candidate = [0, None]
  login_wtime = 1
  ntarget_cnt = 0
  for key in position.LGT_DICT:
    r = utils.diff_string(key, target)
    if r > candidate[0]:
      candidate = [r, key]
  target = position.LGT_DICT[candidate[1]]
  _G.log_info("Gathering", candidate[1])
  flag_crowded = False
  while True:
    _G.log_info("Logout")
    depth = 0
    while depth == 0 or stage.is_stage('SceneMap'):
      uwait(0.5)
      yield
      action.logout()
      for _ in range(50):
        action.target_player()
        Input.key_down(win32con.VK_RIGHT)
        wait(0.5)
        Input.key_up(win32con.VK_RIGHT)
        if stage.is_player_targeted():
          _G.log_info("Other player detected")
          flag_crowded = True
        yield
      depth += 1
      if depth > 5:
        _G.log_error("Unable to logout (?)")
        exit(1)
    if flag_crowded:
      login_wtime += 300
    else:
      login_wtime = 1
    if ntarget_cnt >= 5:
      _G.log_error("Seems away from gathering area, exit")
      exit(1)
    _G.log_info("Wait time:", login_wtime)
    uwait(login_wtime)
    flag_crowded = False
    _G.log_info("Start game")
    Input.rmoveto(*position.GameStart)
    for _ in range(2):
      uwait(0.3)
      yield
      Input.click(use_msg=False)
    while not stage.is_stage('CharacterSelection'):
      uwait(1)
      yield
    _G.log_info("Login")
    uwait(0.3)
    Input.rmoveto(*position.FirstCharacter)
    yield
    for _ in range(2):
      uwait(0.3)
      Input.click(use_msg=False)
      yield
    uwait(0.3)
    # Input.rmoveto(*position.GeneralOK)
    Input.rmoveto(*position.LoginOK)
    yield
    uwait(0.3)
    Input.click(use_msg=False)
    _G.log_info("Login OK")
    while not stage.is_stage('SceneMap'):
      uwait(0.5)
      yield
    for _ in range(3):
      Input.trigger_key(win32con.VK_ESCAPE)
      yield
    node = None
    try:
      node = get_nearest_node(target['nodes'])
    except Exception:
      pass
    jump_cnt = []
    if node:
      _G.log_info("Current node:", node[0])
      for k,v in node[1:]:
        if k == 'rotate':
          if v > 0:
            action.rotate_right(v)
          else:
            action.rotate_left(abs(v))
        elif k == 'cam_rotate':
          if v > 0:
            Input.scroll_to(500, 500, 500+v, 500, mright=1)
          else:
            Input.scroll_to(700, 500, 700-v, 500, mright=1)
        elif k == 'jump':
          jump_cnt.append(v)
        elif k == 'backward':
          action.move_backward(v)
        elif k == 'left':
          action.move_left(v)
    uwait(0.3)
    _G.log_info("Start gathering")
    depth = 0
    action.target_object()
    uwait(0.5)
    yield
    if target.get('disableAutoFind') and not stage.has_targeted_object():
      _G.log_info("No target found, skip")
      ntarget_cnt += 1
      continue
    else:
      while not stage.has_targeted_object():
        action.rotate_right(0.3 if depth else 0)
        uwait(0.1)
        yield
        action.target_object()
        uwait(0.3)
        yield
        depth += 1
        if depth > 20:
          _G.log_error("Unable to find resource node")
          Input.rmoveto(*position.ReturnPos)
          uwait(0.3)
          Input.rmoveto(*position.GeneralOK)
          uwait(0.3)
          Input.click(use_msg=False)
          exit(1)

    dist = stage.get_distance(fallback=99)
    last_dist = dist
    depth = 0
    _G.log_info(f"Target detected, distance={dist}")
    ntarget_cnt = 0
    if not target.get('disableLock'):
      action.lockon_target()
      uwait(0.3)
      action.auto_walk()
      counter = 0
      while dist > 3.5:
        yield
        counter += 1
        last_dist = dist
        dist = stage.get_distance(fallback=99)
        delta = abs(last_dist - dist)
        if counter in jump_cnt:
          Input.trigger_key(win32con.VK_SPACE)
        while delta > 20:
          _G.flush()
          dist = stage.get_distance(fallback=99)
          delta = abs(last_dist - dist)
          depth += 1
          if depth >= 10:
            depth = 0
            dist = 1
            break
        if delta == 0:
          depth += 1
          if depth >= 10:
            depth = 0
            dist = 1
        _G.log_info(f"Target detected, distance={dist}")
    elif dist < 50 and dist > 3:
      _G.log_info("Stationary gather unreachable, skip")
      continue
    uwait(1)
    yield
    action.interact()
    uwait(0.5)
    yield
    # enable auto gather
    if not graphics.is_color_ok(graphics.get_pixel(*position.AutoGatherPos, sync=1), position.AutoGatherEnabledColor):
      Input.rmoveto(89, 628)
      yield
      Input.click(use_msg=False)
      yield
    target_exists = True
    if 'hidden' in target:
      target_exists = graphics.is_color_ok(graphics.get_pixel(*target['hidden'][0], sync=1), target['hidden'][1])
      _G.log_info(f"Target exists: {target_exists}")
    if target_exists:
      Input.rmoveto(*target['mpos'])
      yield
      Input.click(use_msg=False)
      sk = target.get('skill')
      if sk:
        if sk in position.GatherSkillUsable:
          sp, sc = position.GatherSkillUsable[sk]
          uwait(0.3)
          if graphics.is_pixel_match((sp,), (sc,), sync=True):
            _G.log_info(f"Use gather skill {sk}")
            Input.trigger_key(ord(sk))
            uwait(1)
        uwait(0.1)
    elif 'alts' in target:
      for pos in target['alts']:
        Input.rmoveto(*pos)
        yield
        Input.click(use_msg=False)
        yield
    for _ in range(10):
      uwait(1)
      yield
    action.target_player()
    uwait(0.5)
    yield
    if stage.is_player_targeted():
      _G.log_info("Other player detected")
      flag_crowded = True

def start_minipick_fiber():
  while True:
    yield
    action.interact2()
    uwait(0.3)
    action.interact2()
    uwait(0.5)
    action.menu_right()
    uwait(0.3)
    action.menu_up()
    uwait(0.3)
    action.interact2()
    wait(1)
    a = graphics.find_object('objs/miniball.png', 0.9)
    if not a:
      return
    a = a[0]
    px = a[0] - 805
    py = 905 - a[1]
    delta_ms_x = 0.15
    delta_ms_y = 0.13
    dtx = int(px / delta_ms_x)
    dty = int(py / delta_ms_y)
    _G.log_info(f"Press time X: {dtx}ms Y: {dty}ms")
    action.interact_press(dtx)
    wait(0.3)
    action.interact_press(dty)
    wait(5)
    uwait(3)
    if graphics.find_object('objs/minigame_success.png', 0.9):
      _G.log_info(f"Minigame success")
      Input.trigger_key(win32con.VK_ESCAPE)
      uwait(1)
    else:
      _G.log_info(f"Minigame failed")