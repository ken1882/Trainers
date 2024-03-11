import win32api,win32con,ctypes
import Input
import _G
import time
import multiprocessing
from multiprocessing import Process,Pipe

BASE_INTERVAL_TIME = 0.1
DIR_LEFT  = 1
DIR_RIGHT = 2
