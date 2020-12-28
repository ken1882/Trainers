module Grinding
  ProfilePos = [89, 84]
  ResetDungPos = [183, 130]
  ResetFirstDungPos = [298, 139]

  HardDifficultyPos = [1072, 750]
  EnterDungPos = [1151, 835]

  HpBarPos = [155, 62]
  MpBarPos = [155, 80]
  HpBarColor = [210, 46, 4]
  MpBarColor = [10, 125, 160]

  SystemMenuPos = [1139, 30]
  UnstuckPos    = [976, 460]
  
  GearsPos = [1455, 491]
  BatchExcPos = [1752, 707]
  StartExcPos = [1360, 640]
  ItemRowPos  = [[1510, 450],[1510, 500],[1510, 550],[1510, 600],[1510, 650]]
  ItemPagePos = [[1515, 705],[1537, 703],[1557, 704],[1578, 703],[1600, 704]]
  StartExtRowN  = 0
  StartSellPage = 1
  NpageToSell   = 5
  NextPagePos   = [1618, 706]
  NextColumnDX  = 48
  
  FirstItemPos       = [[1506, 452]]
  FirstItemColor     = [[27, 27, 27]]
  ExtractBarPos = [[900,818],[960,818]]
  ExtractBarColorThreshold = 50
  LastPageToExcPos   = [[1840, 655]]
  LastPageToExcColor = [[30, 30, 28]]

  DragonShardPos = [1792, 408]
  ShardTypesPos  = [1523, 440]
  ShardTypeListPos = [[1464, 469],[1469, 496],[1470, 521],[1472, 544],[1465, 575]]
  ShardFilterPos = [[1606, 438], [1645, 441]]
  ShardDmgFilterInput = [[Keymap[:vk_3],Keymap[:vk_5]],[Keymap[:vk_4], Keymap[:vk_0]]]
  ShardDefFilterInput = [[Keymap[:vk_9],Keymap[:vk_5]],[Keymap[:vk_1], Keymap[:vk_0], Keymap[:vk_0]]]
  ShardDmg302FilterInput = [ [Keymap[:vk_6],Keymap[:vk_0]],[Keymap[:vk_6],Keymap[:vk_5]] ]
  ShardDef302FilterInput = [ [Keymap[:vk_1],Keymap[:vk_5],Keymap[:vk_0]],[Keymap[:vk_1],Keymap[:vk_6],Keymap[:vk_0]] ]
  TenthShardPos   = [[1555, 557]]
  TenthShardColor = [[23, 23, 21]]
  ItemShardsPos   = [[1507, 506],[1553, 506],[1601, 503],[1648, 503],[1695, 505],[1745, 505],[1795, 505],[1841, 503],[1506, 553],[1557, 555]]
  CombineShardPos = [147, 724]
  AttunedShardPos = [232, 413]
  ShardCombineOkPos = [910, 312]
  ShardTypeListScollPos = [[1573, 495],[1575, 531]]
  ShardScrolldownPos = [1573, 574]

  TrashBinPos = [1847, 705]
  DeleteTrashPos = [1357, 639]
  DeleteTrashOkPos = [911, 312]
  ColorNoItem = [30,30,30]

  RepairShopPos = [524, 786]
  RepairGearsPos = [655, 522]
  StartRepairPos = [877,517]
  
  JBBuffs = [[242, 571],[243, 536],[245, 493],[252, 464],[254, 426],[261, 389],[263, 359],[256, 326]]
  HudOpenedPos = [[10,5],[1900,5]]
  HudPixelSampleRate = 100
  HudOpenedColorAvg = 30
  CharSelectionPos = [971, 525]
  module_function

  # reset position and camera
  def unstuck(async=false)
    puts "Unstucking"
	while !hud_opened?
	  Input.trigger_key Keymap[:vk_esc],false; uwait(0.5);
	end  
    Input.moveto(*SystemMenuPos); uwait(0.1);
    Input.click_l false,true; uwait(0.3);
    Input.moveto(*UnstuckPos); uwait(0.1);
    Input.click_l false,true
    if !async 
      60.times do |i|
        puts "Teleport countdown: #{60-i}"
        wait(0.9)
      end
      puts "Teleported"
    else 
      puts "Teleport after 60 seconds"
      $timer_unstuck = Time.now.to_i+60
    end
	Input.zoomout 0x600+rand(0x200)
  end

  def extract_loots
    puts "Start extracing loots"
    Input.trigger_key Keymap[:vk_B]; uwait(0.3);
	2.times do 
      Input.moveto *GearsPos; uwait(0.3);
      Input.click_l false, true; uwait(0.3);
      Input.moveto *BatchExcPos; uwait(0.3);
      Input.click_l false, true; uwait(0.3);
    end
    return puts("Nothing to extract!") if 3.times.collect{
      uwait(0.1); 
      px,py = FirstItemPos[0]
      _pos = 9.times.collect{|i| [px+(i%3-1),py+(i/3)-1] }
      Graphics.screen_pixels_matched?(
        _pos, FirstItemColor*9
      )
    }.all?
    
    mx, my = *ItemRowPos[StartExtRowN]
    _ExtractProc = Proc.new{
      for i in (StartExtRowN...[StartExtRowN+3,ItemRowPos.size].min)
        mx, my = *ItemRowPos[i]
        8.times do 
          Input.moveto mx-rand(10), my+rand(10)-5
          Input.click_r false,true; uwait(0.03);
          mx += NextColumnDX
          Input.click_r false,true
        end
      end
    }
	_exterrcnt = 0
    _EnsureExtractingProc = Proc.new{
      loop do 
        _flag_exc_started = true 
        60.times do 
          _flag_exc_started = true 
          sy = ExtractBarPos[0][1]
          ExtractBarPos[0][0].upto ExtractBarPos[1][0] do |sx|
            rgb = Graphics.get_pixel(sx,sy).rgb
            if rgb.any?{|cv| cv > ExtractBarColorThreshold}
              _flag_exc_started = false; break;
            end
          end
          Fiber.yield
          break if _flag_exc_started        
        end
        puts "Extracting status: #{_flag_exc_started}"
        break if _flag_exc_started
        if Graphics.screen_pixels_matched? LastPageToExcPos, LastPageToExcColor
          puts "Seems nothing to extract"
          break
        elsif _exterrcnt > 5
          puts "Seems something went wrong, retry extracing process"
          Combat.earth_shield; uwait 3;
          return extract_loots
        end
        Input.moveto *StartExcPos; uwait(0.3)
        Input.click_l false,true
        puts "Extract seems not started, retry (#{_exterrcnt})"
		    _exterrcnt += 1
      end
    }
    _ExtractProc.call; Input.moveto *StartExcPos;
    uwait(0.3); Input.click_l false,true; uwait(0.3);
    puts "Extract started"
    loop do 
      _ExtractProc.call;
      Input.moveto *GearsPos; uwait(0.5);
      _EnsureExtractingProc.call
      break if 3.times.collect{
                  uwait(0.2); Graphics.screen_pixels_matched?(
                    LastPageToExcPos, LastPageToExcColor
                  )
                }.all?
      puts "Waiting for next page of loots"
      uwait(3)
    end
    puts "Last page of loots, after 10 seconds ending"
    uwait(2)
    _ExtractProc.call
    uwait(8)
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

  def reset_dungeon 
    while !hud_opened?
      Input.trigger_key(Keymap[:vk_esc]); uwait 0.3;
	end
    Input.moveto(*ProfilePos); wait((rand/2).floor(2));
    Input.click_r(false,true); wait((rand/2).floor(2));
    Input.moveto(*ResetDungPos); wait(0.1+(rand/5).floor(2));
    Input.moveto(*ResetFirstDungPos);  wait(0.1+(rand/5).floor(2));
    Input.click_l(false,true)
  end

  def enter_dungeon
    method = rand(3)
    if method == 0
      Input.key_down(Keymap[:vk_Lalt],false); wait((rand/2).floor(2));
      Input.trigger_key(Keymap[:vk_Q],false); wait(0.2+(rand/2).floor(2));
      Input.trigger_key(Keymap[:vk_Q],false); wait(0.1);
      Input.key_up(Keymap[:vk_Lalt],false)
    else
      move_front(0.5,method>1)
    end
	uwait 1
	logout unless hud_opened?
  end

  def select_difficulty
    mx, my = HardDifficultyPos; mx+=rand(20)-10; my+=rand(20)-10;
    Input.moveto(mx,my); wait(0.1+(rand/5).floor(2));
    Input.click_l(false,true);
    mx, my = EnterDungPos; mx+=rand(20)-10; my+=rand(20)-10;
    Input.moveto(mx,my); wait(0.1+(rand/5).floor(2));
    Input.click_l(false,true);
  end

  def combine_shards(combine_302=false)
    puts "Start combine dragon shards"
	Input.key_down Keymap[:vk_Lcontrol],false; uwait 0.5;
    Input.trigger_key Keymap[:vk_equal]; uwait 0.5;
    Input.key_up Keymap[:vk_Lcontrol],false; uwait(2.5);
    Input.moveto(*ShardTypesPos); uwait 0.3;  Input.click_l false,true;
    Input.moveto(*ShardTypeListPos[1]); uwait 0.3;  Input.click_l false,true;
	# filter to only 198 damage shards
	2.times do |i|
	  Input.moveto(*ShardFilterPos[i]); uwait 0.3;
	  Input.click_l false,true; uwait 0.3
      ShardDmgFilterInput[i].each{|vk| Input.trigger_key vk,false}
	  uwait 0.3
	end
    _CombineShardsProc = Proc.new{
      loop do 
        uwait(1)
        break if Graphics.screen_pixels_matched? TenthShardPos,TenthShardColor
        ItemShardsPos.each do |pos|
          mx, my = pos 
          Input.moveto(mx+rand(20)-10,my+rand(20)-10); uwait 0.1;
          Input.click_r false,true; uwait 0.1;
        end
        Input.moveto(*CombineShardPos,50); uwait 0.3; 
        Input.click_l false,true;
        Input.moveto(*ShardCombineOkPos,50); uwait 0.3;
        Input.click_l false,true;
        Input.moveto(*AttunedShardPos,50); uwait 0.5;
        2.times{ Input.click_r false,true; uwait 0.3; }
        Input.moveto(*DragonShardPos,50)
      end
    }
    _CombineShardsProc.call 
    [ShardTypeListPos[2],ShardTypeListPos[3],ShardTypeListPos[4]].each do |spos|
      Input.moveto(*ShardTypesPos); uwait 0.3; Input.click_l false,true;
      Input.moveto(*spos); uwait 0.3; Input.click_l false,true;
      _CombineShardsProc.call()
    end

    # Scroll down and select/combine dsd shards
    Input.moveto(*ShardTypesPos); uwait 0.3; Input.click_l false,true;
    Input.moveto *ShardTypeListScollPos[0]; uwait 0.3;
    Input.mouse_ldown false,true; uwait 0.3;
    Input.moveto *ShardTypeListScollPos[1]; uwait 0.3;
    Input.mouse_lup false,true; uwait 0.3;
    Input.moveto(*ShardTypeListPos[0]); uwait 0.3;  Input.click_l false,true;
    _CombineShardsProc.call()
    uwait 0.5

    # Combine Phy/MagDef shards
    Input.moveto(*ShardTypesPos); uwait 0.3; Input.click_l false,true;
    Input.moveto(*ShardTypeListPos[1]); uwait 0.3;  Input.click_l false,true;
    2.times do |i| 
	  Input.moveto(*ShardFilterPos[i]); uwait 0.3;  Input.click_l false,true;
      uwait 0.3
      2.times do 
        Input.trigger_key Keymap[:vk_backspace],false; uwait 0.3; 
        Input.trigger_key Keymap[:vk_delete],false; uwait 0.3;
      end
      ShardDefFilterInput[i].each{|vk| Input.trigger_key vk,false}
	  uwait 0.3
	end
	[ShardTypeListPos[1],ShardTypeListPos[2]].each do |tpos|
		Input.moveto(*ShardTypesPos); uwait 0.3; Input.click_l false,true;
		Input.moveto(*tpos); uwait 0.3;  Input.click_l false,true;
		uwait 0.3; _CombineShardsProc.call;
		Input.moveto *DragonShardPos; uwait 0.3;
		Input.click_l false,true; uwait 0.5;
	end 
    
    return unless combine_302
    Input.trigger_key Keymap[:vk_B]; uwait 0.5;
    Input.trigger_key Keymap[:vk_B]; uwait 1.5;
    Input.moveto *DragonShardPos; uwait 0.5;
    Input.click_l false,true; uwait 0.3;
    Input.moveto *ShardTypesPos; uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    Input.moveto *ShardTypeListPos[2]; uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    
    Input.moveto *ShardFilterPos[0]; uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    ShardDmg302FilterInput[0].each do |vk|
      Input.trigger_key vk,false; uwait 0.1;
    end
    Input.moveto *ShardFilterPos[1]; uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    ShardDmg302FilterInput[1].each do |vk|
      Input.trigger_key vk,false; uwait 0.1;
    end

    Input.moveto *DragonShardPos; uwait 0.5;
    Input.click_l false,true; uwait 0.3;
	# combine mdmg,edmg,ndmg
    [ShardTypeListPos[2],ShardTypeListPos[3],ShardTypeListPos[4]].each do |spos|
      Input.moveto(*ShardTypesPos); uwait 0.3; Input.click_l false,true;
      Input.moveto(*spos); uwait 0.3; Input.click_l false,true;
      _CombineShardsProc.call()
    end
	# combine phy/magdef
	Input.moveto *ShardTypesPos; uwait(0.3);
    Input.click_l false, true; uwait(0.3);
    Input.moveto *ShardScrolldownPos; uwait 0.3;
    3.times{ Input.click_l false, true; uwait(0.2); }
	Input.moveto *ShardTypeListPos[4]; uwait 0.3;
	Input.click_l false, true; uwait(0.3);
	2.times do |i| 
	  Input.moveto(*ShardFilterPos[i]); uwait 0.3;  Input.click_l false,true;
      uwait 0.3
      2.times do 
        Input.trigger_key Keymap[:vk_backspace],false; uwait 0.3; 
        Input.trigger_key Keymap[:vk_delete],false; uwait 0.3;
      end
      ShardDef302FilterInput[i].each{|vk| Input.trigger_key vk,false}
	  uwait 0.3
	end
	[ShardTypeListPos[3],ShardTypeListPos[4]].each do |tpos|
		Input.moveto(*ShardTypesPos); uwait 0.3; Input.click_l false,true;
		Input.moveto(*tpos); uwait 0.3;  Input.click_l false,true;
		uwait 0.3; _CombineShardsProc.call;
		Input.moveto *DragonShardPos; uwait 0.3;
		Input.click_l false,true; uwait 0.5;
	end 
    uwait 0.3; _CombineShardsProc.call;
	Input.moveto *DragonShardPos; uwait 0.3;
    Input.click_l false,true; uwait 0.5;
  end

  def discard_shards
    puts "Start discard useless shards"
    while !hud_opened?
	  Input.trigger_key Keymap[:vk_B]; uwait(2.5);
	end
    Input.moveto *DragonShardPos; uwait(0.3);
    Input.click_l false, true; uwait(0.3);
    Input.moveto *ShardTypesPos; uwait(0.3);
    Input.click_l false, true; uwait(0.3);

    Input.moveto *ShardScrolldownPos; uwait 0.3;
    6.times{ Input.click_l false, true; uwait(0.2); }
    Input.moveto *ShardTypeListPos[0]; uwait 0.3;
    Input.click_l false, true; uwait(0.3);
    Input.moveto *TrashBinPos; uwait 0.3;
    Input.click_l false, true; uwait(0.3);
    _SellShardProc = Proc.new{
      loop do 
        uwait(1)
        break if Graphics.screen_pixels_matched? TenthShardPos,TenthShardColor
        ItemShardsPos.each do |pos|
          mx, my = pos 
          Input.moveto(mx+rand(20)-10,my+rand(20)-10); uwait 0.1;
          Input.click_r false,true; uwait 0.1;
        end
        Input.moveto(*DeleteTrashPos); uwait 0.3; 
        Input.click_l false,true;
        Input.moveto(*DeleteTrashOkPos); uwait 0.3;
        Input.click_l false,true;
        Input.moveto(*DragonShardPos,30+rand(20))
      end
    }
    # delete pdef
    _SellShardProc.call; uwait 0.3;

    # delete nres,eres,dres
    [ShardTypeListPos[2],ShardTypeListPos[3],ShardTypeListPos[4]].each do |spos|
      Input.moveto *ShardTypesPos; uwait(0.3);
      Input.click_l false, true; uwait(0.3);
      Input.moveto *spos; uwait 0.3;
      Input.click_l false, true; uwait(0.3);
      _SellShardProc.call; uwait 0.3;
    end
    # delete hp
    Input.moveto *ShardTypesPos; uwait 0.3;
    Input.click_l false, true; uwait 0.2;
    Input.moveto *ShardScrolldownPos; uwait 0.3;
    Input.click_l false, true; uwait 0.2;
    Input.moveto *ShardTypeListPos[4]; uwait 0.3;
    Input.click_l false, true; uwait(0.3);
    _SellShardProc.call; uwait 0.3;
  end

  def shop_sells
	while !hud_opened?
      Input.key_down Keymap[:vk_Lcontrol],false; uwait 0.5;
      Input.trigger_key Keymap[:vk_minus]; uwait 0.5;
      Input.key_up Keymap[:vk_Lcontrol],false; uwait(1);
      uwait 3; Input.trigger_key Keymap[:vk_F],false; uwait 2.5;
	end
    Input.moveto 1,1; uwait 0.1;
    Input.moveto *ItemPagePos[StartSellPage]; uwait 0.3;
    Input.click_l false, true; uwait(0.3);
    NpageToSell.times do |i|
      _sellpos = []
      puts "Selling page##{1+i+StartSellPage}"
      ItemRowPos.each do |rpos|
        mx, my = rpos 
        8.times do
          _pos = 9.times.collect{|i| [mx+(i%3-1),my+(i/3)-1] }
          if !(_pos.collect{ |p| 
                Graphics.screen_pixels_matched?([p], [ColorNoItem])
              }
            ).all?
            _sellpos << [mx,my]
          end
          mx += NextColumnDX
        end
      end
      puts "Item pos: #{_sellpos}"
      _sellpos.each do |pos| 
        Input.moveto *pos; uwait 0.1;
        Input.click_r false, true; uwait(0.3);
      end
      Input.moveto *NextPagePos; uwait 0.1;
      Input.click_l false, true; uwait(0.3);
    end
    # repair item
    Input.moveto *RepairShopPos; uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    Input.moveto *RepairGearsPos; uwait 0.3;
    Input.click_l false,true; uwait 0.3;
    Input.moveto *StartRepairPos; uwait 0.3;
    Input.click_l false,true; uwait 5;
  end
  
  def get_jb_buff
	Input.trigger_key Keymap[:vk_F],false; uwait 1;
	return logout unless hud_opened?
	JBBuffs.each do |pos|
	  Input.trigger_key Keymap[:vk_F],false; uwait 1;
	  Input.moveto *pos; uwait 0.5;
	  Input.click_l false, true; uwait 0.3;
	end
  end
  
  def hud_opened?
    uwait 1
	sum = 0
	sx,sy = HudOpenedPos[0]
	ex = HudOpenedPos[1].first
	_cnt = ((ex-sx) / HudPixelSampleRate).to_i
	_cnt.times do |i|
	  rgb = Graphics.get_pixel(sx+i*HudPixelSampleRate,sy).rgb
	  sum += (rgb.sum / 3)
	end 
	return (sum / _cnt) <= HudOpenedColorAvg
  end
  
  def logout
	puts "Logout!"
	while !hud_opened?
	  Input.trigger_key Keymap[:vk_esc],false
	  uwait 1.5
	end
	Input.moveto *SystemMenuPos; uwait 0.3;
	Input.click_l false,true; uwait 0.3;
	Input.moveto *CharSelectionPos; uwait 0.3;
	Input.click_l false,true; uwait 0.3;
	exit
  end
end