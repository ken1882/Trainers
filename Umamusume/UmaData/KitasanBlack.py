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

  'クラシック級3月後半',   # Fans x5000
  'クラシック級9月後半',   # セントライト記念
  'クラシック級10月後半',  # 菊花賞
  'クラシック級12月後半',  # 有馬記念
  'シニア級3月後半',      # 大阪杯
  'シニア級4月後半',      # 天皇賞（春）
  'シニア級6月後半',      # 宝塚記念
  'シニア級10月後半',     # 天皇賞（秋）
  'シニア級11月後半',     # ジャパンカップ
  'シニア級12月後半',     # 有馬記念

  'ファイナルズ 開催中', 'ファイナルズ 開催中', 'ファイナルズ 開催中'
]

ObjectiveName = [
  'メイクデビュー',
  
  '', # Fans x3000
  'セントライト記念',
  '菊花賞',
  '有馬記念',
  '大阪杯',
  '天皇賞（春）',
  '宝塚記念',
  '天皇賞（秋）',
  'ジャパンカップ',
  '有馬記念',

  'ファイナルズ予選',
  'ファイナルズ準決勝',
  'ファイナルズ決勝'
]


ObjectiveAttributeMin = [
  #SPD,STA,POW,WIL,WIS
  [100,100,100, 90, 90],  # メイクデビュー
  [200,200,200,100,100],  #
  [250,250,200,100,100],  #
  [250,250,200,100,100],  #
  [300,350,200,150,200],  #
  [400,350,400,250,200],  #
  [400,450,300,200,200],  #
  [400,350,400,250,200],  #
  [500,450,400,200,200],  #
  [500,450,400,200,200],  #
  [600,500,400,250,200],  #
  [600,500,400,250,200],
  [600,500,400,250,200],
  [600,500,400,250,200],
]

ObjectiveAttributeFair = [
  [200,200,200,100,100],  # メイクデビュー
  [250,200,200,150,100],  #
  [300,300,250,200,150],  #
  [300,350,250,200,150],  #
  [400,450,300,250,200],  #
  [500,500,400,250,250],  #
  [500,600,450,300,300],  #
  [550,600,450,300,350],  #
  [550,600,500,300,350],  #
  [550,600,500,300,350],  #
  [600,600,600,350,350],  #
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
  # '朝日杯フューチュリティステークス',
  'ホープフルステークス',
  '皐月賞',
  '日本ダービー',
  '宝塚記念',
  # '大阪杯',
  # 'ヴィクトリアマイル',
  '天皇賞（秋）',
  'エリザベス女王杯',
  'ジャパンカップ',
  '金鯱賞',
  # '毎日王冠'
]

# Optional race specified by date
DateOptionalRace = {
  # 'シニア級6月前半': '安田記念',
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
