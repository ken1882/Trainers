import os
import sys
import logging
from logging import getLogger, StreamHandler, Formatter
from time import sleep
from random import random
from dotenv import load_dotenv

load_dotenv()

ARGV = {}
FPS = (1 / 240)

BROWSER_PROFILE_DIR = './profiles'

Console = None

logger = getLogger('main')
logger.setLevel(logging.DEBUG)
ch = StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = Formatter('%(asctime)s - [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

FlagRunning = True

def log_info(*args, **kwargs):
    global Console
    if Console:
        print('\r')
    logger.info(*args, **kwargs)
    if Console:
        Console.refresh_line()

def log_error(*args, **kwargs):
    global Console
    if Console:
        print('\r')
    logger.error(*args, **kwargs)
    if Console:
        Console.refresh_line()

def log_warning(*args, **kwargs):
    global Console
    if Console:
        print('\r')
    logger.warning(*args, **kwargs)
    if Console:
        Console.refresh_line()

def log_debug(*args, **kwargs):
    global Console
    if Console:
        print('\r')
    logger.debug(*args, **kwargs)
    if Console:
        Console.refresh_line()

def wait(sec):
    sleep(sec)

def uwait(sec):
    sleep(sec + max(random() / 2, sec * random() / 5))

WaitInterval = 0.1
def rwait(sec):
    global WaitInterval,FPS
    times = int(sec // (WaitInterval + FPS))
    for _ in range(times):
        wait(WaitInterval)
        yield
    wait(sec - times * (WaitInterval+FPS))
