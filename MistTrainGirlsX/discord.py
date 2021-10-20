import os
import configparser
from stage import StageData

ConfigFilePath = os.getenv("MTGDiscordRPCConfigPath")
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
  if not ConfigFilePath or stage_id not in StageData:
    return
  detail,stat = StageData[stage_id]
  config = configparser.ConfigParser()
  config.optionxform = str
  config.read(ConfigFilePath)
  config['State']['State'] = stat
  config['State']['Details'] = detail
  with open(ConfigFilePath, 'w') as fp:
    config.write(fp, space_around_delimiters=False)