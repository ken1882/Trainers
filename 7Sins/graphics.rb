require 'win32/api'
require 'win32con'

AppCanvasPos = [2, 42]

module Graphics
  PixelStruct    = Struct.new(:r, :g, :b, :red, :green, :blue, :rgb)
  ScreenHwnd     = Win32API.GetDesktopWindow
  ScreenHDC      = Win32API.GetDeviceContext(ScreenHwnd)
  PixelTolerance = 0x10
  
  module_function
  def init
    $AppRect = Rect.new
  end

  def get_pixel(x, y)
    v = Win32API.GetPixel(ScreenHDC, x, y)
    r = (v & 0x000000FF)
    g = (v & 0x0000FF00) >> 8
    b = (v & 0x00FF0000) >> 16
    return PixelStruct.new(r,g,b,r,g,b,[r,g,b])
  end

  def screen_pixels_matched?(coords, pixels)
    coords.each_with_index do |pos, i|
      p = get_pixel(pos.first, pos.last)
      # puts "#{pos} #{p.rgb}"
      return false if (p.rgb.sum - pixels[i].sum).abs > PixelTolerance
    end
    return true
  end

  def move_window(hwnd, x, y, w, h)
    Win32API.MoveWindow(hwnd, x, y, w, h)
  end

end