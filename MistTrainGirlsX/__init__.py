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
