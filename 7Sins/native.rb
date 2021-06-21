class Rect
  attr_accessor :width, :height, :x, :y
  def initialize(*args)
    @x = 0
    @y = 0
    @width  = 1
    @height = 1
    case args.length
    when 1; copy_rect(args[0]);
    when 2
      @x = args[0]
      @y = args[1]
    when 4
      @x = args[0]
      @y = args[1]
      @width  = args[2]
      @height = args[3]
    end
  end

  def copy_rect(rect)
    @x = rect.x
    @y = rect.y
    @width  = rect.width
    @height = rect.height
  end

  def to_winrect
    return [@x, @y, @x+@width, @y+height]
  end
end