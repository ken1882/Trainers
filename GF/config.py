Config = {
  'MaxRepair': 4,
  'WorstRepairTime': 3600, # 1 hour
  'FastRepairThreshold': 1200, # -frth X (40 mins)
  'StopFastRepairItemThreshold': 30,
  'RetireDollNumber': 24,

  'CheckRepairCount': {
    'default': 1,
    '0-2': 4,
  },

  'MainGunnerIndexA': {
    "default": ["assets/FAL.png"],
    "0-2": ["assets/FAL.png"]
  },

  'MainGunnerIndexB': {
    "default": ["assets/AR15.png"],
    "0-2": ["assets/M4A1.png", "assets/AR15.png"],
  },

  'MinCombatResources': [3000, 3000, 3000, 2500],

  'LevelFastRepairThreshold': {
    '3-3E': 1200, # 20 mins
    '3-4E': 1800, # 30 mins
    '4-3E': 1200, # 20 mins
    '0-2': 1800,  # 30 mins
    'VAHA-8': 300, # 5 mins
    'VAHA-6': 1200,
  },

  'LevelWorstRepairTime': {
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
          ([718, 398], [755, 181]), 
          ([717, 400], [857, 193]),
          ([-1, -1], [708, 96]),    # -1: needn't select again
        ],

        [] # team 2
      ],

      [ # turn 2
        [ # team 1
          ([716, 404], [1008, 402]), 
          ([720, 401], [907, 434])
        ],

        [], # team 1
      ]
    ],
  }, # team movement

  'EventLevelPos': {
    'SC1-3': [932, 439]
  },

  'TeamDeployPos': {
    '3-3E': [[986, 536], [466, 403]],
    '3-4E': [[216, 361], [1170, 261]],
    '4-3E': [[1193, 544], [255, 408]],
    '0-2': [[738, 411], [300, 394]],
    'SC1-3': [[718, 408], [389, 454]],
  },

  # arg0: command string, arg1~: args
  # move: click two given position (arg1=src, arg2=dest)
  # swap: swap two team (arg1=src, arg2=dest, arg3=swap comfirm pos)
  # deploy: deploy a team on given position (arg1=pos)
  # supply: supply team on given position (arg1=pos)
  # scoll: Scroll from posA to posB (arg1=[x1, y1, x2, y2])
  # retreat: Retreat team on given position (arg1=pos)
  # restart: Restart mission
  # abort: Abort mission
  'EventCombatMovement': {
    'SC1-3': [
      [ # turn1
        ['supply', [718, 408]],
        ['supply', [389, 454]],
        ['move', [717, 402], [584, 267]],
        ['move', None, [713, 146]],
        ['move', [713, 402], [849, 279]],
        ['move', [271, 785], [370, 731]],
      ],
      [ # turn 2
        ['move', [377, 737], [204, 629]],
        ['move', None, [70, 533]],
        ['move', [716, 401], [546, 236]],
        ['move', [547, 237], [406, 117]],
      ],
    ]
  }, # event combat movements
}