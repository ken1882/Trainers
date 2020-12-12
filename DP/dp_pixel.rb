require 'win32/api'
require 'win32con'


GetDesktopWindow = Win32::API.new('GetDesktopWindow', 'V', 'L', 'user32')
GetDeviceContext = Win32::API.new('GetDC', 'L', 'L', 'user32')
GetPixel = Win32::API.new('GetPixel', 'LLL', 'L', 'gdi32')
MoveWindow  = Win32::API.new('MoveWindow', 'LLLLLL', 'L', 'user32')

module Graphics
  ScreenHwnd = GetDesktopWindow.call()
  ScreenHDC  = GetDeviceContext.call(ScreenHwnd)
  PixelStruct = Struct.new(:r, :g, :b, :red, :green, :blue, :rgb)
  
  SWP_SHOWWINDOW = 0x40
  PixelTolerance = 0xf

  module_function
  def get_pixel(x, y)
    v = GetPixel.call(ScreenHDC, x, y)
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
    MoveWindow.call(hwnd, x, y, w, h, 1)
  end

end