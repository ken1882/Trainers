require 'win32/api'
require 'win32con'
require 'win32con/keymap'

include Win32CON

$GameHwnd = 0

SendMessage = Win32::API.new('SendMessage', 'LLLL', 'L', 'user32')
GetWindowThreadProcessId = Win32::API.new('GetWindowThreadProcessId', 'LL', 'L', 'user32')
GetAsyncKeyState = Win32::API.new('GetAsyncKeyState', 'L', 'L', 'user32')
GetCursorPos = Win32::API.new('GetCursorPos', 'P', 'V', 'user32')
SetCursorPos = Win32::API.new('SetCursorPos', 'LL', 'V', 'user32')
MouseEvent = Win32::API.new('mouse_event', "LLLLL", 'V', 'user32')
KeybdEvent = Win32::API.new('keybd_event', 'LLLP', 'V', 'user32')
GetSystemMetrics = Win32::API.new('GetSystemMetrics', 'L', 'L', 'user32')

EnumWindows     = Win32::API.new('EnumWindows', 'KL', 'L', 'user32')
GetWindowClass   = Win32::API.new('GetClassName', 'LPI', 'I', 'user32')
EnumWindowsProc = Win32::API::Callback.new('LP', 'I'){ |handle, param|
  buf = "\0" * 200
  GetWindowClass.call(handle, buf, 200);
  buf.encode!('UTF-8', 'binary', invalid: :replace, undef: :replace, replace: '')
  cls = buf.strip
  flag_found = false
  if cls == 'UnrealWindow'
    $GameHwnd = handle
    puts "Game found: #{cls} (0x#{handle.to_s(16)})"
    flag_found = true
  end
  !flag_found # Proc return whether enum continues
}

FPS = (1 / 120)

$flag_running = true
$flag_pressed = false
$flag_working = false

module Input
  @keystate = Array.new(0xff){0}
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

  def mouse_rdown
    SendMessage.call($GameHwnd, WM_RBUTTONDOWN, 0, 0)
    $flag_pressed = true
  end

  def mouse_rup
    SendMessage.call($GameHwnd, WM_RBUTTONUP, 0, 0)
    $flag_pressed = false
  end

  def mouse_ldown
    SendMessage.call($GameHwnd, WM_LBUTTONDOWN, 0, 0)
    $flag_pressed = true
  end

  def mouse_lup
    SendMessage.call($GameHwnd, WM_LBUTTONUP, 0, 0)
    $flag_pressed = false
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
    sleep(0.03)
    key_up(kid, use_msg)
  end
end

def start_hammering
  loop do
    Input.mouse_ldown
    24.times{ sleep 0.1; Fiber.yield; }
    Input.mouse_lup
    5.times{ sleep 0.1; Fiber.yield; }
  end
end

def start_turtle
  loop do
    Input.trigger_key Keymap[:vk_1],false
    sleep(2)
    Input.key_down Keymap[:vk_S],false
    sleep(0.2)
    Input.key_up Keymap[:vk_S],false
    (238).times{ sleep 0.5; Fiber.yield; }
  end
end

def start_honey
  loop do
    Input.trigger_key Keymap[:vk_2],false
    sleep(0.3)
    Input.trigger_key Keymap[:vk_1],false
    sleep(2)
    Input.trigger_key Keymap[:vk_E],false
    (8).times{ sleep 0.5; Fiber.yield; }
    Input.trigger_key Keymap[:vk_1],false
    (20).times{ sleep 0.5; Fiber.yield; }
    Input.trigger_key Keymap[:vk_W],false
    sleep(1)
    Input.trigger_key Keymap[:vk_W],false
    sleep(1)
    Input.trigger_key Keymap[:vk_R],false
    (30).times{ sleep 0.5; Fiber.yield; }
    Input.trigger_key Keymap[:vk_3],false
    (70).times{ sleep 0.5; Fiber.yield; }
  end
end

def start_attack
  loop do
    # Input.trigger_key Keymap[:vk_2],false
    # sleep(0.3)

    Input.trigger_key Keymap[:vk_R],false
    sleep(0.3)
    Input.trigger_key Keymap[:vk_1],false
    (6).times{ sleep 0.5; Fiber.yield; }
    
    Input.trigger_key Keymap[:vk_Q],false
    sleep(0.3)
    7.times do
      Input.mouse_ldown
      23.times{ sleep 0.1; Fiber.yield; }
      Input.mouse_lup
      6.times{ sleep 0.1; Fiber.yield; }
    end
  end
end

def start_crystal
  n = 414
  attack = Proc.new{
    Input.mouse_ldown
    5.times{ sleep 0.1; Fiber.yield; }
    Input.mouse_lup
    5.times{ sleep 0.1; Fiber.yield; }
  }
  skill = Proc.new{
    Input.trigger_key(Keymap[:vk_1],false)
    sleep(1.2)
  }
  i = 0
  loop do
    Input.trigger_key(Keymap[:vk_2],false)
    n.times do |i|
      # puts i
      attack.call
      if i == 2 || (i+1) % 24 == 0
        sleep(0.2)
        skill.call
      end
    end
  end
end

def main_update
  Input.update
  if Input.trigger?(Keymap[:vk_F8])
    $flag_working ^= true
    if $flag_working
      $fiber = Fiber.new{ start_hammering }
    else
      $fiber = nil
      Input.mouse_lup
    end
    puts $flag_working ? "Press start" : "Press end"
  elsif Input.trigger? Keymap[:vk_F7]
    $flag_working ^= true
    if $flag_working
      $fiber = Fiber.new{ start_turtle }
    else
      $fiber = nil
    end
    puts $flag_working ? "Press start" : "Press end"
  elsif Input.trigger? Keymap[:vk_F6]
    $flag_working ^= true
    if $flag_working
      $fiber = Fiber.new{ start_honey }
    else
      $fiber = nil
    end
    puts $flag_working ? "Press start" : "Press end"
  elsif Input.trigger? Keymap[:vk_F5]
    $flag_working ^= true
    if $flag_working
      $fiber = Fiber.new{ start_attack }
    else
      $fiber = nil
    end
    puts $flag_working ? "Press start" : "Press end"
  elsif Input.trigger? Keymap[:vk_F4]
    $flag_working ^= true
    if $flag_working
      $fiber = Fiber.new{ start_crystal }
    else
      $fiber = nil
    end
    puts $flag_working ? "Press start" : "Press end"
  end
  $fiber.resume if $fiber && $flag_working
  $flag_running = false if Input.trigger?(Keymap[:vk_F9])
end

def notfound_exit
end

def start
  EnumWindows.call(EnumWindowsProc, 0)
  notfound_exit if ($GameHwnd || 0) == 0
  puts "Press F8 to start/pause, F9 to stop program"
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
  Input.mouse_rup
  Input.mouse_lup
end
