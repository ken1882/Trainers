# Defines the consts of pixels/color of app
Version = "0.1.0"

FrozenDetectorPixel = [[274,64], [267,66], [246,65], [125,776], [255,65]]

StageSlimePixel = [[32, 119], [413, 99], [61, 828], [423, 831], [384, 753], [202, 531]]
StageSlimeColor = [(52, 67, 40), (52, 68, 41), (49, 65, 38), (50, 65, 39), (63, 70, 62), (236, 156,54)]

StageSlimeOverPixel = [[73, 414], [385, 431], [146, 284], [278, 269], [329, 284], [202, 590]]
StageSlimeOverColor = [(145, 123, 78), (141, 119, 74), (255, 236, 175), (255, 236, 175), (255, 236, 175), (240, 155, 55)]

SlimeOKPos = [236, 530]
SlimeScrollPos = [285, 759]
SlimeGridBoundY = 245
SlimeOverOKPos = [232, 587]

SlimeGridPos = [
  [48, 286], [148, 286], [242, 286], [335, 286], 
  [48, 386], [148, 386], [242, 386], [335, 386], 
  [48, 478], [148, 478], [242, 478], [335, 478], 
  [48, 570], [148, 570], [242, 570], [335, 570]
]

SlimeImages = ["assets/{}.png".format(str(2**i)) for i in range(1,15)]
SlimeColors = [
  (255,0,0),(0,255,0),(0,0,255),
  (255,255,0),(0,255,255),(255,0,255),
  (128,32,128),(128,128,32),(0,0,0),
  (180,180,90),(180,90,180),(90,180,180),
  (0xf0,0x0f8,0x0ff),(0x07f,0x0ff,00),(0x047,0x063,0xff),
  (0x0f5,0x0f5,0x0dc),(0xff,0xe4,0xc4),(0x8a,0x02b,0x0e2),
  (0x0a5,0x02a,0x02a),(0x0de,0x0e8,0x087),(0x05f,0x09e,0x0a0)
]

StageStrawPixel = [[197, 86], [299, 94], [394, 246], [435, 619], [203, 534]]
StageStrawColor = [(61, 47, 31), (61, 47, 31), (36, 55, 19), (64, 74, 35), (238, 154, 60)]

StrawPathPosA  = [[290, 354], [284,353]]
StrawPathPosB  = [[290, 472], [286,474]]
StrawPathPosC  = [[290, 606], [280,607]]
StrawPathColor = [(152, 185, 88), (155, 185, 88), (159, 183, 88)]

StageStrawGamePixel = [[166, 85], [298, 84], [42, 615]]
StageStrawGameColor = [(151, 117, 77), (151, 117, 77), (159, 183, 90)]

StageStrawOverPixel = [[279, 280], [150, 295], [60, 435], [408, 444], [184, 94], [203, 585]]
StageStrawOverColor = [(255, 236, 175), (255, 236, 175), (144, 122, 78), (144, 122, 78), (61, 47, 31), (238, 154, 60)]
StrawReadyPos  = [233,531]
StrawOverOKPos = [232, 587]

StageMiniGameSelectionPixel = [[47, 173], [70, 154], [293, 167], [316, 163], [224, 169], [429, 811], [393, 736]]
StageMiniGameSelectionColor = [(82, 102, 198), (201, 68, 75), (83, 103, 199), (203, 66, 73), (240, 240, 142), (255, 255, 75), (238, 238, 228)]
MiniGameEnterPos = [399, 525]


TokenNumberPos = [334, 821, 377, 840]

EventPixel      = [[110,245],[122,334]]
EventColor      = [(239,156,53),(159,129,80)]
EventOK         = [242,649]

StageBattlePixel = [[24,765], [239,83], [309, 53]]
StageBattleColor = [(59,234,255),(110,85,37), (212,45,18)]

StageBattleEndPixel = [[49,321], [241,491], [440,352]]
StageBattleEndColor = [(231,233,89), (93,61,16), (238,175,65)]

StageBattleLostPixel = [[110, 503], [270, 443], [360, 528], [309, 301], [314, 276]]
StageBattleLostColor = [(111, 105, 84), (235, 223, 198), (151, 145, 127), (192, 192, 192), (0, 0, 0)]

BattleReadyPixel  = [[405,444], [41,441]]
BattleReadyColor  = [(103,90,45), (102,89,44)]

ActionContinue  = EventOK
ActionBattle    = [[100,476], [231,386], [372,475]]

StageLootPixel  = [[11,342],[240,285]]
StageLootColor  = [(191,176,107),(255,236,178)]

StageNoStaminaPixel = [[64,418], [43,322], [397,390], [157,341]]
StageNoStaminaColor = [(93,76,50), (255,236,176), (212,199,159), (255,241,216)]
ActionNoStaminaOK   = [237,551]

StageShopListPixel = [[28,214], [304,306], [41,654]]
StageShopListColor = [(254,237,177), (102,89,43), (203,186,137)]

StageMinePixel = [[31,149], [151,155], [398,835], [278,817]]
StageMineColor = [(254,235,175), (254,235,175), (251,232,173), (255,255,248)]

StageLoadingPixel = [[23,79], [74, 417], [264,178], [191, 705], [427, 816], [284, 343]]
StageLoadingColor = [(52,44,34), (49, 40, 28), (62,53,45), (65,61,55), (54,44,32), (46,36,24)]

LevelLeavePos   = [60,822]

StageLevelupPixel = [[236,392], [146,451]]
StageLevelupColor = [(255,226,76), (243,51,64)]

InventoryPos     = [435,170]
InventoryBackPos = [395,140]

AppClosePos  = [81,12]
AppIconPos   = [[302,178], [402,178]]
AppIconPixel = [[323, 180], [286, 150]]
AppIconColor = [(255, 244, 228), (84, 132, 195)]
AppLoginPos  = [239,639]

StageFarmPixel = [[285,64], [55,186], [244,815], [406,725]]
StageFarmColor = [(103,90,44), (249,86,80), (176,161,115), (158,204,89)]

StageNoInternetPixel = [[217,182], [255,681], [188,535], [335,538], [43,320], [156,329]]
StageNoInternetColor = [(0,0,0), (0,0,0), (176,161,115), (179,161,115), (255,236,176), (255,241,216)]
NoInternetOKPOS = [172,537]

ToTownPos = [415,785]

SlimeScorePos = [337, 178, 424, 200]
LeaveGamePos = [56, 759]
LeaveGameConfirm = [164, 549]

StageLevelPixel = [[69, 439], [233, 322], [341, 411], [238, 760], [429, 766]]
StageLevelColor = [(100, 160, 106), (101, 182, 136), (73, 130, 138), (59, 40, 19), (255, 255, 255)]