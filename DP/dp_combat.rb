# Hardware and OS settings dependent
DegreeSpeedFactor = 7.76
def rotateX(degree, speed=20, async=false)
  dx = degree < 0 ? -speed : speed
  [(degree.abs*DegreeSpeedFactor/speed).to_i, 1].max.times do |i|
    MouseEvent.call(MOUSEEVENTF_MOVE, dx, 0, 0, 0)
    (async ? sleep(FPS) : Fiber.yield)
  end
end

def rotateY(degree, speed=20, async=false)
  dy = degree < 0 ? -speed : speed
  (degree.abs*DegreeSpeedFactor/speed).to_i.times do |i|
    MouseEvent.call(MOUSEEVENTF_MOVE, 0, dy, 0, 0)
    (async ? sleep(FPS) : Fiber.yield)
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

def move_front(duration,dash,release=true,jump=true)
  if dash
    Input.trigger_key(Keymap[:vk_W],false)
    sleep(0.1)
  end
  Input.key_down Keymap[:vk_W],false
  wait(0.3)
  if jump
    cnt = (duration / JumpDuration).to_i
    cnt.times do 
      Input.trigger_key Keymap[:vk_space] if rand > JumpChance
      wait(JumpDuration)
    end
  else
    wait(duration)
  end
  Input.key_up(Keymap[:vk_W],false) if release
end

def move_right(duration)
  cnt = (duration / JumpDuration).to_i
  Input.key_down Keymap[:vk_D],false
  cnt.times do 
    Input.trigger_key Keymap[:vk_space] if rand > JumpChance
    wait(JumpDuration)
  end
  Input.key_up Keymap[:vk_D],false
end

def move_back(duration)
  cnt = (duration / JumpDuration).to_i
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
  CombatIndicatorPos = [72, 74]

  TargetTooFarPos = [[778, 305],[848, 308],[1140, 301]]
  TargetTooFarColor = [[244, 154, 193],[244, 154, 193],[244, 154, 193]]
  NoTargetPos = [[989, 301],[666, 300],[1342, 302],[1296, 304],[1190, 310]]
  NoTargetColor = [[242, 153, 191],[242, 153, 191],[242, 153, 191],[242, 153, 191],[242, 153, 191]]
  CharacterDeadPos   = [[1029, 484],[1040, 508],[886, 506],[884, 549],[1010, 552],[1137, 610],[758, 608],[852, 368],[1233, 392]]
  CharacterDeadColor = [[2, 106, 141],[27, 27, 26],[29, 29, 27],[27, 27, 25],[25, 25, 24],[12, 12, 12],[11, 13, 12],[254, 254, 254],[187, 181, 149]]
  
  PetPagePos = [1843, 406]
  LootPetPos = [1604, 457] #[1743, 451]

  DragonHpPos   = [[103, 175]]
  DragonHpColor = [[200, 38, 2]]

  module_function
  def summon_dragon
    return if dragon_summoned?
    Input.key_down(Keymap[:vk_Lalt],false); uwait(0.1);
    Input.trigger_key(Keymap[:vk_f2],false); uwait(0.1);
    Input.key_up(Keymap[:vk_Lalt],false)
  end

  def unsummon_dragon
    return unless dragon_summoned?
    Input.key_down(Keymap[:vk_Lalt],false); uwait(0.1);
    Input.trigger_key(Keymap[:vk_f2],false); uwait(0.1);
    Input.key_up(Keymap[:vk_Lalt],false)
  end

  def dragon_summoned?
    return Graphics.screen_pixels_matched? DragonHpPos,DragonHpColor
  end

  def scan4enemy(method=0)
    return (rand()*30).to_i.times{rotateX(2)} if $flag_always_combat
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
  def clickR; Input.click_r(false,true); end;
  def cancel_skill; Input.click_r(false,true); end;
  def cd?(vk); return Time.now.to_i - (HotKeyCoolDowns[vk] || 0) < 0; end;
  def cd(vk,t); HotKeyCoolDowns[vk] = Time.now.to_i + t; end;
  def hk(vk); Input.trigger_key(vk); end;

  def in_combat?
    color = Graphics.get_pixel(*CombatIndicatorPos)
    return false if color.r < 180
    return false if color.g+color.b < 50
    return true
  end

  def netherbomb
    vk = Keymap[:vk_4]
    return if cd?(vk) 
    backjump; uwait(0.4);
    Input.zoomout 0x7ff
    hk(vk)
    rotateY 90,40; uwait(0.03);
    clickL; uwait(0.03);
    rotateY -88,40
    cd(vk, 15)
    forwardjump
    Input.zoomout 0x7ff
    rotateX 180,40
  end

  def earth_shield
    vk = :alt_E
    return if cd?(vk) 
    Input.key_down Keymap[:vk_Lalt],false; sleep(0.03);
    Input.trigger_key Keymap[:vk_E]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
    cd(vk, 18)
  end

  def elemental_activation
    vk = :alt_R
    return if cd?(vk) 
    Input.key_down Keymap[:vk_Lalt],false; sleep(0.03);
    Input.trigger_key Keymap[:vk_R]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
    cd(vk, 42)
  end

  def blink 
    vk = :alt_Q
    Input.key_down Keymap[:vk_Lalt],false; sleep(0.03);
    Input.trigger_key Keymap[:vk_Q]; uwait(0.03);
    Input.key_up Keymap[:vk_Lalt],false
  end

  def healbuff 
    vk = :alt_3
    Input.key_down Keymap[:vk_Lalt],false; sleep(0.03);
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

  def sidejump
    vk = rand(10) < 5 ? Keymap[:vk_A] : Keymap[:vk_D]
    Input.key_down vk,false
    uwait(0.1)
    Input.trigger_key Keymap[:vk_space],false
    uwait(0.1)
    Input.trigger_key Keymap[:vk_space],false
    uwait(0.4)
    Input.key_up vk,false
  end

  def target_reachable?
    # return false unless $flag_hastarget
    hk Keymap[:vk_2]; wait 0.8;
    return !(
      Graphics.screen_pixels_matched?(
      TargetTooFarPos,TargetTooFarColor) || 
      Graphics.screen_pixels_matched?(
        NoTargetPos,NoTargetColor
      )
    )
  end

  def use_skill(vk, _cd=nil)
    return if _cd && cd?(vk)
    hk(vk)
    cd(vk,_cd) if _cd
    uwait 0.7
  end

  def roll
    dir = rand(2)
    if dir == 0
      Input.key_down Keymap[:vk_D],true; uwait(0.05);
      Input.trigger_key Keymap[:vk_Lshift],false; uwait(0.05);
      Input.key_up Keymap[:vk_D],true;
      rotateX(-90,40)
    else
      Input.key_down Keymap[:vk_A],true; uwait(0.05);
      Input.trigger_key Keymap[:vk_Lshift],false; uwait(0.05);
      Input.key_up Keymap[:vk_A],true;
      rotateX(90,40)
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
    $flag_hastarget = false
    skill_stage = 0
    loop do 
      break if timer_neutralized >= 5
      if chacter_dead?
        puts "Character is gg"
        60.times do |i|
          puts "#{60-i} seconds until respawn"
          uwait 0.9
        end
        wait_until_transition_ok; uwait 2;
        revive_prepare
        break
      end
      elemental_activation
      Input.zoomout 0x3ff+rand(0x200)
      $flag_hastarget = !enemy_dead?
      if !$flag_hastarget
        cam_dx = scan4enemy
        $flag_hastarget = !cam_dx.nil?
      end
      if timer_neutralized > 3
        unsummon_dragon; uwait 0.1;
      elsif !dragon_summoned?
        summon_dragon; uwait 0.1;
      end
      can_engage = $flag_hastarget ? target_reachable? : false
      if $flag_hastarget && !can_engage
        puts "Target too far, force search next; timer: #{timer_neutralized += 0.3}"
        rotateX 30,40
        wait 0.1
        next
      elsif !$flag_hastarget && in_combat?
        puts "Untargeted enemy nearby"
        roll; uwait(0.1); blink; 
        use_skill Keymap[:vk_2]
        netherbomb;
        next
      end
      if $flag_hastarget && can_engage
        timer_neutralized = 0
        puts "Enemy detected, engaging"
        case skill_stage
        when 0
          earth_shield; uwait(0.1); skill_stage=1;
        when 1
          roll; netherbomb;
          healbuff; roll; scan4enemy;
          use_skill Keymap[:vk_V]
          use_skill Keymap[:vk_E]
          roll; scan4enemy;
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
    puts "Combat ends"
  end

  def revive_prepare
    Input.trigger_key Keymap[:vk_9]; uwait 1.5;
    Input.trigger_key Keymap[:vk_B]; uwait 1;
    Input.moveto *PetPagePos; uwait 0.3;
    clickL; uwait 0.3;
    Input.moveto *LootPetPos; uwait 0.3;
    clickR; uwait 0.3;
    $flag_combat_dead = true 
  end

  def reset_view
    rotateY(360,50); uwait 0.5;
    rotateY(-150,50)
    Input.zoomout 0xC00+rand(0x100)
  end
end