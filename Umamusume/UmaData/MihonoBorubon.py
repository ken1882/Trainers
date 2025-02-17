RunningStyle = 0  # 0/1/2/3: 逃/先/差/追

# index = Speed/Stamina/Power/Willness/Wisdom(SPD/STA/POW/WIL/WIS)
# Attribute weight multiplier when under next objective min.attr.
MinAttributeWeightMultiplier = [
  1.15,
  1.15,
  1.15,
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

# Attribute weight multiplier when over fair.attr.
OverAttributeWeightMultiplier = [
  1.0,
  1.0,
  1.0,
  1.0,
  1.0,
]

# Delta weigt multiplier differnce of targegt attribute per day
MinAttributeDateWeightDecay = [
  0.98, 0.98, 0.98, 0.98, 0.98
]
FairAttributeDateWeightDecay = [
  0.95, 0.95, 0.95, 0.95, 0.95
]
OverAttributeDateWeightDecay = [
  0.92, 0.92, 0.92, 0.92, 0.92
]

# How many weight added to objective per difference
AttrDistanceWeightPlus = [
  0.01,
  0.01,
  0.01,
  0.01,
  0.01,
]

# Weight for each suppor card present
SupporterWeightMultiplier = 1.0

# Objective prehead calculating when determine attribute weight
ObjectiveDepth = 2

# When prehead calc, attribute weight decay per depth
ObjectiveWeightDecay = 0.8

# Post-calc of y = λx + σ
ObjectiveWeightLambda = 1.0
ObjectiveWeightSigma  = 0

ObjectiveDate = [
  'ジュニア級デビュー前', # メイクデビュー
  'ジュニア級12月前半',   # 朝日杯
  'クラシック級3月後半',  # スプリングステークス
  'クラシック級4月前半',  # 皐月賞
  'クラシック級5月後半',  # 日本ダービー
  'クラシック級10月後半', # 菊花賞
  'シニア級4月後半',      # 天皇賞（春）
  'シニア級11月後半',     # ジャパC
  'シニア級12月後半',     # 有馬記念
  'ファイナルズ 開催中', 'ファイナルズ 開催中', 'ファイナルズ 開催中'
]

ObjectiveName = [
  'メイクデビュー',
  '朝日杯フューチュリティステークス',
  'スプリングステークス',
  '皐月賞',
  '日本ダービー',
  '菊花賞',
  '天皇賞（春）',
  'ジャパンカップ',
  '有馬記念',
  'ファイナルズ予選',
  'ファイナルズ準決勝',
  'ファイナルズ決勝'
]

ObjectiveAttributeMin = [
  #SPD,STA,POW,WIL,WIS
  [100,100,100, 90, 90],  # メイクデビュー
  [200,200,200,100,100],  # 朝日杯
  [250,250,200,100,100],  # スプリングステークス
  [250,250,200,100,100],  # 皐月賞
  [250,250,200,100,100],  # 日本ダービー
  [300,350,200,150,200],  # 菊花賞
  [400,450,300,200,300],  # 天皇賞（春）
  [500,450,400,200,300],  # ジャパC
  [600,500,400,250,400],  # 有馬記念
  [600,500,400,250,400],
  [600,500,400,250,400],
  [600,500,400,250,400],
]

ObjectiveAttributeFair = [
  [200,200,200,100,100],
  [300,200,300,100,150],  # 朝日杯
  [350,300,350,200,200],  # スプリングステークス
  [350,300,400,200,250],  # 皐月賞
  [350,350,400,200,250],  # 日本ダービー
  [450,450,400,250,300],  # 菊花賞
  [450,600,400,300,350],  # 天皇賞（春）
  [600,600,500,300,400],  # ジャパC
  [600,600,600,300,400],  # 有馬記念
  [600,600,600,300,400],
  [600,600,600,300,400],
  [600,600,600,300,400],
]

OptionalRace = [
  'ホープフルステークス',
  '安田記念',
  '宝塚記念',
  '大阪杯',
  '天皇賞（秋）',
  'エリザベス女王杯',
  'ジャパンカップ',
  '有馬記念',
]

# Optional race specified by date
DateOptionalRace = {
  
}

PreferredEventOption = {
  '追加の自主トレ': 0,
  '愉快ッ！密着取材！': 0,
  'オペレーション：外出時トラブル': 1,
  '素敵な♪練習日和': 2,
  'あぁ、故郷': 1,
  '完全無欠のスイーツ': 0,
  'ダシが重要！！': 0,
  'あんし〜ん笹針師、参☆上': 1,
  '初詣': 1,
  'シークレット・ノート！': 1,
}

# Skill to get immediately as soon as it's available
# regardless any situation (by prior knowledge)
ImmediateSkills = [
  '先頭の景色は譲らない…！',
  '勝利の鼓動',
  '汝、皇帝の神威を見よ',
  '良バ場◎',
  '道悪◎',
  '晴れの日◎',
  '徹底マーク◎',
  '円弧のマエストロ',
  '地固め',
  'コーナー回復○',
  '好転一息',
  '直線回復',
  '全身全霊',
  '末脚',
  '臨機応変',
  'レーンの魔術師',
]
