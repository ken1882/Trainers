from datetime import date, datetime,timedelta
from random import random
from graphics import is_color_ok
import Input
import _G
from time import sleep, time

LastSkillUsedTime = 0
class Skill:
  def __init__(self, name, cd, keycode):
    '''
    A Skill Struct

    - Arguments:
      - name: Skill name
      - cd: Cool down time of skill, in seconds
      - keycode: Corresponding MapleStory keycode linked to skill
    '''
    self.name    = name
    self.cd      = timedelta(seconds=cd)
    self.keycode = keycode
    self.last_used_time = datetime(1990, 1, 1)
  
  def is_ready(self):
    return (datetime.now() - self.last_used_time) > self.cd

  def use(self):
    global LastSkillUsedTime
    if _G.FlagPaused or not _G.FlagRunning:
      return
    if not self.is_ready():
      return
    if self.name not in ['Teleport'] or self.name in ['BreathOfDivinity']:
      curt = time()
      if curt < LastSkillUsedTime+0.2:
        sleep(min(0.1, curt-LastSkillUsedTime))
    LastSkillUsedTime = time()
    for event in Input.get_keybd_pair(self.keycode):
      r = random()/5
      if r < 0.1:
        sleep(r)
      Input.SendInput(event)
  
  def apply_cd(self):
    self.last_used_time = datetime.now()

TrueArachnidReflection = Skill('TrueArachnidReflection', 250, _G.MAPLE_KEYCODE['6']) # 蜘蛛之鏡
WillOfAlliance    = Skill('WillOfAlliance', 7200, _G.MAPLE_KEYCODE['L'])    # 聯盟的意志
MapleWarrior      = Skill('Maple Warrior', 10, _G.MAPLE_KEYCODE['F7'])      # 楓葉祝福
HerosWill         = Skill('HerosWill', 300, _G.MAPLE_KEYCODE['8'])          # 楓葉淨化
BuffCombination1  = Skill('BuffCombination1', 180, _G.MAPLE_KEYCODE['F5'])  # 加持技能組合

MagicGuard        = Skill('MagicGuard', 1, _G.MAPLE_KEYCODE['F6'])         # 魔心防禦
ManaBrust         = Skill('ManaBrust', 0, _G.MAPLE_KEYCODE['A'])           # 魔力之環
Teleport          = Skill('Teleport', 0, _G.MAPLE_KEYCODE['SHIFT'])        # 瞬間移動
FireBreath        = Skill('FireBreath', 5, _G.MAPLE_KEYCODE['D'])          # 龍之氣息
DragonFlash       = Skill('DragonFlash', 5, _G.MAPLE_KEYCODE['Q'])         # 龍之捷
DragonDive        = Skill('DragonDive', 5, _G.MAPLE_KEYCODE['S'])          # 龍之躍
WindCircle        = Skill('WindCircle', 0, _G.MAPLE_KEYCODE['W'])          # 風之環
EarthCircle       = Skill('EarthCircle', 0, _G.MAPLE_KEYCODE['F'])         # 地之環
ThunderCircle     = Skill('ThunderCircle', 0, _G.MAPLE_KEYCODE['E'])       # 雷之環
Return            = Skill('Return', 0, _G.MAPLE_KEYCODE['V'])              # 回來吧
MagicDerbis       = Skill('MagicDerbis', 0, _G.MAPLE_KEYCODE['G'])         # 魔力殘骸
DarkFog           = Skill('DarkFog', 40, _G.MAPLE_KEYCODE['1'])            # 龍神之怒
DragonSlam        = Skill('DragonSlam', 20, _G.MAPLE_KEYCODE['X'])         # 聖龍突襲
ElementalBarrage  = Skill('ElementalBarrage', 60, _G.MAPLE_KEYCODE['R'])   # 元素滅殺破
ElementalRadiance = Skill('ElementalRadiance', 180, _G.MAPLE_KEYCODE['5']) # 星宮射線
DragonMaster      = Skill('DragonMaster', 240, _G.MAPLE_KEYCODE['2'])      # 龍之主
SummonOnyxDragon  = Skill('SummonOnyxDragon', 80, _G.MAPLE_KEYCODE['3'])   # 招喚聖歐尼斯龍
LucidsNightmare   = Skill('LucidsNightmare', 110, _G.MAPLE_KEYCODE['4'])   # 露希妲的惡夢
FreudsWisdom      = Skill('FreudsWisdom', 25, _G.MAPLE_KEYCODE['C'])       # 普利特的祝福
SpiderMirror      = Skill('SpiderMirror', 245, _G.MAPLE_KEYCODE['8'])      # 蜘蛛之鏡
SolarImprint      = Skill('SolarImprint', 245, _G.MAPLE_KEYCODE['9'])      # 烈陽印記
HeroicMemories    = Skill('HeroicMemories', 120, _G.MAPLE_KEYCODE['7'])    # 英雄歐尼斯
EldasFall         = Skill('EldasFall', 38, _G.MAPLE_KEYCODE['T'])          # 艾爾達斯降臨

TakenoKonoko      = Skill('TakenoKonoko', 1800, _G.MAPLE_KEYCODE['0'])    # 木野子的祝福
Kurama            = Skill('Kurama', 1800, _G.MAPLE_KEYCODE['K'])          # 闇的指甲
Yorozu            = Skill('Yorozu', 1800, None)                           # 萬事屋的拘束
Izuna             = Skill('Izuna', 1800, None)                            # 泉奈的祈禱
Ibaraki           = Skill('Ibaraki', 1800, None)                          # 棘鬼

BreathOfDivinity  = Skill('BreathOfDivinity', 60, _G.MAPLE_KEYCODE['C'])     # 天上的氣息
BreathOfDivinity2 = Skill('BreathOfDivinity2', 62, _G.MAPLE_KEYCODE['C'])     # 天上的氣息
MasterOfNightmare = Skill('MasterOfNightmare', 150, _G.MAPLE_KEYCODE['`'])   # 惡夢的支配者

DecentHolySymbol = Skill('DecentHolySymbol', 180, _G.MAPLE_KEYCODE['M'])    # 實用的祈禱
ManaOverload     = Skill('ManaOverload', 60, _G.MAPLE_KEYCODE['O'])         # 超載魔力
EtherealForm     = Skill('EtherealForm', 60, _G.MAPLE_KEYCODE['9'])         # 虛無型態
DecentAdvancedBlessing = Skill('DecentAdvancedBlessing', 180, _G.MAPLE_KEYCODE['K']) # 實用的進階祝福

Reincarnation = Skill('Reincarnation', 240, _G.MAPLE_KEYCODE['Y'])