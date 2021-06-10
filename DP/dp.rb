require 'win32/api'
require 'win32con'
require 'win32con/keymap'
include Win32CON
require 'windows/unicode'
include Windows::Unicode

require_relative 'dp_pixel'
require_relative 'dp_grind'
require_relative 'dp_fiber'

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

FPS = (1.0 / 120)

$flag_running = true
$flag_paused  = false
$flag_working = false
$flag_pressed = false
$flag_auto_restart = ARGV.include? '-r'; ARGV.delete '-r';

$PrimaryScreenWidth  = GetSystemMetrics.call(SM_CXSCREEN)
$PrimaryScreenHeight = GetSystemMetrics.call(SM_CYSCREEN)

module Input
  @keystate  = Array.new(0xff){0}
  @mouse_pos = [0,0]

  module_function
  def mouse_pos; @mouse_pos; end

  def update
    0xff.times do |i|
      @keystate[i] = (GetAsyncKeyState.call(i) & 0x8000) > 0 ? @keystate[i] + 1 : 0
    end
    pos = [0, 0].pack("LL"); GetCursorPos.call(pos);
    @mouse_pos = pos.unpack("LL")
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
    sleep(0.03)
    mouse_lup(use_msg,apply_pos)
  end

  def click_r(use_msg,apply_pos)
    mouse_rdown(use_msg,apply_pos)
    sleep(0.03)
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
    sleep(0.05)
    key_up(kid, use_msg)
  end

  def set_cursor(x,y,use_event=false)
    @mouse_pos = [x,y]
    return SetCursorPos.call(x,y) unless use_event
    x = (x * 0xffff / $PrimaryScreenWidth).to_i
    y = (y * 0xffff / $PrimaryScreenHeight).to_i
    MouseEvent.call(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, x, y, 0, 0)
  end

  def moveto(x,y,speed=nil)
    _MaxSteps = 42
    cx,cy = @mouse_pos
    dx = x - cx; dy = y - cy;
    if speed.nil?
      default_speed = 10
      cnt = (Math.hypot(dx,dy) / default_speed).to_i
      if cnt > _MaxSteps
        speed = (Math.hypot(dx,dy) / _MaxSteps).to_i
        cnt   = _MaxSteps
      else
        speed = default_speed
      end
    else
      cnt = (Math.hypot(dx,dy) / speed).to_i
    end
    angle = Math.atan2(dy, dx)
    dx = speed * Math.cos(angle)
    dy = speed * Math.sin(angle)
    cnt.times{ cx += dx; cy += dy; self.set_cursor(cx, cy, true); Fiber.yield;}
    self.set_cursor(x, y, false); self.set_cursor(x, y, true);
  end
  
  def zoomout(n)
    MouseEvent.call(MOUSEEVENTF_WHEEL, 0, 0, -n, 0)
  end

  def zoomin(n)
    MouseEvent.call(MOUSEEVENTF_WHEEL, 0, 0, n, 0)
  end
end

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
end

$fiber = nil
$working_stage = 0

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

WorkerFibers = [
  :start_pirate_fiber, :start_interact_fiber, :start_combat_fiber,
  :start_sp_fiber, :start_eggdance_fiber, :start_dunar_temple,
  :start_cod_fiber, :start_mail_fiber,:start_extract_fiber, :start_bag_clear_fiber,
  :start_sell_fiber, :start_auction_fiber
]
SelectedWorker = WorkerFibers.find{|f| f if f.match ARGV[0]} rescue nil

if SelectedWorker
  puts "Worker selected: #{SelectedWorker}"
else
  puts "No worker selected, default set to pirate"
end

def main_update
  Input.update
  if Input.trigger?(Keymap[:vk_f8]) || ($flag_auto_restart && !$flag_first_work)
    if ($flag_auto_restart && !$flag_first_work)
	  puts "Restarting first work task, continue in 3 seconds"
	  sleep 3
	end
    $flag_first_work = true
    $flag_working ^= true
    $flag_paused = false
    puts "Working: #{$flag_working}"
    if $flag_working
      if SelectedWorker
        $fiber = Fiber.new{method(SelectedWorker).call(*ARGV[1..-1])}
      else
        $fiber = Fiber.new{start_pirate_fiber}
        # $fiber = Fiber.new{start_interact_fiber}
        # $fiber = Fiber.new{start_sp_fiber 3}
        # $fiber = Fiber.new{start_dunar_temple}
      end
    else
      puts "Worker terminated"
      $fiber = nil
    end
  elsif Input.trigger?(Keymap[:vk_f7])
    $flag_paused ^= true
    puts $flag_paused ? "Program paused" : "Program unpaused"
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
  Input.mouse_rup false,true   if $flag_pressed
  Input.mouse_rup false,false  if $flag_pressed
  Input.mouse_rup true,true    if $flag_pressed
  Input.mouse_rup true,false   if $flag_pressed
end
