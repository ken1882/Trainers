module DunarTemple
  extend Grinding  
  
  TimesPerClearInventory = 1
  TimesPerJBBuff = 3
  TimesPer302ShardCombine = 3
  TimesPerEquipmentEnhance = 9
  TimesPerShardDiscard = 2
  TimesPerAutoRestart = 12
  
  ExctractBarPos     = [[856, 804],[845, 809],[959, 806]]
  ExctractBarColor   = [[2, 65, 92],[39, 33, 32],[126, 153, 158]]
  DungeonMapPos   = [1750,864]
  DungeonMapColor =  [31,33,25]
  FlagHasJB = false
  FlagHasMerchant = false
  FlagHasCombiner  = false

  @timer_run = 0
  
  module_function
  def start
    # return p in_dungeon?
    # return Combat.reset_view
    # return start_room3
	  # return p hud_opened?
    # return clear_inventory
    # return p Combat.target_reachable?
    # return combine_shards(true)
    # return discard_shards
    # return extract_loots
	  # return shop_sells
    # return enhance_equipments
    if FlagHasJB
      get_jb_buff
      rotateX(-90-rand(20))
    end
    loop do 
      @timer_run += 1
      puts "Running ##{@timer_run} time"
      Input.zoomout 0x800+rand(0x300)
      Combat.reset_view; uwait(0.5);
      reset_dungeon; uwait(2);
      enter_dungeon; uwait(3);
      select_difficulty; wait(8);
      wait_until_transition_ok; uwait(2.5);
      
      if !in_dungeon?
        puts "Not in dungeon"
        return logout
      end

      Combat.reset_view
      start_room1 
      if $flag_combat_dead
        unstuck; uwait 3;
        terminate; $flag_combat_dead = false;
        next
      end
      reposition
      
      start_room2
      if $flag_combat_dead
        unstuck; uwait 3;
        terminate; $flag_combat_dead = false;
        next
      end
      reposition
      
      start_room3
      if $flag_combat_dead
        unstuck; uwait 3;
        terminate; $flag_combat_dead = false;
        next
      end

      terminate
    end
  end

  def terminate
    leave
    wait_until_transition_ok;
    3.times do |i|
      puts "#{3-i} seconds until redo the dungeon"
      wait(0.8)
    end
    Combat.earth_shield; uwait 2;
    # Input.trigger_key Keymap[:vk_esc],false; uwait 1;
    if FlagHasJB && @timer_run % TimesPerJBBuff == 0
      rotateX(-75)
      Input.key_down Keymap[:vk_W],false; uwait 0.95;
      Input.key_up Keymap[:vk_W]; uwait 1;
      if $flag_auto_restart && @timer_run % TimesPerAutoRestart == 0
        puts "Restarting program"
        args = ARGV.join ' '
        cmd = "ruby dp.rb #{args} --auto-start"
        exec cmd
      end
      get_jb_buff
      rotateX(-90-rand(20))
    else
      rotateX(190+rand(30))
      if $flag_auto_restart && @timer_run % TimesPerAutoRestart == 0
        puts "Restarting program"
        args = ARGV.join ' '
        cmd = "ruby dp.rb #{args} --auto-start"
        exec cmd
      end
    end  
  end
  
  def reposition
    Combat.unsummon_dragon; uwait 1;
    unstuck(true); extract_loots;
    wt = $timer_unstuck - Time.now.to_i
    puts "#{wt} seconds before teleport"
    wt.times{|i| wait(0.95);}; uwait 2;
    wait_until_transition_ok; uwait 2;
    3.times{Input.zoomout 0x1000+rand(0x200); uwait 0.3;}
  end

  def start_room1 
    puts "Starting room#1"
    Combat.earth_shield; uwait 1;
    Combat.reset_view; uwait 1;
    move_left 1.7
    move_front 1.2,true,false
    rotateX(90)
    9.times{wait(0.1); Input.trigger_key Keymap[:vk_space],false}
    rotateX(90)
    3.times{wait(0.1); Input.trigger_key Keymap[:vk_space],false}
    uwait(0.6)
    Input.key_up(Keymap[:vk_W],false)
    rotateX(-180)
    Combat.summon_dragon; uwait(0.5)
    Input.trigger_key Keymap[:vk_f2]
    uwait(0.1)
    Combat.forwardjump
    # Input.trigger_key Keymap[:vk_f1]
    Combat.engage
  end

  def start_room2 
    puts "Starting room#2"
    Combat.earth_shield; uwait 1;
    Combat.reset_view; uwait 1;
    move_front 2.1,true
    Input.key_down Keymap[:vk_W],false
    Combat.summon_dragon; uwait(0.5)
    Input.trigger_key Keymap[:vk_f2]; uwait(0.6);
    Combat.blink;
    Input.key_up Keymap[:vk_W],false; uwait(0.5);
    Thread.new{
      sleep(0.8)
      2.times{ Input.trigger_key Keymap[:vk_space],false; sleep(0.1); }
      sleep(0.6)
      vk = Keymap[:vk_4]
      3.times{Input.trigger_key(vk); sleep(0.05);}
      rotateY(90, 80, true)
      3.times{Input.click_l(false, true); sleep(0.05);}
      rotateY(-88, 80, true)
      Combat.cd(vk, 15)
    }
    move_front(2.5,true,true,false)
    Combat.blink; uwait(0.5);
    Combat.backjump
    uwait(0.1)
    # Input.trigger_key Keymap[:vk_f1]
    Combat.backjump; Combat.roll;
    Combat.healbuff
    Combat.engage
  end

  def start_room3
    puts "Start room#3"
    Combat.earth_shield; uwait 1;
    Combat.reset_view; uwait 1;
    move_front 9.0,true; uwait 0.7;
    move_front 2.0,true; uwait 0.3;
    Combat.backjump
    rotateX(90); uwait 0.5;
    move_front 1.4,true; uwait 0.5;
    Combat.summon_dragon; Combat.backjump;
    Combat.engage
  end

  def leave
    puts "Leaving Dungeon"
    unless $flag_combat_dead
      Combat.unsummon_dragon; uwait 0.3;
      unstuck(true); extract_loots;
      wt = $timer_unstuck - Time.now.to_i
      puts "#{wt} seconds before teleport"
      wt.times{|i| wait(0.95);}; uwait(2);
      Input.trigger_key Keymap[:vk_esc],false; uwait 1;
    end
    Input.zoomout 0x800+rand(0x200)
    clear_inventory if @timer_run % TimesPerClearInventory == 0
    if @timer_run % TimesPerEquipmentEnhance == 0
      puts "Enhance equipment durability"
      Combat.healbuff; uwait 1;
      enhance_equipments; uwait 1;
    end
    3.times{ move_back 1.5 }
    wait 15; uwait 15;
  	Input.zoomout 0x1200+rand(0x200)
  end

  def clear_inventory
    if FlagHasCombiner
      Combat.earth_shield; uwait 2;
      flag_combine302 = (@timer_run % TimesPer302ShardCombine == 0)
      combine_shards(flag_combine302); uwait 2;
      Input.trigger_key Keymap[:vk_esc],false; uwait 0.5;
    end
    Input.trigger_key Keymap[:vk_D],false; uwait 0.5; Combat.earth_shield; uwait 2;
    if @timer_run % TimesPerShardDiscard == 0
      discard_shards; uwait 2;
    end
    if FlagHasMerchant
      Input.trigger_key Keymap[:vk_esc],false; uwait 0.5;
      Input.trigger_key Keymap[:vk_A],false; uwait 0.5; Combat.earth_shield; uwait 2;
      shop_sells; uwait 2;
    end
    puts "Inventory cleared"
  end

  def in_dungeon?
    return Graphics.screen_pixels_matched?([DungeonMapPos],[DungeonMapColor])
  end
end

def start_dunar_temple
  DunarTemple.start
end