from time import sleep
import _G, utils
import requests
import json
from glob import glob

ASSET_HOST = 'https://assets.mist-train-girls.com/production-client-web-assets'
STATIC_HOST = 'https://assets.mist-train-girls.com/production-client-web-static'

CharacterData = {}

MAX_RETRY = 100
RETRY_DELAY = 1

def get_voice_files(id, bid):
    return {
        'BattleStart':    f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_battle_{id}.mp3",
        'Attack_1':       f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_attack1_{bid}.mp3",
        'Attack_2':       f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_attack2_{bid}.mp3",
        'Skill_1':        f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_skill1_{id}.mp3",
        'Skill_2':        f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_skill2_{id}.mp3",
        'SkillLink':      f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_cutin_{id}.mp3",
        'Damage':         f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_damage_{bid}.mp3",
        'Death':          f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_death_{id}.mp3",
        'Victory':        f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_victory_{id}.mp3",
        'SpecialSkill':   f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_special_{id}.mp3",
        'NewJoin':        f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_new_{id}.mp3",
        'Home_1':         f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_home1_{id}.mp3",
        'Home_2':         f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_home2_{id}.mp3",
        'Home_3':         f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_home3_{id}.mp3",
        'Kizuna_1':       f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_favorite1_{id}.mp3",
        'Kizuna_2':       f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_favorite2_{id}.mp3",
        'Kizuna_3':       f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_favorite3_{id}.mp3",
        'Kizuna_4':       f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_favorite4_{id}.mp3",
        'Kizuna_5':       f"{ASSET_HOST}/Sounds/Voices/Characters/Layers/{id}/voice_favorite5_{id}.mp3",
        'NewYear':        f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_jan_{bid}.mp3",
        'Valentine':      f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_feb_{bid}.mp3",
        'WhiteValentine': f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_mar1_{bid}.mp3",
        'DollsDay':       f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_mar2_{bid}.mp3",
        'GoldenWeek':     f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_apr_{bid}.mp3",
        'MomsDay':        f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_may_{bid}.mp3",
        'Tsuyu':          f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_jun_{bid}.mp3",
        'Tanabata':       f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_jul_{bid}.mp3",
        'SummerFesti':    f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_aug_{bid}.mp3",
        'Moonfesti':      f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_sep_{bid}.mp3",
        'Halloween':      f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_oct_{bid}.mp3",
        'Autumn':         f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_nov_{bid}.mp3",
        'Christmas':      f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_dec1_{bid}.mp3",
        'NewYearEve':     f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_dec2_{bid}.mp3",
        'Oneyear':        f"{ASSET_HOST}/Sounds/Voices/Characters/Bases/{bid}/voice_oneyear_{bid}.mp3",
    } 


def get_character_spine(id):
    return {
        'battler_png': f"{ASSET_HOST}/Small/Spines/SDs/{id}/{id}.png",
        'battler_atlas': f"{ASSET_HOST}/Small/Spines/SDs/{id}/{id}.atlas",
        'battler_skel': f"{ASSET_HOST}/Small/Spines/SDs/{id}/{id}.skel",
        'full_png': f"{ASSET_HOST}/Spines/Events/{id}/{id}.png",
        'full_atlas': f"{ASSET_HOST}/Spines/Events/{id}/{id}.atlas",
        'full_skel': f"{ASSET_HOST}/Spines/Events/{id}/{id}.skel",
    }

def get_character_avatars():
    return {
        'image': [
            f"{ASSET_HOST}/Textures/Icons/Atlas/Layers/character-1.png",
            f"{ASSET_HOST}/Textures/Icons/Atlas/Layers/character-2.png"
        ],
        'clip': [
            f"{ASSET_HOST}/Textures/Icons/Atlas/Layers/character-1.plist",
            f"{ASSET_HOST}/Textures/Icons/Atlas/Layers/character-2.plist",
        ]
    }

def get_character_info():
    return {
        "/MasterData/MCharacterViewModel.json": parseCharacterData,
        "/MasterData/GearLevelsViewModel.json": parseGearData,
        "/MasterData/MSkillViewModel.json": parseSkillData,
        "/MasterData/MLinkSkillViewModel.json": parseLinkSkillData,
        "/MasterData/MChangeSkillViewModel.json": parseChangeSkillData,
    }

def parseCharacterData(res):
    global CharacterData
    path = "assets/MasterData/MCharacterViewModel.json"
    utils.ensure_dir_exist(path)
    with open(path, 'wb') as fp:
        fp.write(res.content)
    for obj in res.json():
        CharacterData[obj['Id']] = obj

def parseGearData(res):
    path = "assets/MasterData/GearLevelsViewModel.json"
    utils.ensure_dir_exist(path)
    with open(path, 'wb') as fp:
        fp.write(res.content)

def parseSkillData(res):
    path = "assets/MasterData/MSkillViewModel.json"
    utils.ensure_dir_exist(path)
    with open(path, 'wb') as fp:
        fp.write(res.content)

def parseLinkSkillData(res):
    path = "assets/MasterData/MLinkSkillViewModel.json"
    utils.ensure_dir_exist(path)
    with open(path, 'wb') as fp:
        fp.write(res.content)

def parseChangeSkillData(res):
    path = "assets/MasterData/MChangeSkillViewModel.json"
    utils.ensure_dir_exist(path)
    with open(path, 'wb') as fp:
        fp.write(res.content)

def get_all_scenes():
    ret = {}
    files = glob(f"{_G.DCTmpFolder}/scenes/*.json")
    for file in files:
        with open(file, 'r') as fp:
            dat = json.load(fp)
        ret[dat['MSceneId']] = dat
    return ret

def dump_asset(url):
    print("Downloading", url)
    err_cnt = 0
    while err_cnt < MAX_RETRY:
        try:
            res = requests.get(url)
            break
        except Exception as err:
            err_cnt += 1
            print(f"Connection error ({err}), retrying #{err_cnt}")
            sleep(RETRY_DELAY)
    path = _G.DCTmpFolder+'assets'+url.split(ASSET_HOST)[-1]
    utils.ensure_dir_exist(path)
    with open(path, 'wb') as fp:
        fp.write(res.content)

def dump_scene_assets():
    scenes = get_all_scenes()
    bgm_set = set()
    scene_voices = {}
    for scene_id, data in scenes.items():
        scene_voices[scene_id] = []
        for dia in data['MSceneDetailViewModel']:
            if dia['BGM']:
                bgm_set.add(dia['BGM'])
            if dia['VoiceFileName']:
                scene_voices[scene_id].append(dia['VoiceFileName'])
    for bgm in bgm_set:
        url = f"{ASSET_HOST}/Sounds/Bgms/Adv/{bgm}.mp3"
        dump_asset(url)
    
    for scid, voices in scene_voices.items():
        for voice in voices:
            url = f"{ASSET_HOST}/Sounds/Voices/Scenarios/Mains/m_{scid}/{voice}.mp3"
            dump_asset(url)

if __name__ == '__main__':
    
    # ava_info = get_character_avatars()
    # utils.ensure_dir_exist(f"assets/Textures/Icons/Atlas/Layers/")
    # for key, cat in ava_info.items():
    #     for url in cat:
    #         print("Downloading", url)
    #         res = requests.get(url)
    #         path = _G.DCTmpFolder+'assets'+url.split(ASSET_HOST)[-1]
    #         with open(path, 'wb') as fp:
    #             fp.write(res.content)
    #         print(f"File {path} dumped")

    for uri,handler in get_character_info().items():
        print(f"Fetching {STATIC_HOST}{uri}")
        err_cnt = 0
        while err_cnt < MAX_RETRY:
            try:
                res = requests.get(f"{STATIC_HOST}{uri}")
                break
            except Exception as err:
                err_cnt += 1
                print(f"Connection error, retrying #{err_cnt}")
                sleep(RETRY_DELAY)
        handler(res)

    for chid,character in CharacterData.items():
        bid  = character['MCharacterBaseId']
        
        print("Processing", chid, character['Name']+character['MCharacterBase']['Name'])
        sdat = get_character_spine(chid)
        for _,url in sdat.items():
            dump_asset(url)
        
        vdat = get_voice_files(chid, bid)
        for _,url in vdat.items():
            dump_asset(url)