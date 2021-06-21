require 'win32/api'
require 'win32con'
include Win32CON

module Win32API
  GetWindowThreadProcessId_ = Win32::API.new('GetWindowThreadProcessId', 'LL', 'L', 'user32')
  GetForegroundWindow_ = Win32::API.new('GetForegroundWindow', 'V', 'L', 'user32')
  GetSystemMetrics_    = Win32::API.new('GetSystemMetrics', 'L', 'L', 'user32')
  GetDesktopWindow_    = Win32::API.new('GetDesktopWindow', 'V', 'L', 'user32')
  GetDeviceContext_    = Win32::API.new('GetDC', 'L', 'L', 'user32')
  GetPixel_            = Win32::API.new('GetPixel', 'LLL', 'L', 'gdi32')
  MoveWindow_          = Win32::API.new('MoveWindow', 'LLLLLL', 'L', 'user32')
  EnumWindows_         = Win32::API.new('EnumWindows', 'KL', 'L', 'user32')
  GetWindowText_       = Win32::API.new('GetWindowText', 'LPI', 'I', 'user32')
  GlobalAlloc_         = Win32::API.new('GlobalAlloc', 'LL', 'L', 'kernel32')
  GlobalLock_          = Win32::API.new('GlobalLock', 'L', 'L', 'kernel32')
  GlobalUnlock_        = Win32::API.new('GlobalUnlock', 'L', 'L', 'kernel32')
  CopyMemory_          = Win32::API.new('RtlMoveMemory', 'LPL', 'V', 'ntdll')
  GetLastError_        = Win32::API.new('GetLastError', 'V', 'L', 'kernel32')
  OpenClipboard_       = Win32::API.new('OpenClipboard', 'L', 'L', 'user32')
  SetClipboardData_    = Win32::API.new('SetClipboardData', 'LL', 'L', 'user32')
  CloseClipboard_      = Win32::API.new('CloseClipboard', 'V', 'L', 'user32')
  EmptyClipboard_      = Win32::API.new('EmptyClipboard', 'V', 'L', 'user32')
  MultiByteToWideChar_ = Win32::API.new('MultiByteToWideChar', 'ILSIPI', 'I', 'kernel32')
  GetWindowRect_       = Win32::API.new('GetWindowRect', 'LP', 'I', 'user32')
  
  SendMessage_         = Win32::API.new('SendMessage', 'LLLL', 'L', 'user32')
  GetAsyncKeyState_    = Win32::API.new('GetAsyncKeyState', 'L', 'L', 'user32')
  GetCursorPos_        = Win32::API.new('GetCursorPos', 'P', 'V', 'user32')
  SetCursorPos_        = Win32::API.new('SetCursorPos', 'LL', 'V', 'user32')
  MouseEvent_          = Win32::API.new('mouse_event', "LLLLL", 'V', 'user32')
  KeybdEvent_          = Win32::API.new('keybd_event', 'LLLP', 'V', 'user32')
  
  GMEM_MOVEABLE = 0x02
  SWP_SHOWWINDOW = 0x40
  
  module_function
  def GetWindowRect(hwnd)
    rect = [0,0,0,0].pack("L*")
    GetWindowRect_.call($AppHwnd, rect)
    return rect.unpack("L*")
  end

  def GetCursorPos
    pos = [0,0].pack("LL")
    GetCursorPos_.call(pos)
    return pos.unpack("LL")
  end
  
  def GetForegroundWindow; return GetForegroundWindow_.call; end
  
  def GetWindowText(hwnd, buflen=0xff)
    buffer = "\0" * buflen
    GetWindowText_.call(hwnd, buffer, buflen)
    return buffer.strip
  end
  
  def EnumWindows(lparam, &block)
    _EnumWindowsProc = Win32::API::Callback.new('LP', 'I', &block)
    EnumWindows_.call(_EnumWindowsProc, lparam)
  end
  
  def SendMessage(hwnd, msg, wParam, lParam)
    return SendMessage_.call(hwnd,msg,wParam,lParam)
  end

  def GetAsyncKeyState(vk)
    return (GetAsyncKeyState_.call(vk) & 0x8000) > 0
  end

  def MouseEvent(dwFlags, x, y, dwData, dwExtraInfo)
    return MouseEvent_.call(dwFlags, x, y, dwData, dwExtraInfo)
  end

  def KeybdEvent(bVk, bScan, dwFlags, dwExtraIngo)
    return KeybdEvent_.call(bVk, bScan, dwFlags, dwExtraInfo)
  end
  
  def MoveWindow(hwnd, x, y, w, h, repaint=true); return MoveWindow_.call(hwnd,x,y,w,h,repaint); end
  def GetPixel(hdc, x, y);              return GetPixel_.call(hdc, x, y);             end
  def GetDesktopWindow;                 return GetDesktopWindow_.call;                end
  def GetDeviceContext(hwnd);           return GetDeviceContext_.call(hwnd);          end
  def GlobalAlloc(uFlags, dwBytes);     return GlobalAlloc_.call(uFlags, dwBytes);    end
  def GlobalLock(hMem);                 return GlobalLock_.call(hMem);                end
  def CopyMemory(dest, src, len);       return CopyMemory_.call(dest, src, len);      end
  def GlobalUnlock(hMem);               return GlobalUnlock_.call(hMem);              end
  def OpenClipboard(hwnd);              return OpenClipboard_.call(hwnd);             end
  def EmptyClipboard;                   return EmptyClipboard_.call;                  end
  def SetClipboardData(uFormat, hMem);  return SetClipboardData_.call(uFormat, hMem); end
  def CloseClipboard;                   return CloseClipboard_.call;                  end
  def SetCursorPos(x,y);                return SetCursorPos_.call(x,y);               end

end