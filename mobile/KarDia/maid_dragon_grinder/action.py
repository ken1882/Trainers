import util, const, random, stage

def uwait(sec, rand=True):
  if rand:
    sec += random.random()
    if sec > 0.5:
      sec -= (random.random() / 3)
  util.wait(sec)

def random_click(x, y, rrange=const.DefaultRandRange):
  if rrange is None:
    rrange = const.DefaultRandRange
  util.click(x + random.randint(-rrange,rrange), y + random.randint(-rrange,rrange))

def action_next(rrange=const.DefaultRandRange):
  mx, my = const.ActionContinue
  random_click(mx, my, rrange)

def no_stamina_ok():
  random_click(*const.ActionNoStaminaOK)

def to_battle(difficulty=0):
  difficulty = difficulty % 3
  random_click(*const.ActionBattle[difficulty])
  uwait(0.42, False)
  random_click(*const.ActionBattle[difficulty])

def to_boss_battle(loc=0):
  if loc >= 3:
    mx, my = const.ActionBattle[2]
    rrange = 25
    util.scroll_right(mx+random.randint(-rrange,rrange), my+random.randint(-rrange,rrange), 250)
    uwait(1)
    util.scroll_right(mx+random.randint(-rrange,rrange), my+random.randint(-rrange,rrange), 250)
    uwait(0.5)
  loc = loc % 3
  random_click(*const.ActionBossBattle[loc])
  uwait(0.42, False)
  random_click(*const.ActionBossBattle[loc])

def leave_level(loc=0):
  random_click(*const.LevelLeavePos)

def to_level(loc=0):
  random_click(*const.LevelPos[loc])

def purchase_item():
  x, y = const.ShopScrollPos[0] + random.randint(-8,8), const.ShopScrollPos[1] + random.randint(-8,8)
  x += random.randint(-const.DefaultRandRange, const.DefaultRandRange)
  y += random.randint(-const.DefaultRandRange, const.DefaultRandRange)
  util.scroll_down(x, y, const.ShopScrollDelta)
  uwait(2)
  random_click(*const.ItemBuyPos)
  uwait(1)
  util.click(*const.GoodsAmountPos)
  uwait(0.8)
  random_click(*const.GoodsPurchasePos)
  uwait(0.8)
  while not stage.is_stage_loot():
    uwait(1)
    yield
  action_next()
  uwait(0.5)
  random_click(*const.GoodsListLeavePos)
  uwait(0.4)

def use_recovery_item():
  random_click(*const.InventoryPos)
  uwait(1.5)
  random_click(*const.UsableItemPos)
  uwait(0.8)
  random_click(*const.ItemStickPos)
  uwait(0.3)
  random_click(*const.ItemStickUsePos)
  uwait(0.5)
  util.click(*const.UseItemAmountPos)
  uwait(0.8)
  random_click(*const.UseItemOKPos)
  uwait(0.8)
  while not stage.is_stage_loot():
    uwait(1)
    yield
  action_next()
  uwait(2)
  if stage.is_pixel_match([const.ItemBreadPos], [const.ItemBreadColor]):
    uwait(0.8)
    random_click(*const.ItemBreadPos)
    uwait(0.3)
    random_click(*const.ItemBreadUsePos)
    uwait(0.5)
    util.click(*const.UseAllItemPos)
    uwait(0.8)
    random_click(*const.UseItemOKPos)
    uwait(0.8)
    while not stage.is_stage_loot():
      uwait(1)
      yield
    action_next()
  uwait(0.8)
  close_inventory()
  uwait(2)
  

def close_inventory():
  random_click(*const.InventoryBackPos)

def leave_shop():
  random_click(*const.ShopLeavePos)