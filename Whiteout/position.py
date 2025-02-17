CommonBackPos = (10, 10)
MapSearchPos  = (26, 505)
MapSearchStart = (205, 700)
StartGatherPos = (205, 360)
DeployTroops = (317, 700)
SearchLevelDec = (40, 604)
SearchLevelInc = (280, 604)
CancelSearch = (201, 92)
CancelDeploy = (126, 457)
SwitchView = (379, 707)

HealAvailable   = ((315, 596), (238, 113, 147))
StartHealing    = (336, 693)
RequestHealHelp = (206, 329)
HelpAvailable   = ((306, 637), (21, 168, 50))
HelpAvailable2  = ((309, 636), (43, 168, 50))

MaxoutTroopPos = (
    (348, 375),(348, 456),(348, 537),(348, 617)
)

TrainInfantry = {
    'pos': (
        (108, 349),(192, 439),(308, 694),(23, 26),
        (187, 471),(265, 557),(308, 689),(25, 23),
        (296, 325),(363, 406),(309, 695),(27, 28),
    ),
    'wait': (
        1, 3, 1.2, 1.2,
        1, 3, 1.2, 1.2,
        1, 3, 1.2, 1.2,
        1, 3, 1.2, 1.2,
    )
}

MapSearchFound = (
    ((275, 184),(221, 314),(127, 377),(174, 362),(303, 368),),
    ((196, 119, 56),(207, 221, 242),(239, 249, 255),(79, 165, 252),(239, 249, 255),)
)

MapTroopDispatched = (
    (
        ((121, 158), (71, 181, 217)),
        ((121, 158), (76, 198, 244)),
        ((120, 156), (73, 190, 235)),
        ((126, 146), (76, 198, 244))
    ),
    (
        ((121, 194), (71, 181, 217)),
        ((121, 194), (76, 198, 244)),
        ((120, 192), (73, 190, 235)),
        ((124, 196), (76, 198, 244))
    ),
    (
        ((121, 229), (68, 172, 209)),
        ((127, 216), (76, 198, 244)),
        ((122, 230), (76, 198, 244)),
        ((127, 217), (76, 198, 244)),
        ((126, 233), (76, 198, 244)),
        ((119, 223), (76, 198, 244)),
        ((128, 218), (76, 198, 244)),
    )
)

TroopHeroAssigned = (
    ((135, 148),(244, 148),(353, 148)),
    ((255, 255, 255),(255, 255, 255),(255, 255, 255))
)

RemoveHeroPos = (
    (),
    (135, 148),
    (244, 148),
    (353, 148)
)

GatherFormation = (
    {
        'level': 6,
        'remove_hero': [2, 3]
    },
    {
        'level': 6,
        'remove_hero': [3]
    },
    {
        'level': 6,
        'remove_hero': [3]
    },
)