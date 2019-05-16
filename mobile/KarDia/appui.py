import win32api, win32gui, win32ui, const, util, copy
from PIL import Image
from ctypes import windll

Initialized = False

def uwait(sec):
  util.wait(sec)

def initialize():
  if const.AppHwnd == 0:
    raise Exception("Invalid Hwnd")
  Initialized = True
  const.HwndDC = win32gui.GetWindowDC(const.AppHwnd)
  const.MfcDC  = win32ui.CreateDCFromHandle(const.HwndDC)
  const.SaveDC = const.MfcDC.CreateCompatibleDC()
  const.Bitmap = win32ui.CreateBitmap()
  const.Bitmap.CreateCompatibleBitmap(const.MfcDC, const.AppRect[2], const.AppRect[3])
  const.SaveDC.SelectObject(const.Bitmap)

def print_window():
  result = windll.user32.PrintWindow(const.AppHwnd, const.SaveDC.GetSafeHdc(), 1)
  bmpinfo = const.Bitmap.GetInfo()
  bmpstr  = const.Bitmap.GetBitmapBits(True)
  im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
  if result == 1:
    pixels = im.load()
  return pixels
  
def terminate():
  win32gui.DeleteObject(const.Bitmap.GetHandle())
  const.SaveDC.DeleteDC()
  const.MfcDC.DeleteDC()
  win32gui.ReleaseDC(const.AppHwnd, const.HwndDC)