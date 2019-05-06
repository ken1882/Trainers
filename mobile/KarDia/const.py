PWD = ""

# Program running flag
running = True
paused  = False

# Hwnd of this program
Hwnd    = 0

# Hwnd of target window
AppHwnd = 0

FPS = (1 / 120)
InternUpdateTime = 60

# Not an actually const
AppRect = [0,0,0,0]

AppWidth = 472
AppHeight = 909

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

StageLevelPixel = [[290,60], [237,755], [130,452]]
StageLevelColor = [(96,84,41), (59,40,19), (100,160,106)]

StageBossPixel = [[290,60], [319,315]]
StageBossColor = [(96,84,41), (236,99,197)]

StageShopPixel = [[449,298], [252,628]]
StageShopColor = [(139,106,96), (102,106,135)]

EventPixel      = [[110,245],[122,334]]
EventColor      = [(239,156,53),(159,129,80)]
EventOK         = [242,649]

StageBattlePixel = [[150,53],[317,52],[237,83]]
StageBattleColor = [(152,198,29), (216,46,18), (110,85,37)]

StageBattleEndPixel  = [[238,305], [238,470], [211,446]]
StageBattleEndColor  = [(235,138,85), (237,156,56), (143,129,85)]

StageLevelupPixel = [[236,392], [146,451]]
StageLevelupColor = [(255,226,76), (243,51,64)]

BattleReadyPixel  = [[405,444], [41,441]]
BattleReadyColor  = [(103,90,45), (102,89,44)]

ActionContinue  = EventOK
ActionBattle    = [[100,476], [231,386], [372,475]]
ActionBossBattle = [[92,422], [235,419], [378,408]]

StageNoTicketPixel = [[129,494], [272,494], [414,494]]
StageNoTicketColor = [(246,70,71), (244,74,71), (244,74,71)]

StageLootPixel  = [[237,291], [243,341], [11,342]]
StageLootColor  = [(255,236,178), (102,89,43), (193,176,107)]

StageNoStaminaPixel = [[42,326], [156,334], [264,548]]
StageNoStaminaColor = [(255,236,176), (255,241,216), (179,161,115)]
ActionNoStaminaOK   = [237,544]

StageShopListPixel = [[28,214], [304,306], [41,654]]
StageShopListColor = [(254,237,177), (102,89,43), (203,186,137)]

StageMinePixel = [[31,149], [151,155], [104,156], [126,149], [135,163]]
StageMineColor = [(254,235,175), (254,235,175), (222,203,149), (251,232,173), (254,235,175)]

StageLoadingPixel = [[22,74], [191,706], [358,697], [333,369], [77,453], [447,846]]
StageLoadingColor = [(53,45,36), (66,62,57), (66,66,69), (62,57,52), (49,42,30), (52,42,30)]

LevelLeavePos   = [60,822]
LevelPos        = [[20,474], [406,497]]
ShopPos         = [320,267]
BossPosA        = [53,543]
BossPosB        = [437,386]
ShopKeeperPos   = [107,452]
ItemBuyPos      = [400,549]
GoodsAmountPos  = [310,443]
ShopScrollPos   = [300,655]
ShopScrollDelta = 500
GoodsPurchasePos  = [238,505]
GoodsListLeavePos = [434,221]
ShopLeavePos      = [66,822]

InventoryPos     = [435,170]
InventoryBackPos = [395,140]
UsableItemPos    = [178,254]
ItemStickPos     = [292,332]
ItemStickUsePos  = [404,530]
ItemBreadPos     = [392,330]
ItemBreadUsePos  = [405,534]
ItemBreadColor   = (221,144,66)
UseItemAmountPos = [205,445]
UseAllItemPos    = [300,439]
UseItemOKPos     = [238,503]

FrozenDetectorPixel = [[274,64], [267,66], [246,65], [125,776], [255,65]]
AppClosePos = [81,12]
AppIconPos  = [[305,170], [405,170]]
AppIconPixel = [[288,166], [323,180]]
AppIconColor = [(255,240,208), (255,246,231)]
AppLoginPos     = [239,639]

StageFarmPixel = [[285,64], [55,186], [244,815], [406,725]]
StageFarmColor = [(103,90,44), (249,86,80), (176,161,115), (158,204,89)]

StageNoInternetPixel = [[217,182], [255,681], [188,535], [335,538], [43,320], [156,329]]
StageNoInternetColor = [(0,0,0), (0,0,0), (176,161,115), (179,161,115), (255,236,176), (255,241,216)]
NoInternetOKPOS = [172,537]

ToTownPos = [415,785]
ToEventShopPos = [224,829]

EventMapScrollPos = [400,400]
EventMapScrolldX   = 109
EventMapScrolldY   = 100