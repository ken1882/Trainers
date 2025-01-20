import _G
import Input
import win32con
from _G import sleep, wait, uwait
import position

VK_W = ord('W')
VK_A = ord('A')
VK_S = ord('S')
VK_D = ord('D')
VK_E = ord('E')
VK_T = ord('T')
VK_TILDE = 0xC0

def target_object():
  Input.key_down(win32con.VK_CONTROL)
  Input.key_down(win32con.VK_TAB)
  sleep(0.03)
  Input.key_up(win32con.VK_TAB)
  Input.key_up(win32con.VK_CONTROL)

def target_enemy():
  Input.key_down(win32con.VK_TAB)
  sleep(0.03)
  Input.key_up(win32con.VK_TAB)

def target_player():
  Input.key_down(win32con.VK_CONTROL)
  Input.key_down(win32con.VK_SHIFT)
  Input.key_down(win32con.VK_TAB)
  sleep(0.03)
  Input.key_up(win32con.VK_TAB)
  Input.key_up(win32con.VK_SHIFT)
  Input.key_up(win32con.VK_CONTROL)

def face_target():
  Input.key_down(win32con.VK_CONTROL)
  Input.key_down(VK_W)
  sleep(0.03)
  Input.key_up(VK_W)
  Input.key_up(win32con.VK_CONTROL)

def lockon_target():
  Input.trigger_key(win32con.VK_NUMPAD5)

def interact():
  # return interact2()
  Input.key_down(win32con.VK_SHIFT)
  Input.key_down(VK_E)
  sleep(0.03)
  Input.key_up(VK_E)
  Input.key_up(win32con.VK_SHIFT)

def auto_walk():
  Input.trigger_key(VK_TILDE)

# 5s =~ 0.6 grid
def move_forward(dur=0.3):
  Input.key_down(VK_W)
  sleep(dur)
  Input.key_up(VK_W)

def move_backward(dur=0.3):
  Input.key_down(VK_S)
  sleep(dur)
  Input.key_up(VK_S)

def move_right(dur=0.3):
  Input.key_down(win32con.VK_MENU)
  Input.key_down(VK_D)
  sleep(dur)
  Input.key_up(VK_D)
  Input.key_up(win32con.VK_MENU)

def move_left(dur=0.3):
  Input.key_down(win32con.VK_MENU)
  Input.key_down(VK_A)
  sleep(dur)
  Input.key_up(VK_A)
  Input.key_up(win32con.VK_MENU)

# 2.62s =~ 360 degree
def rotate_left(dur):
  Input.key_down(VK_A)
  sleep(dur)
  Input.key_up(VK_A)

def rotate_right(dur):
  Input.key_down(VK_D)
  sleep(dur)
  Input.key_up(VK_D)

def camera_left(dur):
  Input.key_down(win32con.VK_LEFT)
  sleep(dur)
  Input.key_up(win32con.VK_LEFT)

def camera_right(dur):
  Input.key_down(win32con.VK_RIGHT)
  sleep(dur)
  Input.key_up(win32con.VK_RIGHT)

def mount():
  Input.key_down(win32con.VK_CONTROL)
  Input.key_down(VK_T)
  sleep(0.03)
  Input.key_up(VK_T)
  Input.key_up(win32con.VK_CONTROL)

def quit_fishing():
  Input.key_down(win32con.VK_MENU)
  Input.key_down(ord('2'))
  sleep(0.2)
  Input.key_up(ord('2'))
  Input.key_up(win32con.VK_MENU)

def logout():
  Input.rmoveto(*position.SystemMenu, rrange=1)
  uwait(0.1)
  Input.click(use_msg=False)
  uwait(0.1)
  Input.rmoveto(*position.Logout)
  uwait(0.1)
  Input.click(use_msg=False)
  uwait(0.1)
  # Input.trigger_key(win32con.VK_ESCAPE)
  # uwait(0.1)
  Input.rmoveto(*position.LogoutOK)
  uwait(0.1)
  Input.click(use_msg=False)

def interact2():
  Input.key_down(win32con.VK_SHIFT)
  Input.key_down(win32con.VK_SPACE)
  sleep(0.03)
  Input.key_up(win32con.VK_SPACE)
  Input.key_up(win32con.VK_SHIFT)

def interact_press(ms):
  Input.key_down(win32con.VK_SHIFT)
  Input.key_down(win32con.VK_SPACE)
  sleep(ms/1000.0)
  Input.key_up(win32con.VK_SPACE)
  Input.key_up(win32con.VK_SHIFT)

def menu_up():
  Input.key_down(win32con.VK_SHIFT)
  Input.key_down(win32con.VK_MENU)
  Input.key_down(VK_W)
  sleep(0.03)
  Input.key_up(VK_W)
  Input.key_up(win32con.VK_MENU)
  Input.key_up(win32con.VK_SHIFT)

def menu_right():
  Input.key_down(win32con.VK_SHIFT)
  Input.key_down(win32con.VK_MENU)
  Input.key_down(VK_D)
  sleep(0.03)
  Input.key_up(VK_D)
  Input.key_up(win32con.VK_MENU)
  Input.key_up(win32con.VK_SHIFT)