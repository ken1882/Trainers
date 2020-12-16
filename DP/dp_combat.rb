# Hardware and OS settings dependent
DegreeSpeedFactor = 7.76
def rotateX(degree)
  dx = degree < 0 ? -1 : 1
  (degree.abs*DegreeSpeedFactor).to_i.times do |i|
    MouseEvent.call(MOUSEEVENTF_MOVE, dx, 0, 0, 0)
    Fiber.yield
  end
end

def rotateY(degree)
  dy = degree < 0 ? -1 : 1
  (degree.abs*DegreeSpeedFactor).to_i.times do |i|
    MouseEvent.call(MOUSEEVENTF_MOVE, 0, dy, 0, 0)
    Fiber.yield
  end
end

JumpDuration = 0.1
JumpChance   = 0.2

def move_left(duration)
  cnt = (duration / JumpDuration).to_i
  Input.key_down Keymap[:vk_A],false
  cnt.times do 
    Input.trigger_key Keymap[:vk_space] if rand > JumpChance
    wait(JumpDuration)
  end
  Input.key_up Keymap[:vk_A],false
end

def move_front(duration,dash,release=true)
  cnt = (duration / JumpDuration).to_i
  duration *= JumpDuration
  (Input.trigger_key(Keymap[:vk_W],false); wait(0.1);) if dash
  Input.key_down Keymap[:vk_W],false
  wait(0.3)
  cnt.times do 
    Input.trigger_key Keymap[:vk_space] if rand > JumpChance
    wait(JumpDuration)
  end
  Input.key_up(Keymap[:vk_W],false) if release
end

def move_right(duration)
  cnt = (duration / JumpDuration).to_i
  duration *= JumpDuration
  Input.key_down Keymap[:vk_D],false
  cnt.times do 
    Input.trigger_key Keymap[:vk_space] if rand > JumpChance
    wait(JumpDuration)
  end
  Input.key_up Keymap[:vk_D],false
end

def move_back(duration)
  cnt = (duration / JumpDuration).to_i
  duration *= JumpDuration
  Input.key_down Keymap[:vk_S],false
  cnt.times do 
    Input.trigger_key Keymap[:vk_space] if rand > JumpChance
    wait(JumpDuration)
  end
  Input.key_up Keymap[:vk_S],false
end

module Combat 

  HpBarPos = [155, 62]
  MpBarPos = [155, 80]
  HpBarColor = [210, 46, 4]
  MpBarColor = [10, 125, 160]

  EnemyBarPos   = [[1789, 63], [1715, 127], [1785, 81]]
  EnemyBarColor = [[190, 49, 1], [239, 239, 239], [7, 110, 142]]
  CombatIndicatorPos = [[72, 66]]
  CombatIndicatorColor = [[20, 18, 16]]

  TargetTooFarPos = [[778, 306],[848, 305],[882, 304],[1034, 313],[1086, 306],[1140, 302]]
  TargetTooFarColor = [[244, 154, 193],[244, 154, 193],[244, 154, 193],[244, 154, 193],[244, 154, 193],[244, 154, 193]]

  CharacterDeadPos   = [[1029, 484],[1040, 508],[886, 506],[884, 549],[1010, 552],[1137, 610],[758, 608],[852, 368],[1233, 392]]
  CharacterDeadColor = [[2, 106, 141],[27, 27, 26],[29, 29, 27],[27, 27, 25],[25, 25, 24],[12, 12, 12],[11, 13, 12],[254, 254, 254],[187, 181, 149]]

  module_function
  def scan4enemy(method=0)
    if method == 0
      180.times do |i|
        rotateX(2)
        return (i << 1) if !enemy_dead?
      end
    elsif method == 1
      backjump; wait(0.1);
      return 1 unless enemy_dead?
      forwardjump; wait(0.1);
      return 1 unless enemy_dead?
    end
    return nil
  end

  def enemy_dead?
    return !(Graphics.screen_pixels_matched? EnemyBarPos, EnemyBarColor)
  end

  def chacter_dead?
    return Graphics.screen_pixels_matched? CharacterDeadPos,CharacterDeadColor
  end

  HotKeyCoolDowns = {}
  def clickL; Input.click_l(false,true); end;
  def clickR; Input.click_l(false,true); end;
  def cancel_skill; Input.click_r(false,true); end;
  def cd?(vk); return Time.now.to_i - (HotKeyCoolDowns[vk] || 0) < 0; end;
  def cd(vk,t); HotKeyCoolDowns[vk] = Time.now.to_i + t; end;
  def hk(vk); Input.trigger_key(vk); end;

  def in_combat?
    return !(Graphics.screen_pixels_matched? CombatIndicatorPos, CombatIndicatorColor)
  end

  def netherbomb
    vk = Keymap[:vk_4]
    return if cd?(vk) 
    backjump
    Input.zoomout 0x7ff
    hk(vk)
    rotateY 90; uwait(0.2);
    clickL; uwait(0.1);
    rotateY -90
    cd(vk, 15)
    forwardjump
    Input.zoomout 0x7ff
    rotateX 180
  end

  def earth_shield
    vk = :alt_E
    return if cd?(vk) 
    Input.key_down Keymap[:vk_Lalt],false; Fiber.yield;
    Input.trigger_key Keymap[:vk_E]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
    cd(vk, 18)
  end

  def elemental_activation
    vk = :alt_R
    return if cd?(vk) 
    Input.key_down Keymap[:vk_Lalt],false; Fiber.yield;
    Input.trigger_key Keymap[:vk_R]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
    cd(vk, 42)
  end

  def blink 
    vk = :alt_Q
    Input.key_down Keymap[:vk_Lalt],false; Fiber.yield;
    Input.trigger_key Keymap[:vk_Q]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
  end

  def healbuff 
    vk = :alt_3
    Input.key_down Keymap[:vk_Lalt],false; Fiber.yield;
    Input.trigger_key Keymap[:vk_3]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
    cd(vk, 6)
  end

  def truely_battle?
    return $flag_hastarget && in_combat?
  end

  def forwardjump
    Input.key_down Keymap[:vk_W],false
    uwait(0.1)
    Input.trigger_key Keymap[:vk_space],false
    uwait(0.1)
    Input.trigger_key Keymap[:vk_space],false
    uwait(0.5)
    Input.key_up Keymap[:vk_W],false
  end

  def backjump
    Input.key_down Keymap[:vk_S],false
    uwait(0.1)
    Input.trigger_key Keymap[:vk_space],false
    uwait(0.1)
    Input.trigger_key Keymap[:vk_space],false
    uwait(0.5)
    Input.key_up Keymap[:vk_S],false
  end

  def target_reachable?
    # return false unless $flag_hastarget
    use_skill Keymap[:vk_2]
    roll
    wait(0.5)
    return !Graphics.screen_pixels_matched?(TargetTooFarPos,TargetTooFarColor)
  end

  def use_skill(vk, _cd=nil)
    return if _cd && cd?(vk)
    hk(vk)
    cd(vk,_cd) if _cd
    uwait 0.5
  end

  def roll
    dir = rand(2)
    if dir == 0
      Input.key_down Keymap[:vk_D],true; uwait(0.05);
      Input.trigger_key Keymap[:vk_Lshift],false; uwait(0.05);
      Input.key_up Keymap[:vk_D],true;
      rotateX(-90)
    else
      Input.key_down Keymap[:vk_A],true; uwait(0.05);
      Input.trigger_key Keymap[:vk_Lshift],false; uwait(0.05);
      Input.key_up Keymap[:vk_A],true;
      rotateX(90)
    end
    Input.zoomout 0x400+rand(0x200)
  end

  def wait_until_transition_ok
    loop do
      break if Graphics.screen_pixels_matched?(
        [HpBarPos, MpBarPos], [HpBarColor, MpBarColor]        
      )
      puts "Waiting for loading complete..."
      wait(1)
    end
    puts "Loading completed"
  end

  def engage
    timer_neutralized = 0
    camera_dx = 0
    $flag_hastarget = false
    skill_stage = 0
    loop do 
      break if timer_neutralized >= 5
      if chacter_dead?
        puts "Character is gg"
        60.times do |i|
          puts "#{60-i} seconds until respawn"
          uwait 0.75
        end
        wait_until_transition_ok; uwait 2;
        Input.trigger_key Keymap[:vk_9]
        $flag_combat_dead = true 
        break
      end
      elemental_activation
      Input.zoomout 0x3ff+rand(0x200)
      $flag_hastarget = !enemy_dead?
      if !$flag_hastarget
        cam_dx = scan4enemy
        $flag_hastarget = !cam_dx.nil?
        camera_dx += cam_dx if cam_dx
      end
      can_engage = $flag_hastarget ? target_reachable? : false
      if $flag_hastarget && !can_engage
        puts "Target too far, force search next; timer: #{timer_neutralized += 1}"
        rotateX 30
        wait 0.1
        next
      elsif !$flag_hastarget && in_combat?
        puts "Untargeted enemy nearby"
        roll; uwait(0.1); blink; 
        next
      end
      if $flag_hastarget && can_engage
        timer_neutralized = 0
        puts "Enemy detected, engaging"
        case skill_stage
        when 0
          earth_shield; uwait(0.1); skill_stage=1;
        when 1
          roll; netherbomb; roll; 
          healbuff; skill_stage=2;
        when 2
          use_skill Keymap[:vk_V]
          use_skill Keymap[:vk_E]
          roll; skill_stage=3;
        when 3
          use_skill Keymap[:vk_R]
          use_skill Keymap[:vk_Q]
          use_skill Keymap[:vk_3],15
          roll; skill_stage=4;
        when 4
          use_skill Keymap[:vk_1]
          use_skill Keymap[:vk_1]
          skill_stage=0; healbuff;
        end
      else
        puts "No enemy attackable"
        $flag_hastarget = false
      end
      # check combat over
      if !truely_battle?
        puts "Not in really combat, timer: #{timer_neutralized += 1}"
      end
      Fiber.yield
    end
    puts "Combat ends, camera rotateX: #{camera_dx}"
    return camera_dx
  end
end