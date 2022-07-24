import _G,utils
import skill, Input
from time import sleep
import win32con


Keystate = {
  ' ': 0,
}

def process_autokey():
  global Keystate
  if Keystate[' ']:
    Input.trigger_key(_G.MAPLE_KEYCODE['SPACE'])

def main_loop():
  global Keystate
  Input.update()
  if Input.is_trigger(win32con.VK_NUMPAD4):
    _G.log_info("Assist: Elemental Radiance")
    seq = [
      skill.MagicDerbis,
      skill.FireBreath, skill.WindCircle, skill.MagicDerbis, skill.Return,
      skill.DragonFlash, skill.WindCircle, skill.MagicDerbis, skill.Return,
      skill.DragonDive, skill.EarthCircle, skill.MagicDerbis, skill.Return
    ]
    for sk in seq:
      sk.use()
      if sk in [skill.WindCircle, skill.EarthCircle]:
        sleep(0.05)
      else:
        sleep(0.01)
  elif Input.is_pressed(win32con.VK_NUMPAD5):
    _G.log_info('Assist: Interact/Harvest ' + ('end' if Keystate[' '] else 'start'))
    Keystate[' '] ^= 1
    sleep(0.1)
  # elif Input.is_pressed(win32con.VK_NUMPAD0):
  #   _G.FlagRunning = False
  process_autokey()

if __name__ == '__main__':
  try:
    while _G.FlagRunning:
      main_loop()
  except (SystemExit, KeyboardInterrupt):
    pass