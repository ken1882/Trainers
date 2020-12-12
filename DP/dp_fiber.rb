PirateMissionPos = [[333,576], [416,825]]
SpiritPowderPos = [[210,402], [277,403], [350,404], [213,464], [278,464], [361,466]]
SpiritPowderOKPos = [281, 587]

def start_interact_fiber
  loop do
    break unless $flag_working
    Input.key_down(Keymap[:vk_F])
    Fiber.yield
    Input.key_up(Keymap[:vk_F])
  end
end

def start_pirate_fiber
  loop do
    break unless $flag_working
    Input.key_down(Keymap[:vk_F])
    wait(0.3)
    Input.key_up(Keymap[:vk_F])
    
    pos = PirateMissionPos[0]
    Input.set_cursor(*pos)
    wait(0.1)

    Input.click_l false,false
    Input.click_l false,false
    
    pos = PirateMissionPos[1]
    Input.set_cursor(*pos)
    wait(0.1)

    Input.click_l false,false
    Input.click_l false,false
    wait(0.8)
  end
end

def start_sp_fiber(index)
  loop do
    break unless $flag_working
    Input.set_cursor(*SpiritPowderPos[index])
    Input.click_l false,false
    Input.click_l false,false
    Input.set_cursor(*SpiritPowderOKPos)
    Input.click_l false,false
    wait 0.1
  end
end

WindowWidth  = 1208
WindowHeight = 764
Accounts, Password, CharIndex = eval(File.read("dp_credential.rb"))
EnterAccountPos = [650, 480]
EnterGamePos    = [1095, 688]
LogoutPos       = [1156, 735]
CharacterListPos = [[359,694],[454,691],[554,691],[637,690],[746,693],[844,689]]
CharacterScreenPos   = [[1141, 693], [601, 691]]
CharacterScreenPixel = [[21, 17, 13], [28, 19, 11]]
HpBarPos = [109, 73]
MpBarPos = [113, 85]
HpBarColor = [211, 49, 2]
MpBarColor = [12, 130, 170]
SystemMenuPos = [722, 55]
GroupCarePos = [682, 120]
CharSelectionPos = [608, 387]

def start_login_fiber
  Graphics.move_window($APP_HWND, 0, 0, WindowWidth, WindowHeight)
  
  Accounts.each_with_index do |acc, index|
    # Login details
    puts "Login #{acc}"
    acc.each_char{|ch| Input.trigger_key(ch.upcase.ord, false); Fiber.yield }
    Input.trigger_key Keymap[:vk_enter]
    Password[index].each do |kbind|
      kbind.each{|ch| Input.key_down(ch, false); Fiber.yield}
      wait 0.03
      kbind.each{|ch| Input.key_up(ch, false); Fiber.yield}
    end
    wait(0.1)
    Input.trigger_key(Keymap[:vk_enter], false)
    
    # Wait character selection screen
    wait(5)
    loop do
      break if Graphics.screen_pixels_matched? CharacterScreenPos,CharacterScreenPixel
      puts "Waiting for characters screen..."
      wait(1)
    end

    # Select character
    3.times do
      px = CharacterListPos.at(CharIndex[index]).first + rand(15)
      py = CharacterListPos.at(CharIndex[index]).last  + rand(15)
      Input.moveto(px, py); Fiber.yield;
      Input.click_l(false,true);
      wait(0.1+rand.floor(2)/2)
    end

    # Login character
    px = EnterGamePos.first + rand(15)
    py = EnterGamePos.last  + rand(5)
    Input.moveto(px-rand(10), py-rand(3)); wait(0.1+rand.floor(2)/2);
    Input.click_l(false,true); Fiber.yield; Input.click_l(false,true);
    wait(0.5+rand.floor(2))

    # Wait game loaded
    wait(5)
    loop do
      break if Graphics.screen_pixels_matched?(
        [HpBarPos, MpBarPos], [HpBarColor, MpBarColor]        
      )
      puts "Waiting for loading complete..."
      wait(1)
    end
    puts "Game Loaded, wait 15 seconds to fully loaded"
    wait(15)
    
    # Group care
    puts "Starting group care"
    Input.trigger_key(Keymap[:vk_esc])
    wait(1)
    Input.moveto(*GroupCarePos); wait(0.1+rand.floor(2));
    Input.click_l(false,true)
    wait(1)
    puts "Dancing, wait for 15 seconds"
    Input.trigger_key( [Keymap[:vk_Q],Keymap[:vk_R],Keymap[:vk_E]].at(rand(3)) )
    wait(15) # dancing

    # Logout
    puts "Logout"
    Input.moveto(*SystemMenuPos); wait(0.1+rand);
    Input.click_l(false,true)
    wait(1)
    px = CharSelectionPos.first + rand(10); py = CharSelectionPos.last + rand(5)
    Input.moveto(px,py); wait(1);
    3.times{ Input.click_l(false,true); wait(0.3); }
    
    # Wait character selection screen
    wait(3)
    loop do
      break if Graphics.screen_pixels_matched? CharacterScreenPos,CharacterScreenPixel
      puts "Waiting for characters screen..."
      wait(1)
    end
    Input.moveto(*LogoutPos); wait(0.1+rand);
    Input.click_l(false,true); Fiber.yield; Input.click_l(false,true);
    wait(1.5+rand.floor(2))
  end    
end
