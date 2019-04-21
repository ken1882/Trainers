import PIL.ImageGrab
import win32api, win32con

def getPixel(x=None, y=None):
  if x and y:
    return PIL.ImageGrab.grab().load()[x, y]
  return PIL.ImageGrab.grab().load()


mx, my = win32api.GetCursorPos()
print("Mouse pos: ({}, {})".format(mx, my))
r,g,b = getPixel(mx, my)
print("Pixel Color: R:{} G:{} B:{}".format(r,g,b))