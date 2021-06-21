require 'win32/api'
require 'win32con'
require 'win32con/keymap'
include Win32CON
require 'windows/unicode'
include Windows::Unicode

require_relative 'win32api'
require_relative 'native'
require_relative 'graphics'
require_relative 'input'
require_relative 'utils'
require_relative 'fibers'

FPS = (1.0 / 120)

$AppHwnd = 0
$flag_running = true
$flag_paused  = false
$flag_working = false
$flag_pressed = false
$fiber = nil
$working_stage = 0


$HwndStack = []
WorkerFibers = [

]
SelectedWorker = WorkerFibers.find{|f| f if f.match ARGV[0]} rescue nil

if SelectedWorker
  puts "Worker selected: #{SelectedWorker}"
else
  puts "No worker selected"
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
        
      end
    else
      puts "Worker terminated"
      $fiber = nil
    end
  elsif Input.trigger?(Keymap[:vk_f7])
    $flag_paused ^= true
    puts $flag_paused ? "Program paused" : "Program unpaused"
  elsif Input.trigger?(Keymap[:vk_f6])
    pos = Input.get_cursor_pos
    puts "#{pos}; #{Graphics.get_pixel(*pos).rgb}"
  elsif Input.trigger?(Keymap[:vk_f5])
    _hwnd = Win32API.GetForegroundWindow
    puts "Foreground Hwnd: 0x#{_hwnd.to_s 16}; Title: #{Win32API.GetWindowText.call(_hwnd)}"
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
  Utils.find_app_window
  notfound_exit if ($AppHwnd || 0) == 0
  Graphics.init
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
  Input.mouse_lup false,true   if $flag_pressed
  Input.mouse_lup false,false  if $flag_pressed
  Input.mouse_rup true,true    if $flag_pressed
  Input.mouse_rup true,false   if $flag_pressed
end
