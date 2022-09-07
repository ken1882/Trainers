require 'win32/api'
require 'win32con'
require 'win32con/keymap'
include Win32CON
require 'windows/unicode'
include Windows::Unicode

$APP_Hwnd = 0 unless $APP_HWND

SendMessage = Win32::API.new('SendMessage', 'LLLL', 'L', 'user32')
GetAsyncKeyState = Win32::API.new('GetAsyncKeyState', 'L', 'L', 'user32')
GetCursorPos = Win32::API.new('GetCursorPos', 'P', 'V', 'user32')
SetCursorPos = Win32::API.new('SetCursorPos', 'LL', 'V', 'user32')
MouseEvent = Win32::API.new('mouse_event', "LLLLL", 'V', 'user32')
KeybdEvent = Win32::API.new('keybd_event', 'LLLP', 'V', 'user32')
GetSystemMetrics = Win32::API.new('GetSystemMetrics', 'L', 'L', 'user32')

$PrimaryScreenWidth  = GetSystemMetrics.call(SM_CXSCREEN)
$PrimaryScreenHeight = GetSystemMetrics.call(SM_CYSCREEN)

module Input
  DowncaseKeymap = {
    '*'   => 0x6A, # numpad multiply
    '+'   => 0x6B, # numpad plus
    '\\'  => Keymap[:vk_backslash],
    '-'   => Keymap[:vk_minus],
    '.'   => Keymap[:vk_period],
    '/'   => Keymap[:vk_slash],
    '`'   => Keymap[:vk_tilde],
    '['   => Keymap[:vk_leftbrace],
    ']'   => Keymap[:vk_rightbrace],
    '\''  => Keymap[:vk_quote],
    '='   => Keymap[:vk_equal],
    ';'   => Keymap[:vk_colon],
    ','   => Keymap[:vk_comma],
    "\n"  => Keymap[:vk_enter],
    "\t"  => Keymap[:vk_tab],
    "\b"  => Keymap[:vk_backspace]
  }
  UpcaseKeymap = {
    '~' =>  Keymap[:vk_tilde],
    '!' =>  Keymap[:vk_1],
    '@' =>  Keymap[:vk_2],
    '#' =>  Keymap[:vk_3],
    '$' =>  Keymap[:vk_4],
    '%' =>  Keymap[:vk_5],
    '^' =>  Keymap[:vk_6],
    '&' =>  Keymap[:vk_7],
    '*' =>  Keymap[:vk_8],
    '(' =>  Keymap[:vk_9],
    ')' =>  Keymap[:vk_0],
    '_' =>  Keymap[:vk_minus],
    '{' =>  Keymap[:vk_leftbrace],
    '}' =>  Keymap[:vk_rightbrace],
    '|' =>  Keymap[:vk_backslash],
    ':' =>  Keymap[:vk_colon],
    '"' =>  Keymap[:vk_quote],
    '<' =>  Keymap[:vk_comma],
    '>' =>  Keymap[:vk_period],
    '?' =>  Keymap[:vk_slash],
  }
  10.times{|i| DowncaseKeymap[i.to_s]     = i.to_s.ord}
  26.times{|i| UpcaseKeymap[(65+i).chr]   = 65+i }
  26.times{|i| DowncaseKeymap[(97+i).chr] = 65+i }

  @keystate  = Array.new(0xff){0}
  @mouse_pos = [0,0]

  module_function
  def mouse_pos; @mouse_pos; end

  def update
    0xff.times do |i|
      @keystate[i] = (GetAsyncKeyState.call(i) & 0x8000) > 0 ? @keystate[i] + 1 : 0
    end
    pos = [0, 0].pack("LL"); GetCursorPos.call(pos);
    @mouse_pos = pos.unpack("LL")
  end

  def trigger?(kcode)
    @keystate[kcode] == 1
  end

  def keystate; @keystate; end

  def mouse_rdown(use_msg, apply_pos)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_RBUTTONDOWN, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_RIGHTDOWN
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = true
  end

  def mouse_rup(use_msg, apply_pos)
    mx = apply_pos ? @mouse_pos[0] : 0
    my = apply_pos ? @mouse_pos[1] : 0
    if use_msg
      SendMessage.call($APP_Hwnd, WM_RBUTTONUP, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_RIGHTUP
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = false
  end

  def mouse_ldown(use_msg,apply_pos)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_LBUTTONDOWN, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_LEFTDOWN
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = true
  end

  def mouse_lup(use_msg,apply_pos)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_LBUTTONUP, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_LEFTUP
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      MouseEvent.call(flag, mx, my, 0, 0)
    end
    $flag_pressed = false
  end

  def click_l(use_msg,apply_pos)
    mouse_ldown(use_msg,apply_pos)
    sleep(0.03)
    mouse_lup(use_msg,apply_pos)
  end

  def click_r(use_msg,apply_pos)
    mouse_rdown(use_msg,apply_pos)
    sleep(0.03)
    mouse_rup(use_msg,apply_pos)
  end

  def key_down(kid, use_msg=true)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_KEYDOWN, kid, 0)
    else
      KeybdEvent.call(kid, 0, 0, 0)
    end
    $flag_pressed = true
  end

  def key_up(kid, use_msg=true)
    if use_msg
      SendMessage.call($APP_Hwnd, WM_KEYUP, kid, 0)
    else
      KeybdEvent.call(kid, 0, 2, 0)
    end
    $flag_pressed = false
  end

  def trigger_key(kid, use_msg=true)
    key_down(kid, use_msg)
    sleep(0.05)
    key_up(kid, use_msg)
  end

  def set_cursor(x,y,use_event=false)
    @mouse_pos = [x,y]
    return SetCursorPos.call(x,y) unless use_event
    x = (x * 0xffff / $PrimaryScreenWidth).to_i
    y = (y * 0xffff / $PrimaryScreenHeight).to_i
    MouseEvent.call(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, x, y, 0, 0)
  end

  def moveto(x,y,speed=nil)
    _MaxSteps = 42
    cx,cy = @mouse_pos
    dx = x - cx; dy = y - cy;
    if speed.nil?
      default_speed = 10
      cnt = (Math.hypot(dx,dy) / default_speed).to_i
      if cnt > _MaxSteps
        speed = (Math.hypot(dx,dy) / _MaxSteps).to_i
        cnt   = _MaxSteps
      else
        speed = default_speed
      end
    else
      cnt = (Math.hypot(dx,dy) / speed).to_i
    end
    angle = Math.atan2(dy, dx)
    dx = speed * Math.cos(angle)
    dy = speed * Math.sin(angle)
    cnt.times do 
      cx += dx; cy += dy; self.set_cursor(cx, cy, true)
      Fiber.yield rescue nil
    end
    self.set_cursor(x, y, false); self.set_cursor(x, y, true);
  end
  
  def zoomout(n)
    MouseEvent.call(MOUSEEVENTF_WHEEL, 0, 0, -n, 0)
  end

  def zoomin(n)
    MouseEvent.call(MOUSEEVENTF_WHEEL, 0, 0, n, 0)
  end

  def type_string(ss, use_msg=false)
    ss.each_char do |ch|
      self.type_char(ch, use_msg)
    end
  end

  
  def type_char(ch, use_msg=false)
    return self.trigger_key(DowncaseKeymap[ch], use_msg) if DowncaseKeymap[ch]
    if UpcaseKeymap[ch]
      self.key_down Keymap[:vk_Lshift],use_msg; sleep 0.03;
      self.trigger_key UpcaseKeymap[ch],use_msg;
      self.key_up Keymap[:vk_Lshift],use_msg; sleep 0.03;
    end
  end
end