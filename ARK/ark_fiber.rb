def start_interact_fiber
  begin
    loop{ Input.mouse_ldown(true,false); Fiber.yield; }
  ensure
    Input.mouse_lup(true,false)
  end
end

def start_walk_fiber
  begin
    loop{ Input.key_down(Keymap[:vk_W]); Fiber.yield; }
  ensure
    Input.mouse_lup(true,false)
  end
end

TimesPerRefresh = 50
RefershProc = Proc.new{
  puts "Replenishing"
  Input.trigger_key(Keymap[:vk_I]); wait(1.5);
  # eat
  Input.moveto(538,286); wait(0.3);
  Input.trigger_key(Keymap[:vk_E]); wait(0.5);
  # transfer
  Input.moveto(251,290); wait(0.3);
  Input.click_l(true,false); wait(0.1);
  Input.click_l(true,false); wait(0.3);
  Input.moveto(627,280); wait(0.3);
  Input.trigger_key(Keymap[:vk_E]); wait(0.3);
  Input.trigger_key(Keymap[:vk_I]); wait(1);
  # open transfer gui
  Input.click_l(true,false); wait(1.5);
  Input.moveto(963,946); wait(0.3);
  Input.click_l(true,false); wait(0.3);
  Input.moveto(958,809); wait(0.3);
  Input.click_l(true,false); wait(0.3);
  Input.moveto(596,950); wait(0.3);
  Input.click_l(true,false); wait(1);
  Input.moveto(963,946); wait(0.3);
  Input.click_l(true,false); wait(0.3);
  Input.moveto(939,836); wait(0.3);
  Input.click_l(true,false); wait(0.3);
  Input.moveto(596,950); wait(0.3);
  Input.click_l(true,false); wait(1);
  Input.moveto(1320,948); wait(0.3);
  Input.click_l(true,false); wait(1);
  Input.trigger_key(Keymap[:vk_1]); wait(0.3);
  # drink
  Input.cursor_move(-400, 0, 10); wait(1);
  Input.trigger_key(Keymap[:vk_E]); wait(0.3);
  Input.cursor_move(400, 0, 10); wait(1);
}
def start_slaughter_fiber(cnt=9999)
  cnt.to_i.times do |i|
    puts "Execute #{i+1}/#{cnt} times"
    Input.key_down(Keymap[:vk_E])
    wait(0.8)
    Input.moveto(765,345)
    wait(2.5)
    Input.key_up(Keymap[:vk_E])
    wait(0.3)
    Input.trigger_key(Keymap[:vk_2])
    wait(1.2)
    9.times{ Input.click_l(true, false); wait(0.6) }
    Input.trigger_key(Keymap[:vk_3])
    wait(1.5)
    Input.click_l(true, false)
    wait(0.8)
    Input.trigger_key(Keymap[:vk_4])
    wait(1.5)
    Input.click_l(true, false)
    wait(0.8)
    Input.trigger_key(Keymap[:vk_1])
    wait(1.2)
    RefershProc.call if (i+1) % TimesPerRefresh == 0
  end
end