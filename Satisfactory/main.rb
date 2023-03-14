require 'win32/api'
require 'win32con'
require 'win32con/keymap'

include Win32CON

$GameHwnd = 0

SendMessage = Win32::API.new('SendMessage', 'LLLL', 'L', 'user32')
GetWindowThreadProcessId = Win32::API.new('GetWindowThreadProcessId', 'LL', 'L', 'user32')
GetAsyncKeyState = Win32::API.new('GetAsyncKeyState', 'L', 'L', 'user32')

EnumWindows     = Win32::API.new('EnumWindows', 'KL', 'L', 'user32')
GetWindowText   = Win32::API.new('GetWindowText', 'LPI', 'I', 'user32')
EnumWindowsProc = Win32::API::Callback.new('LP', 'I'){ |handle, param|
  buf = "\0" * 200
  GetWindowText.call(handle, buf, 200);
  buf.encode!('UTF-8', 'binary', invalid: :replace, undef: :replace, replace: '')
  text = buf.strip
  flag_found = false
  if text.downcase.match(/^Satisfactory$/i)
    $GameHwnd = handle
    puts sprintf("0x%x %s", handle, text)
    flag_found = true
  end
  !flag_found # Proc return whether enum continues
}

FPS = (1 / 120)

$flag_running = true
$flag_pressed = false

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

  def key_down(kid)
    SendMessage.call($GameHwnd, WM_KEYDOWN, kid, 0)
    $flag_pressed = true
  end

  def key_up(kid)
    SendMessage.call($GameHwnd, WM_KEYUP, kid, 0)
    $flag_pressed = false
  end
end

$flag_working = false
def main_update
  Input.update
  vk = 'F'.ord
  if Input.trigger?(Keymap[:vk_f8])
    # $flag_pressed ? Input.mouse_rup : Input.mouse_rdown
    # $flag_pressed ? Input.mouse_lup : Input.mouse_ldown
    # $flag_pressed ? Input.key_up(vk) : Input.key_down(vk)
    $flag_working ^= true
    puts $flag_working ? "Press start" : "Press end"
  end
  if $flag_working
    Input.mouse_ldown
    Input.mouse_lup
    Input.mouse_ldown
    Input.mouse_lup
  end
  $flag_running = false if Input.trigger?(Keymap[:vk_f9])
end

def notfound_exit
end

def start
  EnumWindows.call(EnumWindowsProc, 0)
  notfound_exit if ($GameHwnd || 0) == 0
  puts "Press F8 to start/pause, F9 to stop program"
  while $flag_running
    # sleep(FPS)
    main_update
  end
end

begin
  start
rescue SystemExit, Interrupt
  exit
ensure
  puts "Bye!"
  Input.mouse_rup if $flag_pressed
  Input.mouse_lup if $flag_pressed
end
