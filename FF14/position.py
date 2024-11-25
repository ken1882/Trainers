CoordRect = (1733, 246, 1890, 263)
DistanceRect = (607, 75, 662, 91)
MiniMapRect = (1700, 35, 1880, 230)
PlayerMiniMapPos = (1795, 145)
FishRect = (842, 1, 982, 81)
FishAvailable = (777, 925)

CraftProgress = (625, 339, 685, 360)
CraftDurability = (245, 342, 355, 362)

TeleportPos = (
  (1897, 703),(798, 287),(864, 363)
)

UnawareEnemyPosCol = (
  ((783, 113),(783, 115),(781, 116),),
  ((255, 248, 176),(255, 248, 176),(235, 215, 136),)
)

ActiveEnemyPosCols = (
  (
    ((783, 113),(781, 113),(782, 117),(784, 116),),
    ((255, 189, 191),(255, 189, 191),(146, 31, 31),(255, 136, 136),)
  ),
  (
    ((783, 113),(783, 115),(782, 115),),
    ((255, 189, 191),(255, 189, 191),(255, 189, 191),)
  )
)

GatherSkillUsable = {
  '1': ((715, 918), (205, 172, 172)),
  '2': ((759, 917), (164, 156, 148)),
  '3': ((804, 916), (98, 90, 90)),
  '4': ((852, 916), (255, 255, 255)),
  '5': ((899, 916), (57, 57, 41)),
  'Q': ((949, 922), (98, 65, 65)),
  'E': ((985, 915), (255, 255, 255)),
  'R': ((1032, 923), (131, 98, 90)),
  'V': ((1119, 925), (164, 131, 82)),
  'T': ((1161, 923), (172, 139, 82)),
}

OtherPlayerPosCol = (
  ((677, 88),(684, 88),(694, 88),(705, 87),),
  ((157, 194, 213),(157, 194, 213),(157, 194, 213),(156, 208, 244),)
)

FishFullGPPosCol = (
  (1107, 1001),
  (46, 30, 20)    
)

FishHalfGPPosCol = (
  (1041, 1001),
  (51, 35, 23)    
)

MoochPosCol = (
  (1126, 907),
  (255, 255, 156)
)

ThaliakPosCol = (
  (1035, 919),
  (131, 180, 213)
)

TottPosCol = (
  (984, 922),
  (255, 238, 197)
)

CRMMPosCol = (
  (808, 917),
  (197, 197, 197)
)

CRHQPosCol = (
  (597, 391),
  (134, 184, 169)
)

SystemMenu = (1855, 972)#(1853, 984)
Logout     = (1724, 914)
LogoutOK   = (906, 574)
GameStart  = (957, 822)
GeneralOK  = (904, 554)
LoginOK    = (902, 608)
ReturnPos  = (1898, 748)

FirstCharacter = (1556, 143)

LGT_DICT = {
  'Alumen': {
    'mpos': (250, 317),
    'skill': 'Q',
    'nodes': [
      [
        [17.0, 20.1],
        ('rotate', 0.7)
      ],
      [
        [17.3, 19.7],
        ('rotate', -0.8)
      ],
      [
        [17.0, 19.9],
        ('rotate', 0)
      ],
    ]
  },
  'Silver': {
    'mpos': (224, 494),
    'skill': 'T',
    'mtime': 140,
    'nodes': [
      [
        [16.9, 19.5],
        ('rotate', 0)
      ],
      [
        [16.8, 19.4],
        ('rotate', -0.5)
      ],
      [
        [16.7, 19.3],
        ('rotate', 0.5)
      ]
    ]
  },
  'Electrum': {
    'mpos': (246, 497),
    'skill': 'R',
    'nodes': [
      [
        [30.7, 25.0],
        ('rotate', -0.5)
      ],
      [
        [30.7, 25.1],
        ('rotate', 0.8)
      ],
      [
        [30.9, 25.0],
        ('rotate', 0.5)
      ],
      [
        [30.8, 25.1],
        ('rotate', -0.3)
      ],
    ]
  },
  # 'WindShard': {
  #   'mpos': (254, 447),
  #   'skill': 'E',
  #   'disableLock': True,
  #   'jump': True,
  #   'nodes': [
  #     [
  #       [19.5, 26.0],
  #       ('rotate', 0)
  #     ],
  #   ]
  # },
  'Cobalt': {
    'mpos': (244, 368),
    'skill': 'T',
    'disableAutoFind': True,
    'nodes': [
      [
        [23.8, 24.2],
        ('rotate', 0.5)
      ],
      [
        [24.0, 24.0],
        ('rotate', 0.7)
      ],
      [
        [23.9, 24.2],
        ('rotate', -0.3),
      ],
      [
        [23.5, 24.3],
        ('rotate', -0.85),
        ('jump', 5),
      ],
    ]
  },
  'Mythril': {
    'mpos': (213, 542),
    'skill': 'T',
    'disableAutoFind': True,
    'nodes': [
      [
        [24.4, 40.4],
      ],
      [
        [24.4, 40.5],
      ],
      [
        [24.4, 40.6],
      ],
    ]
  },
  'HardSilver': {
    'mpos': (248, 274),
    'alts': [(229, 450)],
    'hidden': ((453, 267), (14,14,14)),
    'skill': 'T',
    'mtime': 140,
    'nodes': [
      [
        [24.9, 23.1],
        ('rotate', 0)
      ],
    ]
  },
}

GT_ZincOre = [
  [
    (23.0, 29.1), 
    ('rotate', 1),
    ('forward', 7),
    ('rotate', -0.7)
  ],
  [
    (22.0, 29.1),
    ('rotate', 1),
    ('forward', 7),
    ('rotate', -0.5)
  ],
  [
    (21.5, 28.3),
    ('rotate', 1.3),
    ('forward', 9),
  ],
  [
    (22.8, 28.0),
    ('rotate', 1),
    ('forward', 5),
    ('rotate', -0.5)
  ]
]

GT_LightningShard = [
  [
    (20.5, 23.0),
    ('mount', None),
    ('rotate', 1.2),
    ('forward', 2),
  ],
  [
    (19.5, 23.2),
    ('mount', None),
    ('rotate', 1.2),
    ('forward', 5.5),
    ('rotate', 0.2),
  ],
  [
    (20.9, 22.2),
    ('mount', None),
    ('rotate', 1.15),
    ('forward', 5.5),
    ('rotate', -1),
  ],
]

GT_Danburite = [
  [
    [28.4, 23.4],
    ('mount', None),
    ('rotate', -1),
    ('forward', 7),
    ('rotate', 0.5),
  ],
  [
    [29.3, 22.5],
    ('mount', None),

  ],
  [
    [29.2, 21.7],
    ('mount', None),
    ('rotate', -0.9),
    ('forward', 7),
    ('rotate', 0.3),
    ('forward', 5),
    ('rotate', -0.6),
  ],
]

GT_BombAsh = [
  [
    [22.1, 29.1],
    ('mount', None),
    ('rotate', 1.2),
    ('forward', 3),
  ],
  [
    [23.0, 29.5],
    ('mount', None),
    ('rotate', 0.2),
  ],
  [
    [23.7, 29.7],
    ('mount', None),
    ('rotate', 1.2),
    ('forward', 5),
    ('rotate', 0.2),
    ('forward', 4),
  ],
  [
    [21.7, 28.8],
    ('mount', None),
    ('rotate', 1.2),
    ('forward', 5),
    ('rotate', -0.2),
    ('forward', 1),
  ],
  [
    [23.0, 30.0],
    ('mount', None),
    ('rotate', 1),
    ('forward', 7),
  ],
  [
    [22.4, 29.7],
    ('mount', None),
    ('rotate', 0.6),
    ('forward', 3),
  ],
  [
    [21.8, 29.8],
    ('mount', None),
    ('rotate', -1),
    ('forward', 3),
  ],
  [
    [22.5, 29.9],
    ('mount', None),
    ('rotate', -0.4),
    ('forward', 2),
  ]

]

GT_SilverOre = [
    [
      [15.9, 20.2],
      ('mount', None),
      ('rotate', 1.5),
      ('forward', 3),
    ],
    [
      [15.3, 19.2],
      ('mount', None),
      ('rotate', 1.1),
      ('forward', 2),
    ],
    [
      [15.9, 18.7],
      ('mount', None),
      ('rotate', 1.1),
      ('forward', 3),
    ],
    [
      [16.8, 19.5],
      ('mount', None),
      ('rotate', 1.2),
      ('forward', 3),
    ],
]