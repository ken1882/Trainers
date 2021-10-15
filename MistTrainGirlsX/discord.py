import os
import configparser

ConfigFilePath = os.getenv("MTGDiscordRPCConfigPath")

StageStatus = {
          0: ('Waiting for maintenance', 'メンテナンス中...'),
  304013106: ('Playing events', '入隊訓練：カラマチ/クインズウェイ (Inferno)'),
  101002505: ('Playing main story', 'クエスト 2-5 (Very Hard)'),
}

ProfileCache = ''

def update_player_profile(name, level):
  global ProfileCache
  if not ConfigFilePath:
    return
  if ProfileCache == f"{name}{level}":
    return
  ProfileCache = f"{name}{level}"
  config = configparser.ConfigParser()
  config.optionxform = str
  config.read(ConfigFilePath)
  config['Images']['SmallImageTooltip'] = f"{name} - Rank.{level}"
  with open(ConfigFilePath, 'w') as fp:
    config.write(fp, space_around_delimiters=False)

def update_status(stage_id):
  if stage_id not in StageStatus:
    return
  detail,stat = StageStatus[stage_id]
  config = configparser.ConfigParser()
  config.optionxform = str
  config.read(ConfigFilePath)
  config['State']['State'] = stat
  config['State']['Details'] = detail
  with open(ConfigFilePath, 'w') as fp:
    config.write(fp, space_around_delimiters=False)