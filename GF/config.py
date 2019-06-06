Config = {
  'MaxRepair': 4,
  'WorstRepairTime': 7200, # 2 hours
  'FastRepairThreshold': 1200, # -frth X
  'StopFastRepairItemThreshold': 30,
  'RetireDollNumber': 24,

  'MainGunnerIndexA': "assets/FAL.png", # -mgia X
  'MainGunnerIndexB': "assets/M14.png", # -mgib X

  'LevelFastRepairThreshold': {
    '4-3E': 1200, # 20 mins
    '0-2': 2400,  # 40 mins
  },

  'LevelWorstRepairTime':{
    '4-3E': 1800, # 60 mins
    '0-2': 5400,  # 90 mins
  },

  'TeamEngagingMovement':{
    '4-3E': [
      [ # team 1
        [1, (6, 3)], # seconds to wait after battle start, pos 6 to 3
        [3, (2, 1)],
        [6, (3, 2)],
      ],
      [ # team 2 (needn't to move)

      ]
    ]
  },

  'TeamMovementPos': {
    '3-3E': [
      [ # turn 1
        [ # team 1
          ([986, 536], [884, 432]), 
          ([884, 432], [1157, 289]), 
          ([1152, 375], [995, 222])
        ], 
        
        [ # team 2
          ([463, 463], [288, 350])
        ] 
      ],
    ], # 3-3E

    '4-3E': [
      [
        [ # team 1
          ([1195, 543], [1181, 376]),
          ([1184, 401], [1244, 233]),
          ([1246, 402], [1142, 231]),
          ([1141, 405], [1160, 169])
        ],     
        [] # team 2 (idle)
      ],
    ], # 4-3E

  } # team movement
}
