# Defines the consts of pixels/color of app
Version = "0.2.1"
AppName = ""
AppTitle = "KarDiaAssassiant"
BSTTitle = "BlueStacks Tweaker"

TargetApps = {
  "BlueStacks": [7, 47, 477, 917],
  "夜神模擬器": [1, 32, 464, 855]
}

TargetAppRegex = {
  "BlueStacks": r"^BlueStacks(?! Tweaker)",
  "夜神模擬器": r"夜神模擬器"
}

TessLanguage = {
  'en_us': 'eng',
  'zh_tw': 'chi_tra',
}
NoxSideToolBar = "通過鍵盤調節GPS方位和移動速度"

OCRDigitTrans = {
  'O': '0',
  'o': '0',
  'D': '0',
  'Z': '2',
  'z': '2',
  '.': '6',
  '/': '8',
  'B': '8',
  'J': '1',
  'j': '1',
  'I': '1',
  'i': '1'
}

DefaultCanvasResoultion = [477, 917]
BSTResoultion = [700, 400]
ScreenResoultion = [1,1]

def getAppOffset():
  if AppName == "":
    return [0, 0]
  return [TargetApps[AppName][0], TargetApps[AppName][1]]

def getAppResoultion():
  if AppName == "":
    return DefaultCanvasResoultion
  return [TargetApps[AppName][2], TargetApps[AppName][3]]
  
FrozenDetectorPixel = [[267, 17], [260, 19], [239, 18], [118, 729], [248, 18]]

StageSlimePixel = [[25, 72], [406, 52], [54, 781], [416, 784], [377, 706], [195, 484]]
StageSlimeColor = [(52, 67, 40), (52, 68, 41), (49, 65, 38), (50, 65, 39), (63,70, 62), (236, 156, 54)]
StageSlimeOverPixel = [[66, 367], [378, 384], [139, 237], [271, 222], [322, 237], [195, 543]]
StageSlimeOverColor = [(145, 123, 78), (141, 119, 74), (255, 236, 175), (255, 236, 175), (255, 236, 175), (240, 155, 55)]

SlimeOKPos = [229, 483]
SlimeScrollPos = [278, 712]
SlimeGridBoundY = 198
SlimeOverOKPos = [225, 540]

SlimeGridPos = [
  [41, 239], [141, 239], [235, 239], [328, 239], 
  [41, 339], [141, 339], [235, 339], [328, 339], 
  [41, 431], [141, 431], [235, 431], [328, 431], 
  [41, 523], [141, 523], [235, 523], [328, 523]
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

StageStrawPixel = [[190, 39], [292, 47], [387, 199], [428, 572], [196, 487]]
StageStrawColor = [(61, 47, 31), (61, 47, 31), (36, 55, 19), (64, 74, 35), (238, 154, 60)]

StrawPathPosA = [[268, 307], [270, 306]]
StrawPathPosB = [[270, 425], [272, 427]]
StrawPathPosC = [[272, 559], [274, 560]]
StrawPathColor = [(152, 185, 88), (155, 185, 88), (159, 183, 88)]

StageStrawGamePixel = [[159, 38], [291, 37], [35, 568]]
StageStrawGameColor = [(151, 117, 77), (151, 117, 77), (159, 183, 90)]
StageStrawOverPixel = [[167, 45], [284, 39], [6, 361], [159, 392], [393, 386], [48, 569], [455, 441]]
StageStrawOverColor = [(53, 39, 26), (61, 47, 31), (185, 168, 107), (120, 107, 62), (141, 119, 75), (64, 73, 36), (176, 157, 96)]

StrawReadyPos = [226, 484]
StrawOverOKPos = [225, 540]

StageMiniGameSelectionPixel = [[40, 126], [63, 107], [286, 120], [309, 116], [217, 122], [422, 764], [386, 689]]
StageMiniGameSelectionColor = [(82, 102, 198), (201, 68, 75), (83, 103, 199), (203, 66, 73), (240, 240, 142), (255, 255, 75), (238, 238, 228)]

StageMiniGameSelectedPixel = [[42, 127], [66, 122], [281, 121], [309, 131], [44, 305], [14, 438], [15, 467], [443, 438], [406, 369], [418, 477]]
StageMiniGameSelectedColor = [(32, 41, 80), (33, 41, 80), (33, 41, 80), (34, 41, 79), (104, 96, 87), (100, 88, 42), (138, 125, 75), (103, 90, 45), (175, 138, 95), (199, 181, 135)]

MiniGameRewardOKPos = [77, 390]
MiniGameEnterPos = [392, 478]

TokenNumberPos = [327, 774, 370, 793]

EventPixel = [[103, 198], [115, 287]]
EventColor = [(239, 156, 53), (159, 129, 80)]
EventOK = [235, 602]

StageBattlePixel = [[17, 718], [232, 36], [302, 6]]
StageBattleColor = [(59, 234, 255), (110, 85, 37), (212, 45, 18)]

StageBattleEndPixel = [[42, 274], [234, 444], [433, 305]]
StageBattleEndColor = [(231, 233, 89), (93, 61, 16), (238, 175, 65)]

StageBattleLostPixel = [[103, 456], [263, 396], [353, 481], [302, 254], [307, 229]]
StageBattleLostColor = [(111, 105, 84), (235, 223, 198), (151, 145, 127), (192,192, 192), (0, 0, 0)]

BattleReadyPixel = [[398, 397], [34, 394]]
BattleReadyColor = [(103, 90, 45), (102, 89, 44)]

ActionContinue = EventOK
ActionBattle = [[93, 429], [224, 339], [365, 428]]

StageLootPixel = [[4, 295], [233, 238]]
StageLootColor = [(191, 176, 107), (255, 236, 178)]

StageNoStaminaPixel = [[57, 371], [36, 275], [390, 343], [150, 294]]
StageNoStaminaColor = [(93, 76, 50), (255, 236, 176), (212, 199, 159), (255, 241, 216)]
ActionNoStaminaOK = [230, 504]

StageMinePixel = [[24, 102], [144, 108], [391, 788], [271, 770]]
StageMineColor = [(254, 235, 175), (254, 235, 175), (251, 232, 173), (255, 255, 248)]

StageLoadingPixel = [[16, 32], [67, 370], [257, 131], [184, 658], [420, 769], [277, 296]]
StageLoadingColor = [(52, 44, 34), (49, 40, 28), (62, 53, 45), (65, 61, 55), (54, 44, 32), (46, 36, 24)]

LevelLeavePos = [53, 775]
StageLevelupPixel = [[229, 345], [139, 404]]
StageLevelupColor = [(255, 226, 76), (243, 51, 64)]

InventoryPos = [428, 123]
InventoryBackPos = [388, 93]

AppClosePos = [74, -35]
AppIconPos = [[295, 131], [395, 131]]
AppIconPixel = [[316, 133], [279, 103]]
AppIconColor = [(255, 244, 228), (84, 132, 195)]
AppLoginPos = [232, 592]

StageFarmPixel = [[278, 17], [48, 139], [237, 768], [399, 678]]
StageFarmColor = [(103, 90, 44), (249, 86, 80), (176, 161, 115), (158, 204, 89)]

StageNoInternetPixel = [[210, 135], [248, 634], [181, 488], [328, 491], [36, 273], [149, 282]]
StageNoInternetColor = [(0, 0, 0), (0, 0, 0), (176, 161, 115), (179, 161, 115),(255, 236, 176), (255, 241, 216)]

NoInternetOKPOS = [165, 490]
ToTownPos = [408, 738]
SlimeScorePos = [330, 131, 417, 153]

LeaveGamePos = [49, 712]
LeaveGameConfirm = [157, 502]

StageLevelPixel = [[62, 392], [226, 275], [334, 364], [231, 713], [422, 719]]
StageLevelColor = [(100, 160, 106), (101, 182, 136), (73, 130, 138), (59, 40, 19), (255, 255, 255)]