require 'win32/api'
require 'win32con'
require 'win32con/keymap'

include Win32CON

$MC_Hwnd = 0

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
  if text.downcase.match(/minecraft(.+)(\d+)/i)
    $MC_Hwnd = handle
    puts text
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
    SendMessage.call($MC_Hwnd, WM_RBUTTONDOWN, 0, 0)
    $flag_pressed = true
  end

  def mouse_rup
    SendMessage.call($MC_Hwnd, WM_RBUTTONUP, 0, 0)
    $flag_pressed = false
  end

  def mouse_ldown
    SendMessage.call($MC_Hwnd, WM_LBUTTONDOWN, 0, 0)
    $flag_pressed = true
  end

  def mouse_lup
    SendMessage.call($MC_Hwnd, WM_LBUTTONUP, 0, 0)
    $flag_pressed = false
  end
end

def main_update
  Input.update
  if Input.trigger?(Keymap[:vk_f8])
    # $flag_pressed ? Input.mouse_rup : Input.mouse_rdown
    puts $flag_pressed ? "Press end" : "Press start"
    $flag_pressed ? Input.mouse_lup : Input.mouse_ldown
  end
  $flag_running = false if Input.trigger?(Keymap[:vk_f9])
end

def notfound_exit
end

def start
  EnumWindows.call(EnumWindowsProc, 0)
  notfound_exit if ($MC_Hwnd || 0) == 0
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
  Input.mouse_rup if $flag_pressed
  Input.mouse_lup if $flag_pressed
end
