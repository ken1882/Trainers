Config = {
  'MaxRepair': 4,
  'WorstRepairTime': 3600, # 1 hour
  'FastRepairThreshold': 1200, # -frth X (40 mins)
  'StopFastRepairItemThreshold': 30,
  'RetireDollNumber': 24,

  'MainGunnerIndexA': {
    "default": ["assets/FAL.png"],
    "0-2": ["assets/FAL.png"]
  },

  'MainGunnerIndexB': {
    "default": ["assets/AR15.png"],
    "0-2": ["assets/AR15.png"],
  },

  'MinCombatResources': [3000, 3000, 3000, 2500],

  'LevelFastRepairThreshold': {
    '3-3E': 1200, # 20 mins
    '3-4E': 1800, # 30 mins
    '4-3E': 1200, # 20 mins
    '0-2': 2400,  # 40 mins
    'VAHA-8': 300, # 5 mins
  },

  'LevelWorstRepairTime':{
    '3-3E': 1800, # 30 mins
    '3-4E': 1800, # 30 mins
    '4-3E': 1800, # 30 mins
    '0-2': 3600,  # 60 mins
    'VAHA-8': 7200, # 2 hours
  },

  'TeamEngagingMovement':{
    '3-3E':[[], []],

    '3-4E': [
      [
        [7, (6, 3)],
        [9, (9, 0)],
      ],

      []
    ],

    '4-3E': [
      [ # team 1
        [1, (6, 3)], # seconds to wait after battle start, pos 6 to 3
      ],
      []# team 2 (needn't to move)
    ],

    '0-2':[[], []],
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

    '3-4E': [
      [ # turn 1
        [ # team 1
          ([214, 362], [387, 434]),
          ([393, 405], [462, 556]),
          ([465, 405], [434, 605]),
          ([430, 403], [584, 503]),
        ],

        [], # team 2
      ]
    ],

    '4-3E': [
      [ # turn 1
        [ # team 1
          ([1195, 543], [1181, 376]),
          ([1184, 401], [1244, 233]),
          ([1246, 402], [1142, 231]),
          ([1141, 405], [1160, 169])
        ],     
        [] # team 2 (idle)
      ],
    ], # 4-3E

    '0-2': [
      [ # turn 1
        [ # team 1
          ([739, 404], [553, 297]), 
          ([564, 403], [604, 184]), 
          ([604, 404], [747, 180]),
          ([-1, -1], [592, 90]),    # -1: needn't select again
        ],

        [] # team 2
      ],

      [ # turn 2
        [ # team 1
          ([593, 294], [906, 293]), 
          ([900, 293], [1102, 333])
        ],

        [], # team 1
      ]
    ],
  }, # team movement

  'EventCombatMovement': {
    'VAHA-3': [
      [ # turn 1
        ('supply', [601, 407]),
        ('move', [-1, -1], [708, 527]),
        ('move', [-1, -1], [928, 656])
      ],

      [ # turn 2
        ('deploy', [595, 478]),
        ('supply', [595, 478]),
        ('move', [-1, -1], [486, 226])
      ]
    ],

    'VAHA-8': [
      [
        ('supply', [933, 111]),
        ('move', [-1, -1], [870, 212]),
        ('move', [-1, -1], [803, 314]),
        ('move', [-1, -1], [670, 312]),
        ('move', [672, 383], [800, 384]),
        ('move', [-1, -1], [865, 283]),
        ('move', [-1, -1], [932, 183], [831, 185]),
        ('retreat', [932, 183]),
        ('abort',)
      ]
    ],
  }, # event combat movements
}