RunningStyle = 0  # 0/1/2/3: 逃/先/差/追

# index = Speed/Stamina/Power/Willness/Wisdom(SPD/STA/POW/WIL/WIS)
# Attribute weight multiplier when under next objective min.attr.
MinAttributeWeightMultiplier = [
  1.2,
  1.2,
  1.2,
  1.0,
  1.1
]

# Attribute weight multiplier when over min.attr. but under fair.attr.
FairAttributeWeightMultiplier = [
  1.0,
  1.0,
  1.0,
  1.0,
  1.0,
]

# Attribute weight multiplier when fair.attr.
OverAttributeWeightMultiplier = [
  1.0,
  1.0,
  1.0,
  1.0,
  1.0,
]

ObjectiveAttributeMin = [
  #SPD,STA,POW,WIL,WIS
  [100,100,100, 90, 90],
  [200,200,200,100,100],  # 朝日杯
  [250,250,200,100,100],  # スプリングステークス
  [250,250,200,100,100],  # 皐月賞
  [250,250,200,100,100],  # 日本ダービー
  [300,350,200,150,200],  # 菊花賞
  [400,500,300,200,300],  # 天皇賞(春)
  [500,500,400,200,300],  # ジャパC
  [600,500,400,250,400],  # 有馬紀念
]

ObjectiveAttributeFair = [
  [200,200,200,100,100],
  [300,200,300,100,150],  # 朝日杯
  [350,300,350,200,200],  # スプリングステークス
  [350,300,400,200,250],  # 皐月賞
  [350,350,400,200,250],  # 日本ダービー
  [450,450,400,250,300],  # 菊花賞
  [450,600,400,300,350],  # 天皇賞(春)
  [600,600,500,300,400],  # ジャパC
  [600,600,600,300,400],  # 有馬紀念
]

OptionalRace = [
  
]

PreferredEventOption = {
  '追加の自主トレ': 0,
  '愉快ッ！密着取材！': 0,
}

# Skill to immediate get (by prior knowledge)
ImmediateSkills = [
  '先頭の景色は譲らない…！',
  '勝利の鼓動',
  '汝、皇帝の神威を見よ',
  '良バ場◎',
  '道悪◎',
  '晴れの日◎',
  '徹底マーク◎',
  '円弧のマエストロ',
  'コーナー回復○',
  '好転一息',
  '直線回復',
  '全身全霊',
  '末脚',
  '垂れウマ回避',
  '臨機応変',
  'レーンの魔術師',
]