require_relative 'dp_combat'
require_relative 'dunar_temple'

PirateMissionPos = [[333,576], [416,825]]
SpiritPowderPos = [[210,402], [277,403], [350,404], [213,464], [278,464], [361,466]]
SpiritPowderOKPos = [281, 587]

def start_interact_fiber
  loop do
    break unless $flag_working
    Input.key_down Keymap[:vk_F],false
    Fiber.yield
    Input.key_up Keymap[:vk_F],false
  end
end

def start_pirate_fiber
  loop do
    break unless $flag_working
    Input.key_down Keymap[:vk_F],false
    wait(0.3)
    Input.key_up Keymap[:vk_F],false
    
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

def start_combat_fiber
  $flag_always_combat = true
  loop{ Combat.engage }
end

WindowWidth  = 1208
WindowHeight = 764
Accounts = []
File.open('dp_credentials.txt') do |file|
  file.each_line do |line|
    next if line.strip.length < 3
    Accounts << [line.strip.split(' ')]
  end
end
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

def start_eggdance_fiber
  Graphics.move_window($APP_HWND, 1, 1, WindowWidth, WindowHeight)
  
  Accounts.each do |ainfo|
    acc, pwd, cidx = ainfo
    # Login details
    puts "Login #{acc}"
    acc.each_char{|ch| Input.type_char(ch); Fiber.yield }
    Input.trigger_key Keymap[:vk_enter],false
    pwd.each_char{|ch| Input.type_char(ch); Fiber.yield }
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
      px = CharacterListPos.at(cidx).first + rand(15)
      py = CharacterListPos.at(cidx).last  + rand(15)
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

FirstShardPos = [1512, 505]
CODAmountPos  = [918, 262]
SendMailPos   = [983, 724]

CopyProc = Proc.new{
  Input.key_down(Keymap[:vk_Lcontrol],false); uwait(0.3);
  Input.trigger_key(Keymap[:vk_C],false); uwait(0.3);
  Input.key_up(Keymap[:vk_Lcontrol,false])
}

PasteProc = Proc.new{
  Input.key_down(Keymap[:vk_Lcontrol],false); uwait(0.3);
  Input.trigger_key(Keymap[:vk_V],false); uwait(0.3);
  Input.key_up(Keymap[:vk_Lcontrol],false)
}

def start_mail_fiber(cnt=nil)
  cnt = ARGV.find{|arg| arg.include? '--count='}.split('=').last
  cnt.to_i.times do
    Input.moveto(*FirstShardPos); uwait(0.2);
    Input.click_r(false,true); uwait(0.2);
    Input.moveto(*SendMailPos); uwait(0.2);
    2.times{ Input.click_l(false,true); uwait(0.05);}
    uwait(0.8)
  end
end

def start_cod_fiber(cnt=nil)
  cnt = ARGV.find{|arg| arg.include? '--count='}.split('=').last
  cnt.to_i.times do
    Input.moveto(*FirstShardPos); uwait(0.2);
    Input.click_r(false,true); uwait(0.2);
    Input.moveto(*CODAmountPos); uwait(0.2);
    2.times{ Input.click_l(false,true); uwait(0.05);}
    PasteProc.call; uwait(0.2);
    Input.moveto(*SendMailPos); uwait(0.2);
    2.times{ Input.click_l(false,true); uwait(0.05);}
    uwait(0.8)
  end
end

def start_extract_fiber
  Grinding.send(:extract_loots)
end

def start_bag_clear_fiber
  Grinding.send :combine_shards,false; uwait 2;
  Input.trigger_key Keymap[:vk_esc],false; uwait 0.5;
  Input.trigger_key Keymap[:vk_D],false; uwait 0.5; Combat.earth_shield; uwait 2;
  Grinding.send :discard_shards; uwait 2;
  Input.trigger_key Keymap[:vk_esc],false; uwait 0.5;
  Input.trigger_key Keymap[:vk_A],false; uwait 0.5; Combat.earth_shield; uwait 2;
  Grinding.send :shop_sells; uwait 2;
  puts "Inventory cleared"
end

def start_sell_fiber
  Grinding.send :shop_sells
end

def start_shardcombine_fiber
  Grinding.send :combine_shards, true
end

def start_auction_fiber
  20.times do 
    item_pos,auction_pos = [1508,498],[201,735]
    Input.moveto(*item_pos); uwait 0.3;
    Input.click_r false,true; uwait 0.3;
    Input.moveto(*auction_pos); uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    uwait(1)
  end
end