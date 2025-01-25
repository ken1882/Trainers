import _G, utils
import os
from random import randint

JS_DIRECTORY = './js'
AvailableNp = 0

def eval_js(page, script_name):
    path = f'{JS_DIRECTORY}/{script_name}.js'
    if not os.path.exists(path):
        _G.log_error(f"Script {script_name} not found!")
        return
    with open(path, 'r') as f:
        return page.evaluate(f.read())

def scroll_to(page, x=0, y=0):
    return page.evaluate(f"window.scrollTo({x}, {y})")

def click_node(page, node, x_mul=0.5, y_mul=0.5, random_x=(-10, 10), random_y=(-10, 10)):
    bb = node.bounding_box()
    mx = bb['x'] + int(bb['width'] * x_mul) + randint(*random_x)
    my = bb['y'] + int(bb['height'] * y_mul) + randint(*random_y)
    page.mouse.click(mx, my)

def locator_click(locator, x, y, button='left', modifiers=[], random_x=(-10, 10), random_y=(-10, 10)):
    ''' https://playwright.dev/python/docs/api/class-locator#locator-click '''
    mx = x + randint(*random_x)
    my = y + randint(*random_y)
    return locator.click(
        button=button,
        modifiers=modifiers,
        position={'x': mx, 'y': my}
    )

def get_available_np(page):
    global AvailableNp
    AvailableNp = utils.str2int(page.query_selector('#npanchor').text_content())
    return AvailableNp

def draw_debug_point(page, x, y, radius=5, timeout=3000):
    return page.evaluate(f"""
        const marker = document.createElement('div');
        marker.style.width = '{radius*2}px';
        marker.style.height = '{radius*2}px';
        marker.style.backgroundColor = 'red';
        marker.style.position = 'fixed';
        marker.style.top = '{y - radius}px';
        marker.style.left = '{x - radius}px';
        marker.style.borderRadius = '50%';
        marker.style.zIndex = '9999';
        document.body.appendChild(marker);
        setTimeout(() => marker.remove(), {timeout});
    """)

def drag_to(page, locator_a, locator_b, steps=5, random_x=(-10, 10), random_y=(-10, 10)):
    locator_a.hover()
    page.mouse.down()
    bb = locator_b.bounding_box()
    mx = (bb['x'] + bb['width']) // 2 + randint(*random_x)
    my = (bb['y'] + bb['height']) // 2 + randint(*random_y)
    _G.log_info(f"Drag to: {mx},{my}")
    page.mouse.move(mx, my, steps=steps)
    page.mouse.up()
    return True

