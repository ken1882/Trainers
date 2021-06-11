def start_interact_fiber
  begin
    loop{ Input.mouse_ldown(true,false); Fiber.yield; }
  ensure
    Input.mouse_lup(true,false)
  end
end

def start_walk_fiber
  begin
    loop{ Input.key_down(Keymap[:vk_W]); Fiber.yield; }
  ensure
    Input.mouse_lup(true,false)
  end
end