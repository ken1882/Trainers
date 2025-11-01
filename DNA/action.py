import Input
import win32con
from time import sleep


def move_forward(duration=1.0):
    Input.key_down(ord('W'))
    sleep(duration)
    Input.key_up(ord('W'))

def move_backward(duration=1.0):
    Input.key_down(ord('S'))
    sleep(duration)
    Input.key_up(ord('S'))

def move_left(duration=1.0):
    Input.key_down(ord('A'))
    sleep(duration)
    Input.key_up(ord('A'))

def move_right(duration=1.0):
    Input.key_down(ord('D'))
    sleep(duration)
    Input.key_up(ord('D'))

def jump():
    Input.trigger_key(win32con.VK_SPACE)

def interact():
    Input.trigger_key(ord('F'))

def restart():
    Input.trigger_key(win32con.VK_ESCAPE)
    sleep(1)
    Input.click(1769, 987)