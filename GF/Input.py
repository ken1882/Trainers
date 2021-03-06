import G, win32api, win32con

keystate = [0 for _ in range(0xff)]
keystate_intern = [0 for _ in range(0xff)]

class keymap:
  kMOUSE1 = 1
  kMOUSE2 = 2
  kMOUSE3 = 3
  k0 = 48
  k1 = 49
  k2 = 50
  k3 = 51
  k4 = 52
  k5 = 53
  k6 = 54
  k7 = 55
  k8 = 56
  k9 = 57
  kA = 65
  kB = 66
  kC = 67
  kD = 68
  kE = 69
  kF = 70
  kG = 71
  kH = 72
  kI = 73
  kJ = 74
  kK = 75
  kL = 76
  kM = 77
  kN = 78
  kO = 79
  kP = 80
  kQ = 81
  kR = 82
  kS = 83
  kT = 84
  kU = 85
  kV = 86
  kW = 87
  kX = 88
  kY = 89
  kZ = 90
  kENTER = 13
  kRETURN = 13
  kBACKSPACE = 8
  kSPACE = 32
  kESCAPE = 27
  kESC = 27
  kSHIFT = 16
  kTAB = 9
  kALT = 18
  kCTRL = 17
  kCONTROL = 17
  kDELETE = 46
  kDEL = 46
  kINSERT = 45
  kINS = 45
  kPAGEUP = 33
  kPUP = 33
  kPAGEDOWN = 34
  kPDOWN = 34
  kHOME = 36
  kEND = 35
  kLALT = 164
  kLCTRL = 162
  kRALT = 165
  kRCTRL = 163
  kLSHIFT = 160
  kRSHIFT = 161
  kLEFT = 37
  kRIGHT = 39
  kUP = 38
  kDOWN = 40
  kCOLON = 186
  kAPOSTROPHE = 222
  kQUOTE = 222
  kCOMMA = 188
  kPERIOD = 190
  kSLASH = 191
  kBACKSLASH = 220
  kLEFTBRACE = 219
  kRIGHTBRACE = 221
  kMINUS = 189
  kUNDERSCORE = 189
  kPLUS = 187
  kEQUAL = 187
  kEQUALS = 187
  kTILDE = 192
  kF1 = 112
  kF2 = 113
  kF3 = 114
  kF4 = 115
  kF5 = 116
  kF6 = 117
  kF7 = 118
  kF8 = 119
  kF9 = 120
  kF10 = 121
  kF11 = 122
  kF12 = 123
  kArrows = 224

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