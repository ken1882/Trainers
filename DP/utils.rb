GetWindowThreadProcessId = Win32::API.new('GetWindowThreadProcessId', 'LL', 'L', 'user32')
GetForegroundWindow = Win32::API.new('GetForegroundWindow', 'V', 'L', 'user32')
EnumWindows     = Win32::API.new('EnumWindows', 'KL', 'L', 'user32')
GetWindowText   = Win32::API.new('GetWindowText', 'LPI', 'I', 'user32')
EnumWindowsProc = Win32::API::Callback.new('LP', 'I'){ |handle, param|
  buf = "\0" * 200
  GetWindowText.call(handle, buf, 200);
  buf.encode!('UTF-8', 'binary', invalid: :replace, undef: :replace, replace: '')
  text = buf.strip
  flag_found = false
  
  if text.downcase.match(/dragon/i)
    $APP_Hwnd = handle
    puts "Process found: `#{text}` (0x#{handle.to_s 16})"
    flag_found = true
  end
  !flag_found # Proc return whether enum continues
}

$HwndStack = []

module Util 
  GMEM_MOVEABLE = 0x02

  GlobalAlloc  = Win32::API.new('GlobalAlloc', 'LL', 'L', 'kernel32')
  GlobalLock   = Win32::API.new('GlobalLock', 'L', 'L', 'kernel32')
  GlobalUnlock = Win32::API.new('GlobalUnlock', 'L', 'L', 'kernel32')
  CopyMemory   = Win32::API.new('RtlMoveMemory', 'LPL', 'V', 'ntdll')
  GetLastError = Win32::API.new('GetLastError', 'V', 'L', 'kernel32')
  OpenClipboard    = Win32::API.new('OpenClipboard', 'L', 'L', 'user32')
  SetClipboardData = Win32::API.new('SetClipboardData', 'LL', 'L', 'user32')
  CloseClipboard   = Win32::API.new('CloseClipboard', 'V', 'L', 'user32')
  EmptyClipboard   = Win32::API.new('EmptyClipboard', 'V', 'L', 'user32')
  MultiByteToWideChar = Win32::API.new('MultiByteToWideChar', 'ILSIPI', 'I', 'kernel32')
  
  module_function
  def str2clipboard(ss)
    wss   = multi_to_wide(ss)
    wslen = wss.bytes.size
    h_mem = GlobalAlloc.call(GMEM_MOVEABLE, wslen)
    a_mem = GlobalLock.call(h_mem)
    CopyMemory.call(a_mem, wss, wslen)
    GlobalUnlock.call(h_mem)
    OpenClipboard.call(0)
    begin
      EmptyClipboard.call()
      SetClipboardData.call(CF_UNICODETEXT, h_mem)
    ensure
      CloseClipboard.call()
    end
  end

  def switch2foreground
    _hwnd = GetForegroundWindow.call()
    buffer = "\0" * 0xff
    GetWindowText.call(_hwnd, buffer, 0xff)
    buffer = (buffer.strip rescue '')
    puts "Switched to foreground Hwnd: 0x#{_hwnd.to_s 16}; Title: #{buffer}"
    $HwndStack.push($APP_Hwnd)
    $APP_Hwnd = _hwnd
  end
end
