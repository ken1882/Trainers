import os
import configparser

ConfigFilePath = os.getenv("MTGDiscordRPCConfigPath")

def update_player_profile(name, level):
  if not ConfigFilePath:
    return
  config = configparser.ConfigParser()
  config.read(ConfigFilePath)
  config['SmallImageTooltip'] = f"{name} - Rank.{level}"
  with open(ConfigFilePath, 'w') as fp:
    config.write(fp)