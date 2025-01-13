import logging
from logging import getLogger, StreamHandler, Formatter
from time import sleep
from random import random
from dotenv import load_dotenv

load_dotenv()

logger = getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = Formatter('%(asctime)s - [%(name)s] <%(levelname)s> %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def wait(sec):
    sleep(sec)

def uwait(sec):
    sleep(sec + max(random() / 2, sec * random() / 5))