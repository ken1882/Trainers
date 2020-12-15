module DunarTemple
  extend Grinding  
  
  TimesPerClearInventory = 3
  @timer_run = 0
  ExctractBarPos     = [[856, 804],[845, 809],[959, 806]]
  ExctractBarColor   = [[2, 65, 92],[39, 33, 32],[126, 153, 158]]
  
  module_function
  def start
    # return extract_loots
    # return start_room3
    # return shop_sells
    @timer_run += 1
    puts "Running ##{@timer_run} time"
    Input.zoomout 0x400+rand(0x300)
    reset_dungeon; uwait(0.1);
    enter_dungeon; uwait(0.3);
    select_difficulty; wait(3);
    wait_until_transition_ok; uwait(1.5);
    
    start_room1 
    terminate if $flag_combat_dead
    reposition
    
    start_room2
    terminate if $flag_combat_dead
    reposition
    
    start_room3
    terminate if $flag_combat_dead
    reposition

    terminate
  end

  def terminate
    leave; wait 12; uwait 10;
    wait_until_transition_ok;
    3.times do |i|
      puts "#{3-i} seconds until redo the dungeon"
      wait(0.8)
    end
    # Input.trigger_key Keymap[:vk_esc],false; uwait 1;
    rotateX(200+rand(30))
    start
  end

  def reposition
    toggle_dragon; uwait 1;
    unstuck(true); extract_loots;
    wt = $timer_unstuck - Time.now.to_i
    puts "#{wt} seconds before teleport"
    wt.times{|i| wait(0.75);}
    wait_until_transition_ok; uwait 2;
    Input.zoomout 0x400+rand(0x200)
  end

  def start_room1 
    puts "Starting room#1"
    Combat.earth_shield; uwait(1);
    move_left 1.5
    move_front 1.4,true,false
    rotateX(90)
    11.times{wait(0.1); Input.trigger_key Keymap[:vk_space],false}
    rotateX(90)
    6.times{wait(0.1); Input.trigger_key Keymap[:vk_space],false}
    Input.key_up(Keymap[:vk_W],false)
    rotateX(-180)
    toggle_dragon; uwait(0.5)
    Input.trigger_key Keymap[:vk_f2]
    uwait(0.1)
    # Input.trigger_key Keymap[:vk_f1]
    Combat.engage
  end

  def start_room2 
    puts "Starting room#2"
    Combat.earth_shield; uwait 1;
    move_front 1.5,true
    Input.key_down Keymap[:vk_W],false
    toggle_dragon; uwait(0.5)
    Input.trigger_key Keymap[:vk_f2]; uwait(0.5);
    toggle_dragon; Combat.blink;
    Input.key_up Keymap[:vk_W],false; uwait(0.5);
    move_front 1.5,true;
    toggle_dragon; Combat.backjump;
    uwait(0.1)
    # Input.trigger_key Keymap[:vk_f1]
    Combat.engage
  end

  def start_room3
    puts "Start room#3"
    Combat.earth_shield; uwait 1;
    move_front 8,true; uwait 0.5;
    move_front 1.5,true
    rotateX(90); uwait 0.5;
    move_front 2.2,true
    toggle_dragon; Combat.backjump;
    Combat.engage
  end

  def leave
    puts "Leaving Dungeon"
    unstuck(true); extract_loots;
    wt = $timer_unstuck - Time.now.to_i
    puts "#{wt} seconds before teleport"
    wt.times{|i| wait(0.7);}; uwait(1.5);
    Input.trigger_key Keymap[:vk_esc],false; uwait 1;
    Input.zoomout 0x350+rand(0x200)
    if @timer_run % TimesPerClearInventory == 0
      combine_shards; uwait 1;
      Input.trigger_key Keymap[:vk_esc],false; uwait 1;
      discard_shards; uwait 1;
      Input.trigger_key Keymap[:vk_esc],false; uwait 1;
      shop_sells; uwait 1;
      puts "Inventory cleared"
    end
    move_back 1
  end
end

def start_dunar_temple
  DunarTemple.start
end