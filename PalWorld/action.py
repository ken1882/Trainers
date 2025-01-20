import win32api,win32con,ctypes
import Input
import _G
import time
import multiprocessing
from multiprocessing import Process,Pipe

BASE_INTERVAL_TIME = 0.1
DIR_LEFT  = 1
DIR_RIGHT = 2

def walk_left(duration):
    Input.key_down(win32con.VK_LSHIFT)
    Input.key_down(ord('A'))
    _G.wait(duration)
    Input.key_up(ord('A'))
    Input.key_up(win32con.VK_LSHIFT)

def walk_right(duration):
    Input.key_down(win32con.VK_LSHIFT)
    Input.key_down(ord('D'))
    _G.wait(duration)
    Input.key_up(ord('D'))
    Input.key_up(win32con.VK_LSHIFT)

def walk_forward(duration):
    Input.key_down(win32con.VK_LSHIFT)
    Input.key_down(ord('W'))
    _G.wait(duration)
    Input.key_up(ord('W'))
    Input.key_up(win32con.VK_LSHIFT)

def interact(delay=0.1):
    Input.trigger_key(ord('F'))
    _G.wait(delay)

def close(delay=0.1):
    Input.trigger_key(win32con.VK_ESCAPE)
    _G.wait(delay)
