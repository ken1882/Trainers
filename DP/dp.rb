require_relative 'dp_pixel'
require_relative 'dp_grind'
require_relative 'dp_fiber'
require_relative 'input'
require_relative 'utils'

FPS = (1.0 / 120)

$APP_Hwnd = 0 unless $APP_Hwnd
$flag_running = true
$flag_paused  = false
$flag_working = false
$flag_pressed = false

# -r N: auto-restart program after run N times
$flag_auto_restart         = ARGV.include? '-r'
$flag_disable_shardcombine = ARGV.include? '--no-shard-combine'
$flag_disable_itemsell     = ARGV.include? '--no-item-sell'
$flag_auto_start           = ARGV.include? '--auto-start'

puts 'Auto item sell disabled' if $flag_disable_itemsell
puts 'Auto shard combine disable' if $flag_disable_shardcombine


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

WorkerFibers = [
  :start_pirate_fiber, :start_interact_fiber, :start_combat_fiber,
  :start_sp_fiber, :start_eggdance_fiber, :start_dunar_temple,
  :start_cod_fiber, :start_mail_fiber,:start_extract_fiber, :start_bag_clear_fiber,
  :start_sell_fiber, :start_auction_fiber, :start_shardcombine_fiber
]
SelectedWorker = WorkerFibers.find{|f| f if f.match ARGV[0]} rescue nil

if SelectedWorker
  puts "Worker selected: #{SelectedWorker}"
else
  puts "No worker selected, default set to pirate"
end

def main_update
  Input.update
  auto_start = $flag_auto_restart && $flag_auto_start
  if Input.trigger?(Keymap[:vk_f8]) || auto_start
    if auto_start
      $flag_auto_start = false
      puts "Restarting first work task, continue in 3 seconds"
      sleep 3
	  end
    $flag_working ^= true
    $flag_paused = false
    puts "Working: #{$flag_working}"
    if $flag_working
      if SelectedWorker
        $fiber = Fiber.new{method(SelectedWorker).call}
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
