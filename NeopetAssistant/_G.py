import logging
from logging import getLogger, StreamHandler, Formatter
from time import sleep
from random import random
from dotenv import load_dotenv

load_dotenv()

ARGV = {}
FPS = (1 / 240)

IPC_FILE = '.ipc'

logger = getLogger('main')
logger.setLevel(logging.DEBUG)
ch = StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = Formatter('%(asctime)s - [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

FlagRunning = True

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
