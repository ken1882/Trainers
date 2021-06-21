WaitInterval = 0.05
def wait(sec)
  wt = [WaitInterval - FPS, 0].max
  [(sec / WaitInterval).to_i, 1].max.times do
    sleep(wt) if wt > 0
    Fiber.yield
  end
end

def uwait(_t)
  wait(_t+_t*0.5).floor(2)
end

module Utils
  
  module_function
  def find_app_window
    Win32API.EnumWindows(0){ |handle, param|
      text = Win32API.GetWindowText(handle)
      flag_found = false
      if text.downcase.match(/BlueStacks/i)
        $AppHwnd = handle
        puts "Process found: `#{text}` (0x#{handle.to_s 16})"
        flag_found = true
      end
      !flag_found # Proc return whether enum continues
    }
  end

  def str2clipboard(ss)
    wss   = multi_to_wide(ss)
    wslen = wss.bytes.size
    h_mem = Win32API.GlobalAlloc(GMEM_MOVEABLE, wslen)
    a_mem = Win32API.GlobalLock(h_mem)
    Win32API.CopyMemory(a_mem, wss, wslen)
    Win32API.GlobalUnlock(h_mem)
    Win32API.OpenClipboard(0)
    begin
      Win32API.EmptyClipboard
      Win32API.SetClipboardData(CF_UNICODETEXT, h_mem)
    ensure
      Win32API.CloseClipboard
    end
  end

  def switch2foreground
    _hwnd = Win32API.GetForegroundWindow
    buffer = "\0" * 0xff
    Win32API.GetWindowText(_hwnd)
    buffer = (buffer.strip rescue '')
    puts "Switched to foreground Hwnd: 0x#{_hwnd.to_s 16}; Title: #{buffer}"
    $HwndStack.push($AppHwnd)
    $AppHwnd = _hwnd
  end
end

