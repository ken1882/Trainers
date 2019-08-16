Config = {
  'MaxRepair': 4,
  'WorstRepairTime': 3600, # 1 hour
  'FastRepairThreshold': 1200, # -frth X (40 mins)
  'StopFastRepairItemThreshold': 30,
  'RetireDollNumber': 24,

  'CheckRepairCount': {
    'default': 1,
    '0-2': 4,
    'SC2-1': 3,
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
    'SC1-3': [1022, 526],
    'SC2-1': [795, 456],
  },

  'TeamDeployPos': {
    '3-3E': [[986, 536], [466, 403]],
    '3-4E': [[216, 361], [1170, 261]],
    '4-3E': [[1193, 544], [255, 408]],
    '0-2': [[738, 411], [300, 394]],
    'SC1-3': [[815, 407], [659, 426]],
    'SC2-1': [[717, 402]],
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
      [ # turn 1
        ['supply', [815, 407]],
        ['supply', [659, 426]],
        ['move', [815, 404], [755, 338]],
        ['move', None, [816, 280]],
        ['move', [813, 403], [873, 341]],

        ['move', [659, 606], [713, 563]],
      ],
      [ # turn 2
        ['move', [878, 403], [795, 323]],
        ['unselect'],
        ['move', [796, 323], [724, 263]],

        ['move', [713, 561], [636, 509]],
        ['move', None, [570, 465]],
      ],
    ],

    'SC2-1':[
      [ # turn 1 
        ['supply', [693, 406]],
        ['move', None, [656, 339]],

        ['deploy', [693, 406]],
        ['supply', [693, 406]]
      ],
      [ # Plan phase
        ['plan',
          [655, 335], [553, 354], # select team 1 and move
          [690, 397], [784, 400], # select team 2 and confirm
          [928, 528], [627, 710], # team 2 move
          [655, 336], [751, 333], [636, 268] # select team 1 confirm and move
        ]
      ]
      # [ # turn 2
      #   ['move', [655, 339], [554, 354]],

      #   ['move', [686, 403], [796, 516]],
      #   ['move', None, [879, 435]],
      #   ['unselect'], # possible enemy in next move
      #   ['move', [879, 435], [926, 528]]
      # ],
      # [ # turn 3
      #   ['move', [551, 352], [494, 251]],
      #   ['unselect'], # possible enemy in next move
      #   ['move', [494, 251], [630, 270]],

      #   ['move', [924, 528], [731, 646]],
      #   ['unselect'], # possible enemy in next move
      #   ['move', [731, 646], [629, 713]],
      # ],
    ]
  }, # event combat movements
}