module Input
  @keystate  = Array.new(0xff){0}
  @mouse_pos = [0,0]

  module_function
  def get_cursor_pos
    @mouse_pos = Win32API.GetCursorPos
  end

  def mouse_pos; @mouse_pos; end

  def update
    0xff.times do |i|
      @keystate[i] = Win32API.GetAsyncKeyState(i) ? @keystate[i] + 1 : 0
    end
    self.get_cursor_pos
  end

  def trigger?(kcode)
    @keystate[kcode] == 1
  end

  def keystate; @keystate; end

  def mouse_rdown(use_msg, apply_pos)
    if use_msg
      Win32API.SendMessage($AppHwnd, WM_RBUTTONDOWN, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_RIGHTDOWN
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      Win32API.MouseEvent(flag, mx, my, 0, 0)
    end
    $flag_pressed = true
  end

  def mouse_rup(use_msg, apply_pos)
    mx = apply_pos ? @mouse_pos[0] : 0
    my = apply_pos ? @mouse_pos[1] : 0
    if use_msg
      Win32API.SendMessage($AppHwnd, WM_RBUTTONUP, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_RIGHTUP
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      Win32API.MouseEvent(flag, mx, my, 0, 0)
    end
    $flag_pressed = false
  end

  def mouse_ldown(use_msg,apply_pos)
    if use_msg
      Win32API.SendMessage($AppHwnd, WM_LBUTTONDOWN, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_LEFTDOWN
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      Win32API.MouseEvent(flag, mx, my, 0, 0)
    end
    $flag_pressed = true
  end

  def mouse_lup(use_msg,apply_pos)
    if use_msg
      Win32API.SendMessage($AppHwnd, WM_LBUTTONUP, 0, 0)
    else
      mx = apply_pos ? (@mouse_pos[0] * 0xffff / $PrimaryScreenWidth).to_i  : 0
      my = apply_pos ? (@mouse_pos[1] * 0xffff / $PrimaryScreenHeight).to_i : 0
      flag  = MOUSEEVENTF_LEFTUP
      flag |= MOUSEEVENTF_ABSOLUTE if apply_pos
      Win32API.MouseEvent(flag, mx, my, 0, 0)
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
      Win32API.SendMessage($AppHwnd, WM_KEYDOWN, kid, 0)
    else
      Win32API.KeybdEvent(kid, 0, 0, 0)
    end
    $flag_pressed = true
  end

  def key_up(kid, use_msg=true)
    if use_msg
      Win32API.SendMessage($AppHwnd, WM_KEYUP, kid, 0)
    else
      Win32API.KeybdEvent(kid, 0, 2, 0)
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
    return Win32API.SetCursorPos(x,y) unless use_event
    x = (x * 0xffff / $PrimaryScreenWidth).to_i
    y = (y * 0xffff / $PrimaryScreenHeight).to_i
    Win32API.MouseEvent(MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_MOVE, x, y, 0, 0)
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
    Win32API.MouseEvent(MOUSEEVENTF_WHEEL, 0, 0, -n, 0)
  end

  def zoomin(n)
    Win32API.MouseEvent(MOUSEEVENTF_WHEEL, 0, 0, n, 0)
  end
end