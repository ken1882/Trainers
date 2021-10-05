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

ObjectiveDate = [
  'ジュニア級デビュー前', # メイクデビュー

  'クラシック級1月前半',   # Fans x3000
  'クラシック級4月前半',   # 皐月賞
  'クラシック級5月後半',   # 日本ダービー
  'クラシック級10月後半',  # 菊花賞
  'クラシック級12月後半',  # 有馬記念
  'シニア級4月後半',      # 天皇賞（春）
  'シニア級6月後半',      # 宝塚記念
  'シニア級10月後半',     # 天皇賞（秋）
  'シニア級12月後半',     # 有馬記念

  'ファイナルズ 開催中', 'ファイナルズ 開催中', 'ファイナルズ 開催中'
]

ObjectiveName = [
  'メイクデビュー',
  
  '', # Fans x3000
  '皐月賞',
  '日本ダービー',
  '菊花賞',
  '有馬記念',
  '天皇賞（春）',
  '宝塚記念',
  '天皇賞（秋）',
  '有馬記念',

  'ファイナルズ予選',
  'ファイナルズ準決勝',
  'ファイナルズ決勝'
]


ObjectiveAttributeMin = [
  #SPD,STA,POW,WIL,WIS
  [100,100,100, 90, 90],  # メイクデビュー
  [200,200,200,100,100],  # Fans x3000
  [250,250,200,100,100],  # 皐月賞
  [250,250,200,100,100],  # 日本ダービー
  [300,350,200,150,200],  # 菊花賞
  [400,350,400,250,200],  # 有馬記念
  [400,450,300,200,200],  # 天皇賞（春）
  [400,350,400,250,200],  # 宝塚記念
  [500,450,400,200,200],  # 天皇賞（秋）
  [600,500,400,250,200],  # 有馬記念
  [600,500,400,250,200],
  [600,500,400,250,200],
  [600,500,400,250,200],
]

ObjectiveAttributeFair = [
  [200,200,200,100,100],  # メイクデビュー
  [250,200,200,150,100],  # Fans x3000
  [300,300,250,200,150],  # 皐月賞
  [300,350,250,200,150],  # 日本ダービー
  [400,450,300,250,200],  # 菊花賞
  [500,500,400,250,250],  # 有馬記念
  [500,600,450,300,300],  # 天皇賞（春）
  [550,600,450,300,350],  # 宝塚記念
  [550,600,500,300,350],  # 天皇賞（秋）
  [600,600,600,350,350],  # 有馬記念
  [600,600,600,350,400],
  [600,600,600,350,400],
  [600,600,600,350,400],
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
ObjectiveDepth = 0

# When prehead calc, attribute weight decay per depth
ObjectiveWeightDecay = 0.8

# Post-calc of y = λx + σ
ObjectiveWeightLambda = 1.0
ObjectiveWeightSigma  = 0

OptionalRace = [
  '朝日杯フューチュリティステークス',
  'ホープフルステークス',
  '宝塚記念',
  '大阪杯',
  'ヴィクトリアマイル',
  '天皇賞（秋）',
  'エリザベス女王杯',
  'ジャパンカップ',
  '金鯱賞',
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
  '汝、皇帝の神威を見よ',
  '先頭の景色は譲らない…！',
  '勝利の鼓動',
  '良バ場◎',
  '道悪◎',
  '晴れの日◎',
  '徹底マーク◎',
  '地固め',
  '円弧のマエストロ',
  'コーナー回復○',
  '好転一息',
  '直線回復',
  '全身全霊',
  '末脚',
  '臨機応変',
  'レーンの魔術師',
]
