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
  'クラシック級2月前半',  # Fans x5000
  'クラシック級3月前半',  # 弥生賞
  'クラシック級9月後半',  # 神戸新聞杯
  'シニア級3月前半',      # 金鯱賞
  'シニア級6月後半',      # 宝塚記念
  'シニア級10月前半',     # 毎日王冠
  'シニア級10月後半',     # 天皇賞(秋)
  'ファイナルズ 開催中', 'ファイナルズ 開催中', 'ファイナルズ 開催中'
]

ObjectiveName = [
  'メイクデビュー',
  '',
  '弥生賞',
  '神戸新聞杯',
  '金鯱賞',
  '宝塚記念',
  '毎日王冠',
  '天皇賞（秋）',
  'ファイナルズ予選',
  'ファイナルズ準決勝',
  'ファイナルズ決勝'
]

ObjectiveAttributeMin = [
  #SPD,STA,POW,WIL,WIS
  [100,100,100, 90, 90],  # メイクデビュー
  [200,200,200,100,100],  # Fansx5000
  [250,250,200,100,100],  # 弥生賞
  [250,250,200,100,100],  # 神戸新聞杯
  [300,350,200,150,200],  # 金鯱賞
  [400,450,300,200,300],  # 宝塚記念
  [500,450,400,200,300],  # 毎日王冠
  [600,500,400,250,400],  # 天皇賞(秋)
  [600,500,400,250,400],
  [600,500,400,250,400],
  [600,500,400,250,400],
]

ObjectiveAttributeFair = [
  [200,200,200,100,100],
  [300,200,300,100,150],  # Fansx5000
  [350,300,350,200,200],  # 弥生賞
  [350,350,400,200,250],  # 神戸新聞杯
  [450,450,400,250,300],  # 金鯱賞
  [450,600,400,300,350],  # 宝塚記念
  [600,600,500,300,400],  # 毎日王冠
  [600,600,600,300,400],  # 天皇賞(秋)
  [600,600,600,300,400],
  [600,600,600,300,400],
  [600,600,600,300,400],
]

OptionalRace = [
  'ホープフルステークス',
  '皐月賞',
  'NHKマイルカップ',
  '安田記念',
  '宝塚記念',
  '大阪杯',
  '毎日王冠',
  '天皇賞（秋）',
  'エリザベス女王杯',
  'ジャパンカップ',
  '中山記念',
  'ヴィクトリアマイル',
  # '有馬記念',
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
