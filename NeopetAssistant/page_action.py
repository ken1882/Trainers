import _G, utils
from random import randint

AvailableNp = 0

def scroll_to(page, x=0, y=0):
    page.evaluate(f"window.scrollTo({x}, {y})")

def click_node(page, node, x_mul=0.5, y_mul=0.5, random_x=(-10, 10), random_y=(-10, 10), wait=0):
    bb = node.bounding_box()
    mx = bb['x'] + int(bb['width'] * x_mul) + randint(*random_x)
    my = bb['y'] + int(bb['height'] * y_mul) + randint(*random_y)
    page.mouse.click(mx, my)
    _G.wait(wait)

def get_availabe_np(page):
    global AvailableNp
    # new style
    AvailableNp = utils.str2int(page.query_selector('#npanchor').text_content())
    return AvailableNp
