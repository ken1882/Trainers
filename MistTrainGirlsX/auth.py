import _G
import requests
import game

def reauth_game():
  session = requests.Session()
  with open(f"{_G.DCTmpFolder}/dmmcookies.key") as fp:
    raw = fp.read()
  for line in raw.split(';'):
    k,v = line.strip().split('=')
    session.cookies.set(k, v)
  print(session.cookies)