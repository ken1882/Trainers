import game
import player
import combat
import shop
import expedition
import training
import poker
import upgrade
import discord
import derpy_datamanager as dd
import derpy_predict as dp
import sys
from io import StringIO
from time import sleep

game.init()

def daily():
    ostdin = sys.stdin
    shop.main()
    expedition.main()
    training.main()
    try:
        sys.stdin = StringIO('n exp 1 -1'.replace(' ', '\n'))
        combat.main()
    except Exception:
        pass
    try:
        sys.stdin = StringIO('n gold 1 -1'.replace(' ', '\n'))
        combat.main()
    except Exception:
        pass
    sys.stdin = ostdin
    sleep(1)
    res = game.post_request('/api/SendRewards/category/1?isNextMissionComplete=true')
    print(res)
    res = game.post_request('/api/SendRewards/mission/35703269')
    print(res)
    res = game.post_request('/api/SendRewards/mission/1148716694')
    print(res)