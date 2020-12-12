require 'win32/api'
require 'win32con'
require 'win32con/keymap'
include Win32CON

require_relative 'dp_fiber'
require_relative 'dp_pixel'

$APP_Hwnd = 0

SendMessage = Win32::API.new('SendMessage', 'LLLL', 'L', 'user32')
GetWindowThreadProcessId = Win32::API.new('GetWindowThreadProcessId', 'LL', 'L', 'user32')
GetAsyncKeyState = Win32::API.new('GetAsyncKeyState', 'L', 'L', 'user32')
GetCursorPos = Win32::API.new('GetCursorPos', 'P', 'V', 'user32')
SetCursorPos = Win32::API.new('SetCursorPos', 'LL', 'V', 'user32')
MouseEvent = Win32::API.new('mouse_event', "LLLLL", 'V', 'user32')
GetForegroundWindow = Win32::API.new('GetForegroundWindow', 'V', 'L', 'user32')
KeybdEvent = Win32::API.new('keybd_event', 'LLLP', 'V', 'user32')
GetSystemMetrics = Win32::API.new('GetSystemMetrics', 'L', 'L', 'user32')

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

FPS = (1 / 120)

$flag_running = true
$flag_paused  = false
$flag_working = false
$flag_pressed = false

$PrimaryScreenWidth  = GetSystemMetrics.call(SM_CXSCREEN)
$PrimaryScreenHeight = GetSystemMetrics.call(SM_CYSCREEN)

module Input
  @keystate  = Array.new(0xff){0}
  @mouse_pos = [0,0]

  module_function
  def update
    0xff.times do |i|
      @keystate[i] = (GetAsyncKeyState.call(i) & 0x8000) > 0 ? @keystate[i] + 1 : 0
    end
  end

  def trigger?(kcode)
    @keystate[kcode] == 1
  end

  def keystate; @keystate; end

  def mouse_rdown(use_msg, apply_pos)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_RBUTTONDOWN, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_RIGHTDOWN
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = true
  end

  def mouse_rup(use_msg, apply_pos)
    mx = apply_pos ? @mouse_pos[0] : 0
    my = apply_pos ? @mouse_pos[1] : 0
    if use_msg
      SendMessage.call($APP_Hwnd, WM_RBUTTONUP, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_RIGHTUP
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = false
  end

  def mouse_ldown(use_msg,apply_pos)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_LBUTTONDOWN, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_LEFTDOWN
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = true
  end

  def mouse_lup(use_msg,apply_pos)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_LBUTTONUP, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_LEFTUP
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = false
  end

  def click_l(use_msg,apply_pos)
    mouse_ldown(use_msg,apply_pos)
    wait(0.03)
    mouse_lup(use_msg,apply_pos)
  end

  def click_r(use_msg,apply_pos)
    mouse_rdown(use_msg,apply_pos)
    wait(0.03)
    mouse_rup(use_msg,apply_pos)
  end

  def key_down(kid, use_msg=true)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_KEYDOWN, kid, 0)
    else
      KeybdEvent.call(kid, 0, 0, 0)
    end
    $flag_pressed = true
  end

  def key_up(kid, use_msg=true)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_KEYUP, kid, 0)
    else
      KeybdEvent.call(kid, 0, 2, 0)
    end
    $flag_pressed = false
  end

  def trigger_key(kid, use_msg=true)
    key_down(kid, use_msg)
    wait(0.03)
    key_up(kid, use_msg)
  end

  def set_cursor(x,y,use_event=false)
    @mouse_pos = [x,y]
    return SetCursorPos.call(x,y) unless use_event
    x = (x * 0xffff / $PrimaryScreenWidth).to_i
    y = (y * 0xffff / $PrimaryScreenHeight).to_i
    MouseEvent.call(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, x, y, 0, 0)
  end

  def moveto(x,y,speed=10)
    pos = [0, 0].pack("LL")
    GetCursorPos.call(pos)
    cx,cy = pos.unpack("LL")
    dx = x - cx; dy = y - cy;
    cnt = (Math.hypot(dx,dy) / speed).to_i
    angle = Math.atan2(dy, dx)
    dx = speed * Math.cos(angle)
    dy = speed * Math.sin(angle)
    cnt.times{ cx += dx; cy += dy; self.set_cursor(cx, cy, true); wait(0.01); }
    self.set_cursor(x, y, false); self.set_cursor(x, y, true);
  end
end

$fiber = nil
$working_stage = 0

WaitInterval = 0.01
def wait(sec)
  (sec / WaitInterval).to_i.times do
    sleep(WaitInterval)
    Fiber.yield
  end
end

$HwndStack = []

def switch2foreground
  _hwnd = GetForegroundWindow.call()
  buffer = "\0" * 0xff
  GetWindowText.call(_hwnd, buffer, 0xff)
  buffer = (buffer.strip rescue '')
  puts "Switched to foreground Hwnd: 0x#{_hwnd.to_s 16}; Title: #{buffer}"
  $HwndStack.push($APP_Hwnd)
  $APP_Hwnd = _hwnd
end

def main_update
  Input.update
  if Input.trigger?(Keymap[:vk_f8])
    $flag_working ^= true
    $flag_paused = false
    puts "Working: #{$flag_working}"
    if $flag_working
      # $fiber = Fiber.new{start_pirate_fiber}
      # $fiber = Fiber.new{start_interact_fiber}
      # $fiber = Fiber.new{start_sp_fiber 1}
      switch2foreground; $fiber = Fiber.new{start_login_fiber};
    else
      puts "Worker terminated"
      $fiber = nil
    end
  elsif Input.trigger?(Keymap[:vk_f7])
    $flag_paused ^= true
  elsif Input.trigger?(Keymap[:vk_f6])
    pos = [0, 0].pack("LL")
    GetCursorPos.call(pos)
    pos = pos.unpack("LL")
    puts "#{pos}; #{Graphics.get_pixel(*pos).rgb}"
  elsif Input.trigger?(Keymap[:vk_f5])
    _hwnd = GetForegroundWindow.call()
    buffer = "\0" * 0xff
    GetWindowText.call(_hwnd, buffer, 0xff)
    puts "Foreground Hwnd: 0x#{_hwnd.to_s 16}; Title: #{buffer.strip}"
  end

  begin
    $fiber.resume if $fiber && !$flag_paused && $flag_working
  rescue FiberError
    puts "Worker ended"
    $fiber = nil
    $flag_working = false
  end
  $flag_running = false if Input.trigger?(Keymap[:vk_f9])
end

def notfound_exit
  puts "Program not found!"
  exit
end

def start
  EnumWindows.call(EnumWindowsProc, 0)
  notfound_exit if ($APP_Hwnd || 0) == 0
  puts "Press F8 to start, F9 to stop program"
  while $flag_running
    sleep(FPS)
    main_update
  end
end

begin
  start
rescue SystemExit, Interrupt
  exit
ensure
  puts "Bye!"
  if $flag_pressed
    Input.mouse_rup(false,true)
    Input.mouse_rup(false,false)
    Input.mouse_rup(true,true)
    Input.mouse_rup(false,false)
  end
end
