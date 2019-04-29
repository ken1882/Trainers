PWD = ""

# Program running flag
running = True

# Hwnd of this program
Hwnd    = 0

# Hwnd of target window
AppHwnd = 0

FPS = (1 / 120)

# Last Stamina Recovery time, not a const actually
LastRecoveryTime   = 0

# Flag of process recovering
FlagRecoverStamina = False

# Debug flag
FlagDebug          = False

# Mining ore location, not really a const
OreLocation        = []

# Map align: topest and left:2-F4 Flag
Mode = 0
# N   | Function
# 0   | inf. grinding at 2-G4-1, if others will stop when no stamina
# 1   | Mining Grind, press CTRL and memory ore location
# other: will stop once no stamina

# First/Advanced/Completely explore
LevelDifficulty = 0
LevelLocationID = 1
BossDifficulty  = 0

# Random range for clicking to bypass detection
DefaultRandRange = 12

StageMapPixel   = [[290,60], [61,728]]
StageMapColor   = [(96,84,41), (158,204,89)]

StageLevelPixel = [[290,60], [240,760], [130,452]]
StageLevelColor = [(96,84,41), (79,60,39), (100,160,106)]

StageBossPixel = [[290,60], [322,317]]
StageBossColor = [(96,84,41), (255,119,217)]

StageShopPixel = [[449,298], [252,628]]
StageShopColor = [(139,106,96), (102,106,135)]

EventPixel      = [[110,245],[122,334]]
EventColor      = [(239,156,53),(159,129,80)]
EventOK         = [242,649]

StageBattlePixel = [[24,765], [239,83], [309, 53]]
StageBattleColor = [(59,234,255),(110,85,37), (212,45,18)]

StageBattleEndPixel = [[49,321], [241,491], [440,352]]
StageBattleEndColor = [(231,233,89), (93,61,16), (238,175,65)]

StageLevelupPixel = [[236,392], [146,451]]
StageLevelupColor = [(255,226,76), (243,51,64)]

BattleReadyPixel  = [[405,444], [41,441]]
BattleReadyColor  = [(103,90,45), (102,89,44)]

ActionContinue  = EventOK
ActionBattle    = [[100,476], [231,386], [372,475]]
ActionBossBattle = [[92,414], [230,405], [372,413]]

StageNoTicketPixel = [[129,494], [272,494], [414,494]]
StageNoTicketColor = [(246,70,71), (244,74,71), (244,74,71)]

StageLootPixel  = [[11,342],[240,285]]
StageLootColor  = [(191,176,107),(255,236,178)]

StageNoStaminaPixel = [[64,418], [43,322], [397,390], [157,341]]
StageNoStaminaColor = [(93,76,50), (255,236,176), (212,199,159), (255,241,216)]
ActionNoStaminaOK   = [237,551]

StageShopListPixel = [[28,214], [304,306], [41,654]]
StageShopListColor = [(254,237,177), (102,89,43), (203,186,137)]

StageMinePixel = [[31,149], [151,155], [398,835], [278,817]]
StageMineColor = [(254,235,175), (254,235,175), (251,232,173), (255,255,248)]

LevelLeavePos   = [60,822]
LevelPos        = [[16,477], [406,497]]
ShopPos         = [320,267]
BossPosA        = [53,543]
BossPosB        = [437,386]
ShopKeeperPos   = [107,452]
ItemBuyPos      = [400,549]
GoodsAmountPos  = [300,443]
ShopScrollPos   = [300,655]
ShopScrollDelta = 400
GoodsPurchasePos  = [238,505]
GoodsListLeavePos = [434,221]
ShopLeavePos      = [66,822]

InventoryPos     = [435,170]
InventoryBackPos = [395,140]
UsableItemPos    = [178,254]
ItemStickPos     = [292,332]
ItemStickUsePos  = [404,530]
ItemBreadPos     = [397,327]
ItemBreadUsePos  = [405,534]
ItemBreadColor   = (221,144,66)
UseItemAmountPos = [250,445]
UseAllItemPos    = [321,444]
UseItemOKPos     = [238,503]

FrozenDetectorPixel = [[274,64], [267,66], [246,65], [125,776], [255,65]]
AppClosePos  = [81,12]
AppIconPos   = [[500,170], [600,170]]
AppIconPixel = [[488,166], [254,178]]
AppIconColor = [(255,240,208), (255,246,231)]
AppLoginPos     = [239,639]

StageFarmPixel = [[285,64], [55,186], [244,815], [406,725]]
StageFarmColor = [(103,90,44), (249,86,80), (176,161,115), (158,204,89)]

ToTownPos = [415,785]
ToEventShopPos = [224,829]

EventMapScrollPos = [400,400]
EventMapScrolldX   = 100
EventMapScrolldY   = 100