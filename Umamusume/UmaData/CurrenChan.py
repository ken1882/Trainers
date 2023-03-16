RunningStyle = 1  # 0/1/2/3: 逃/先/差/追

# index = Speed/Stamina/Power/Willness/Wisdom(SPD/STA/POW/WIL/WIS)
# Attribute weight multiplier when under next objective min.attr.
MinAttributeWeightMultiplier = [
  1.2,
  1.0,
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
  0.98, 0.95, 0.98, 0.98, 0.98
]
FairAttributeDateWeightDecay = [
  0.95, 0.93, 0.95, 0.95, 0.95
]
OverAttributeDateWeightDecay = [
  0.92, 0.90, 0.92, 0.92, 0.92
]

ObjectiveDate = [
  'ジュニア級デビュー前', # メイクデビュー

  'ジュニア級12月前半',   # Fans x3000
  'クラシック級3月前半',  # フィリーズレビュー
  'クラシック級5月後半',  # 葵ステークス
  'クラシック級6月後半',  # 函館スプリントステークス
  'クラシック級9月後半',  # スプリンターズS
  'シニア級3月前半',      # オーシャンS
  'シニア級3月後半',      # 高松宮記念
  'シニア級9月後半',      # スプリンターズS

  'ファイナルズ 開催中', 'ファイナルズ 開催中', 'ファイナルズ 開催中'
]

ObjectiveName = [
  'メイクデビュー',
  
  '', # Fans x3000
  'フィリーズレビュー',
  '葵ステークス',
  '函館スプリントステークス',
  'スプリンターズS',

  'オーシャンS',
  '高松宮記念',
  'スプリンターズS',

  'ファイナルズ予選',
  'ファイナルズ準決勝',
  'ファイナルズ決勝'
]

ObjectiveAttributeMin = [
  #SPD,STA,POW,WIL,WIS
  [100,100,100, 90, 90],  # メイクデビュー
  [200,200,200,100,120],  # Fans x3000
  [250,250,250,120,150],  # NHKマイルカップ
  [350,300,300,150,200],  # マイルCS
  [350,300,300,150,200],  # 有馬記念
  [400,300,400,200,250],  # G1 x2
  [400,300,400,200,250],  # 天皇賞（秋）
  [500,500,400,250,300],  # 有馬記念
  [500,500,400,250,300],
  [500,500,400,250,300],
  [500,500,400,250,300],
]

ObjectiveAttributeFair = [
  [200,200,200,150,150],  # メイクデビュー
  [200,200,200,150,150],  # Fans x3000
  [300,250,350,150,200],  # NHKマイルカップ
  [350,300,350,200,200],  # マイルCS
  [400,350,400,250,200],  # 有馬記念
  [400,350,400,250,250],  # G1 x2
  [500,400,450,250,350],  # 天皇賞（秋）
  [600,600,600,300,400],  # 有馬記念
  [600,600,600,300,400],
  [600,600,600,300,400],
  [600,600,600,300,400],
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
  '小倉ジュニアS',
  '京王杯ジュニアS',
  # '朝日杯フューチュリティステークス',
  '阪神ジュベナイルフィリーズ',
  'フィリーズレビュー',
  '桜花賞',
  'NHKマイルカップ',
  '安田記念',
  'セントウルステークス',
  'マイルチャンピオンシップ',
  '阪神C',
  'スワンS',
]

# Optional race specified by date
DateOptionalRace = {
  'シニア級6月前半': '安田記念',
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
]
