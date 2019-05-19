import G, win32api, win32con

keystate = [0 for _ in range(0xff)]
keystate_intern = [0 for _ in range(0xff)]

def update():
  global keystate
  for i in range(0xff):
    if win32api.GetAsyncKeyState(i):
      keystate[i] += 1
      keystate_intern[i] += 1
    else:
      keystate[i] = 0

def clean_intern():
  for i in range(0xff):
    keystate_intern[i] = 0

def is_trigger(i, intern=True):
  if intern:
    return keystate_intern[i] > 0 and keystate_intern[i] <= G.InternUpdateTime
  return keystate[i] == 1

def is_press(i, intern=True):
  if intern:
    return keystate_intern[i] > 0
  return keystate[i] > 0

def is_repeat(i, intern=True):
  if intern:
    return keystate_intern[i] // G.InternUpdateTime
  return keystate[i]