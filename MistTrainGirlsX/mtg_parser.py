import msgpack

OBJKEYS_ITEMDROP = ('ItemType', 'ItemQuantity', 'ItemId', 'UserItemId', 'Sold', 'HasLimited')
OBJKEYS_USERMETA = (
    'UUserId',
    'Name', '_',
    'Rank',
    'TotalStatus',
    'MFieldSkillId',
    'FieldSkillLevel',
    'LastLoginedAt',
    'MCharacterId',
    'FriendState',
    'RankingTitleId',
    'MCharacterSkinId',
    'IsAutoApprovalFriendRequest',
)
OBJKEYS_FRIENDMETA = (
    'UUserId',
    'Name', '_',
    'Rank',
    'TotalStatus',
    'MFieldSkillId',
    'FieldSkillLevel',
    'LastLoginedAt',
    'MCharacterId',
    'FriendState',
    'RankingTitleId',
    'MCharacterSkinId',
    'IsAutoApprovalFriendRequest',
    'FriendMeterPoint',
    'LastRentalAt',
    'IsNewFriend'
)
OBJKEYS_USERDATA = (
    'Id',
    'CurrentActionPoints',
    'ActionPointsRestoredAt',
    'IsAdult',
    'Money',
    'Gem',
    'FreeGem',
    'Level',
    'TotalExperience',
    'MaxActionPoints',
    'TotalFieldSkillCost',
    'DisplayUserId',
)
OBJKEYS_USERPREF = (
    'Name',
    'DateOfBirth',
    'LocateType',
    'WeaponLimit',
    'ArmorLimit',
    'AccessoryLimit',
    'AbilityStoneLimit',
    'SoundMute',
    'BgmVolume',
    'SeVolume',
    'VoiceVolume',
    'MyPageBgmJukeBoxActivated',
    'AutoRoundBgmJukeBoxActivated',
    'CharacterAutoLockRarity',
    'IsHomeCharacterRandom',
    'CurrentHomeViewTypeIsCharacter',
    'MFieldSkillId1',
    'MFieldSkillId2',
    'MFieldSkillId3',
    'IsHomeFieldSkillRandom',
    'KnuckleWeaponLevel',
    'KnuckleWeaponTotalPoint',
    'SwordWeaponLevel',
    'SwordWeaponTotalPoint',
    'AxWeaponLevel',
    'AxWeaponTotalPoint',
    'SpearWeaponLevel',
    'SpearWeaponTotalPoint',
    'WhipWeaponLevel',
    'WhipWeaponTotalPoint',
    'MagicWeaponLevel',
    'MagicWeaponTotalPoint',
    'BowWeaponLevel',
    'BowWeaponTotalPoint',
    'RodWeaponLevel',
    'RodWeaponTotalPoint',
    'GunWeaponLevel',
    'GunWeaponTotalPoint',
    'UPartyId',
    'MQuestId',
    'BattleAutoSetting',
    'BattleSpeed',
    'AutoSellEquipRarity',
    'AutoSellEquipEvolution',
    'AutoSellEquipLevel',
    'AutoSellAbility',
    'AutoSellSlot',
    'AdventureTextFeed',
    'SpecialSkillAnimation',
    'CurrentClearChapter',
    'UnlockFeatureFlag',
    'UnlockEffectFlag',
    'FunctionHelpFlag',
    'FunctionHelpFlag2',
    'FunctionHelpFlag3',
    'TutorialStatus',
    'BattleAutoSellEquipType',
    'BattleRaritySellTypeB',
    'BattleRaritySellTypeA',
    'BattleRaritySellTypeS',
    'AbilityStoneBattleRaritySellTypeA',
    'AbilityStoneBattleRaritySellTypeS',
    'InCombat',
    'WorkOutEndTime',
    'DoubleWorkOutEndTime',
    'HasRecommendNotice',
    'IsAutoSpecialSkill',
    'IsAutoOverDrive',
    'EnableConnect',
    'EnableIndividualAutoSell',
    'ImageQualitySetting',
    'RankingTitleId',
    'IsAutoApprovalFriendRequest',
    'EnableEnemyShieldEffect',
    'BattleAutoSpecialSkillType',
    'BattleSkipBuffEffectFlag',
    'UserPreferenceActiveFlag',
    'CurrentClearSideStoryChapter'
)
OBJKEYS_BATTLE_SKILL = (
    'Id',
    'SkillRefId',
    'SkillType',
    ('CriticalEffects', list, ('Race', 'Size', 'EnemyId')),
    'SP',
    'IsCommandSkill',
    'IsCounterSkill',
    'IsExtraAttackSkill',
    'IsChangeSkill',
    'IsHiddenSkill',
    'IsSubstituteSkill',
)
OBJKEYS_BATTLESETTING = (
    'BattleAutoSetting', 'BattleSpeed', 'BattleSpecialSkillAnimation',
    'IsAutoSpecialSkill', 'IsAutoOverDrive', 'EnableConnect',
    'EnableEnemyShieldEffect', 'BattleAutoSpecialSkillType',
    'BattleSkipBuffEffectFlag', 'UserPreferenceActiveFlag'
)
OBJKEYS_DAMAGE_ATTRIBUTE = (
    'Blade',
    'Impact',
    'Pierce',
    'Fire',
    'Water',
    'Wind',
    'Light',
    'Dark',
)
OBJKEYS_STATUS_AILMENTS = (
   'Confusion',
    'Paralysis',
    'Poison',
    'Sleep',
    'Silent',
    'Stun',
    'Blind',
    'Charm',
)
OBJKEYS_AURA = ('SerialAuraId', 'SkillEffectType', 'SkillEffectModifier', 'TurnLeft', 'Count')
OBJKEYS_STATUS = (
    'HP',
    'Strength',
    'Defence',
    'Dexterity',
    'Speed',
    'Intelligence',
    'MindDefence',
    'Mind',
    'Luck'
)
OBJKEYS_USKILL = (
    'Id',
    'MSkillId',
    'Stage',
    'Rank',
    'Learned',
)
OBJKEYS_ABSTONE = (
    'Id',
    'SlotNo',
    'MAbilityStoneId',
    'Level',
    'MLevelUpSkillGroupId'
)
OBJDICT_ITEMDROP = (
    ('Items', list, OBJKEYS_ITEMDROP),
    ('GiftItems', list, OBJKEYS_ITEMDROP),
    'DeletedItemIds',
)
OBJDICT_UWEAPON = (
    'Id',
    'UUserId',
    'MWeaponId',
    'EvolutionCount',
    'Level',
    'TotalExperience',
    'MSkillId',
    ('Status', dict, OBJKEYS_STATUS),
    'ReferenceCounting',
    'PresetReferenceCounting',
    'Locked',
    'CanLevelup',
    'CanEvolve',
    'SlotCount',
    ('AbilityStoneSlots', list, OBJKEYS_ABSTONE),
    'AcquiredAt'
)
OBJDICT_UARMOR = (
    'Id',
    'UUserId',
    'MArmorId',
    'EvolutionCount',
    'Level',
    'TotalExperience',
    'MSkillId',
    'Status',
    'AttributeResistGroup',
    'ReferenceCounting',
    'PresetReferenceCounting',
    'Locked',
    'CanLevelup',
    'CanEvolve',
    'SlotCount',
    ('AbilityStoneSlots', list, OBJKEYS_ABSTONE),
    'AcquiredAt',
)
OBJDICT_UACCESSORY = (
    'Id',
    'UUserId',
    'MAccessoryId',
    'ReferenceCounting',
    'PresetReferenceCounting',
    'MSkillId',
    'Locked',
    'Status',
    'SlotCount',
    ('AbilityStoneSlots', list, OBJKEYS_ABSTONE),
    'AcquiredAt'
)
OBJDICT_UABSTONE = (
    'Id',
    'UUserId',
    'MAbilityStoneId',
    'Level',
    'TotalExperience',
    'MLevelUpSkillGroupId',
    'CanLevelUp',
    'Locked',
    'IsEquipped',
    'AcquiredAt',
)
OBJDICT_UCHARACTERBASE = (
    'Id',
    'UUserId',
    'MCharacterBaseId',
    'Experience',
    ('Status', dict, OBJKEYS_STATUS),
    ('ExStatus', dict, OBJKEYS_STATUS),
)
OBJDICT_UCHARACTER = (
    'Id',
    'UUserId',
    'MCharacterId',
    'UCharacterBaseId',
    ('UCharacterBaseViewModel', dict, OBJDICT_UCHARACTERBASE),
    'Level',
    'TotalExperience',
    'MaxLevel',
    ('USkill1', dict, OBJKEYS_USKILL),
    ('USkill2', dict, OBJKEYS_USKILL),
    ('USkill3', dict, OBJKEYS_USKILL),
    ('SpecialSkill', dict, OBJKEYS_USKILL),
    ('BaseStatus', dict, OBJKEYS_STATUS),
    'TotalStatus',
    'KizunaRank',
    'ReferenceCounting',
    'GearLevel',
    'TotalGearExperience',
    'CanLevelup',
    'IllustMCharacterId',
    'IllustMCharacterSkinId',
    'SdMCharacterId',
    'SdMCharacterSkinId',
    'UTrainBoard',
)
OBJDICT_CHARACTER_BATTLER = (
    'ID', 'HP', 'RP', 'SP', 'OP', 'CP',
    'SMP', 'CID',
    'SpecialSkillUsed',
    'MaxRP',
    ('ConditionResistGroup', dict, OBJKEYS_STATUS_AILMENTS),
    ('AttributeResistGroup', dict, OBJKEYS_DAMAGE_ATTRIBUTE),
    ('Auras', list, OBJKEYS_AURA),
    ('Skills', list, OBJKEYS_BATTLE_SKILL),
    'IsGiantUnit',
)
OBJDICT_ENEMY_BATTLER = (
    'ID', 'EID',
    'CurrentHPPercent', 'CurrentDamage',
    'DebugHP',
    'IsBoss',
    'IsGiantUnit',
    'X', 'Y', 'Z',
    ('ConditionResistGroup', dict, OBJKEYS_STATUS_AILMENTS),
    ('AttributeResistGroup', dict, OBJKEYS_DAMAGE_ATTRIBUTE),
    ('Auras', list, OBJKEYS_AURA),
    ('Skills', list, OBJKEYS_BATTLE_SKILL),
    ('Attributes', list, ('Attribute', 'Count')),
    ('Shields', list, ('Id', 'IsActive', 'RemainCount', 'RestoreTurnCount')),
)
OBJDICT_VICTORY_RESULT = (
    ('CharacterExperienceRewards', list, (
        'UCharacterId', 'ExperienceReward'
    )),
    'CharacterExperienceReward',
    'MoneyBonus',
    ('PlayerLevel', dict, (
        'BeforeLevel', 'BeforeTotalExperience', 'Level', 'PlayerExperienceReword'
    )),
    ('QuestRewords', dict, OBJDICT_ITEMDROP),
    ('QuestLoots', dict, OBJDICT_ITEMDROP),
    ('QuestLootApplyCampaigns', list, (
        'ItemType', 'ItemId', 'ApplyItemCampaignFlag'
    )),
    ('SpecialDropItem', dict, OBJDICT_ITEMDROP),
    ('CharacterGrowthStatus', list, (
        'UCharacterId',
        'TotalStatus',
        ('StatusGrowths', list, ('StatusType', 'Reward')),
    )),
    ('CharacterGrowthSkills', list, (
        'UCharacterId',
        ('SkillGrowths', list, ('USkillId', 'GrowthCount')),
    )),
    ('LearnedSkills', list, ('UCharacterId', 'USkillId', 'MSkillId',)),
    'BeforeFriendMeterPoint',
    'AfterFriendMeterPoint',
    'IsRentFriendUser',
    ('FriendCandidateUserInfo', dict, OBJKEYS_USERMETA),
    'CampaignBonus'
    'NextMQuestId',
    'RaidResult',
    'ClearSec',
    'BattalionQuestVictoryInfo',
    'SelectableDeckDrops',
    'SelectableFirstRewards',
    'SelectableWeeklyRewards',
    'BattleFesFirstClearRewards',
    'CharacterActionCountExpBonus',
    'ScoreAttackResult',
    'SportsFesResult',
    'TowerQuestResult',
    'TreasureExQuestResult',
    ('UUser', dict, OBJKEYS_USERDATA),
    ('UUserPreferences', dict, OBJKEYS_USERPREF),
)
OBJDICT_DEFEAT_RESULT = ((
    ('QuestLoots', dict, OBJDICT_ITEMDROP),
    ('QuestRewords', dict, OBJDICT_ITEMDROP),
    'MDefeatTipsId',
    'FriendMeterPoint',
    'IsRentFriendUser',
    'FriendCandidateUserInfo',
    ('UUser', dict, OBJKEYS_USERDATA),
    ('UUserPreferences', dict, OBJKEYS_USERPREF),
    'BattleFesFirstClearRewards',
    'CharacterGrowthExStatusesList',
    'SportsFesResult',
))
OBJDICT_BATTLE_STATE = (
    'WaveNumber',
    'TurnNumber',
    'ActionCount',
    ('Characters', list, OBJDICT_CHARACTER_BATTLER),
    ('Enemies', list, OBJDICT_ENEMY_BATTLER),
    ('BattleAreaUnits', list, OBJDICT_ENEMY_BATTLER),
    'BattleStatus',
    'ChangeSkills',
    'PreemptiveAction',
    'WarnBattleAreaSkill'
)
OBJDICT_ACTION_RESULT = (
    ('BattleActions', list, (
        'BattleActionType',
        'DebugStr',
        'ActorType',
        'ActorId',
        'SkillId',
        'TargetUnitId',
        'TargetCurrentHPPercent',
        'Value',
        'IsMiss',
        'ActionId',
        'AttackId',
        'ActionSkillNo',
        'MainTargetId',
        'DamageFlags',
        'BattleActionEffects',
        'EndedAuraIds',
        'ApplyElements',
        'ActivatedElementalBursts',
        'IsCountUpAction',
        'IsSubstituteAction',
    )),
    ('VictoryResult', dict, OBJDICT_VICTORY_RESULT),
    ('DefeatResult', dict, OBJDICT_DEFEAT_RESULT),
    ('BattleState', dict, OBJDICT_BATTLE_STATE),
    'Sequence',
    'AlreadyBattleResult',
    'TraceLog',
    'Version',
)
OBJDICT_UCHARACTERSLOT = (
    'Id',
    'SlotNo',
    'TotalStatus',
    'UCharacterId',
    ('UCharacter', dict, OBJDICT_UCHARACTER),
    'UWeaponId',
    ('UWeapon', dict, OBJDICT_UWEAPON),
    'MWeaponId',
    'UArmorId',
    ('UArmor', dict, OBJDICT_UARMOR),
    'MArmorId',
    'UAccessoryId',
    ('UAccessory', dict, OBJDICT_UACCESSORY),
    'MAccessoryId',
    'USkill1SPFiexdValue',
    'USkill2SPFiexdValue',
    'USkill3SPFiexdValue',
    'USkill4SPFiexdValue',
    ('AdditionalSeriesSetStatus', dict, OBJKEYS_STATUS),
    ('AdditionalFormationStatus', dict, OBJKEYS_STATUS),
    ('AdditionalPartySkillStatus', dict, OBJKEYS_STATUS),
    ('AdditionalAbilityStoneSkillStatus', dict, OBJKEYS_STATUS),
    ('AdditionalUltimateWeaponSkillStatus', dict, OBJKEYS_STATUS),
    ('USkill', dict, OBJKEYS_USKILL),
)
OBJDICT_UPARTY = (
    'Id',
    'PartyNo',
    'Name',
    'MFormationId',
    ('UCharacterSlots', list, OBJDICT_UCHARACTERSLOT),
    'UFieldSkill1Id',
    'MFieldSkill1Id',
    'UFieldSkill2Id',
    'MFieldSkill2Id',
    'UFieldSkill3Id',
    'MFieldSkill3Id',
    'GetUPartyFailedReason',
)
OBJDICT_TRADE_GOODS = (
    'Id', 'UserItemId',
    'StartDate', 'EndDate',
    'Limit', 'WeeklyLimit', 'MonthlyLimit', 'TradedCount', 'Order', 
    'ItemId', 'ItemType', 'ItemQuantity', 'RequiredMItemId', 
    'RequiredMItemNum', 'Sold', 'HasSelectableAbility'
)

def interpret_data(keys, data):
  ret = {}
  for k,dat in zip(keys, data):
    if type(k) == str:
      ret[k] = dat
    else:
      if dat == None:
        ret[k[0]] = None
        continue
      otype = k[1]
      if otype == list:
        ret[k[0]] = []
        try:
           for d in dat:
              ret[k[0]].append(interpret_data(k[2], d))
        except Exception as err:
           print(f"Error while parsing {k}")
           raise err
      elif otype == dict:
        ret[k[0]] = interpret_data(k[2], dat)
  return ret


def get_keys(keys, obj):
    ret = []
    for k in keys:
        ret.append(obj[k])
    return ret

def parse_attack_payload(data):
    ret = []
    ret.append(data['Type'])
    ret.append([])
    for cmd in data['Commands']:
        ret[1].append(get_keys(
            ['UnitSerialId', 'CommandId', 'TargetId', 'IsOverDrive'],
            cmd
        ))
    ret.append(get_keys(OBJKEYS_BATTLESETTING, data['BattleSettings']))
    ret.append(data['IsSimulation'])
    ret.append(data['Version'])
    return msgpack.packb(ret)

def parse_battle_start(data):
    return interpret_data((
        'BattleId',
        'RaidId',
        'BattleMode',
        ('BattleState', dict, OBJDICT_BATTLE_STATE),
        'BattleCharacterStatuses',
        'Participants',
        'FaildReason',
        'UPartyId',
        'Version',
        'UUserPreferences',
        ('UPartyViewModel', dict, OBJDICT_UPARTY),
    ), data)

def parse_victory_result(data):
   return interpret_data(OBJDICT_VICTORY_RESULT, data)

def parse_defeat_result(data):
   return interpret_data(OBJDICT_VICTORY_RESULT, data)

def parse_attack_result(data):
    return interpret_data(OBJDICT_ACTION_RESULT, data)

def parse_lblevelup_payload(data):
    ret = get_keys(
        ['Experience', 'CharacterExperienceItemQuantity', 'GeneralExperienceItemQuantity',],
        data
    )
    return msgpack.packb(ret)

def parse_battlesetting_payload(data):
    return msgpack.packb(get_keys(OBJKEYS_BATTLESETTING, data))

def parse_user_data(data):
    return interpret_data(OBJKEYS_USERDATA, data)

def parse_user_perference(data):
    return interpret_data(OBJKEYS_USERPREF, data)

def parse_friend_retals(data):
    return interpret_data((
        ('FriendUsers', list, OBJKEYS_FRIENDMETA),
        ('OtherUsers', list, OBJKEYS_USERMETA),
    ), data)

def parse_consumable_items(data):
    ret = []
    for item in data:
        ret.append(
        interpret_data(
            ('UItemId', 'MItemId', 'Stock'),
            item
        )
        )
    return ret

def parse_aprecovery_result(data):
    return interpret_data(('CurrentStamina', 'IsLimit'), data)

def parse_limiteditem_result(data):
    return interpret_data(('MItemId', 'ExpireStock', 'ExpireDate', 'MGachaId'), data)

def parse_ucharacter_result(data):
    return interpret_data(OBJDICT_UCHARACTER, data)

def parse_uweapon_result(data):
    return interpret_data(OBJDICT_UWEAPON, data)

def parse_uarmor_result(data):
    return interpret_data(OBJDICT_UARMOR, data)

def parse_uaccessory_result(data):
    return interpret_data(OBJDICT_UACCESSORY, data)

def parse_uabstone_result(data):
    return interpret_data(OBJDICT_UABSTONE, data)

def parse_characterpiece_result(data):
    return interpret_data(('UCharacterPieceId', 'MCharacterPieceId', 'Stock'), data)

def parse_basestatus_result(data):
    return interpret_data((
        'MaxHp',
        ('MaxStatuses', list, OBJKEYS_STATUS),
    ), data)

def parse_quest_prepare_result(data):
   return interpret_data((
        'QuestPreparationDropProbabilityUpViewModels',
        ('QuestPreparationCharacterViewModels', list, (
            'UCharacterId',
            ('GrowStatus', dict, OBJKEYS_STATUS),
            'CampaignTypes',
        )),
        ('UPartyViewModel', dict, OBJDICT_UPARTY),
        'RentalMFieldSkillId',
        ('QuestPreparationPullUpStatusViewModel', dict, (
           'MaxHp',
           'MaxStatus',
           ('PullUpStatuses', list, (
                'UCharacterId',
                'TotalStatus',
                ('StatusGrowthViewModels', list, ('StatusType', 'Reward')),
            )),
        )),
        ('QuestPreparationCharacterExStatusViewModels', list, (
            'UCharacterId',
            ('GrowStatus', dict, OBJKEYS_STATUS),
        )),
    ), data)

def parse_partygroup_result(data):
    return interpret_data((
        'GroupNo',
        ('UParties', list, OBJDICT_UPARTY)
    ), data)

def parse_uparty(data):
   return interpret_data(OBJDICT_UPARTY, data)

def parse_trade_shop(data):
    return interpret_data((
        'Id', 'TradeShopType', 'StartDate', 'EndDate',
        'Order', 'JumpScene', 'TargetValue', 'BannerResourceUri',
        'IconMItemId', 'IconName'
    ), data)

def parse_trade_shop_goods(data):
    return interpret_data((
        'JumpTargetEndDate',
        ('Rewards', list, OBJDICT_TRADE_GOODS),
    ), data)

def parse_vote_result(data):
   return interpret_data((
        'TargetId', 'VoteCount', 'AfterVoteMItemCount', 'VoteFailedReason'
    ), data)