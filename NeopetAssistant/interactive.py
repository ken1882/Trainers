# copy-paste to python interactive shell to test
import _G
import utils
import os
from playwright.sync_api import sync_playwright
from random import randint
from errors import NeoError
from models.mixins.transaction import Transaction, NeoItem
import page_action as action
import captcha
import jellyneo as jn

def create_context(pw, profile_name, enable_extensions=True):
    _G.log_info(f"Creating browser context#{profile_name}")
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--disable-features=IsolateOrigins,site-per-process',
        '--auto-open-devtools-for-tabs',
    ]
    if enable_extensions:
        args.append(f"--disable-extensions-except={os.getenv('BROWSER_EXTENSION_PATHS')}")
        args.append(f"--load-extension={os.getenv('BROWSER_EXTENSION_PATHS')}")
    _G.log_info(f"Launching browser context#{profile_name} with args: {args}")
    return pw.chromium.launch_persistent_context(
        f"{_G.BROWSER_PROFILE_DIR}/profile_{profile_name}",
        headless=False,
        handle_sigint=False,
        color_scheme='dark',
        args=args
    )

fiber = None
def resume():
    return next(fiber)

pw = sync_playwright().start()
context = create_context(pw, 'default')
page = context.new_page()

import ruffle.fashion_fever as ff
player = ff.FashionFever(page)
fiber = player.run()

page.goto('https://www.neopets.com/games/game.phtml?game_id=805&size=regular&quality=high&play=true')


def pclick(x, y):
    return page.frame_locator('#game_frame').locator('ruffle-embed').click(button='left', position={'x': x, 'y': y})

pclick(450, 320)

page.goto('https://www.neopets.com/objects.phtml?type=shop&obj_type=56')
page.wait_for_load_state('networkidle')

def determine_strategy(last_price, max_price, depth=0, **kwargs):
    if last_price < 3000:
        return rounded_up(last_price, max_price, depth)
    raise NeoError(1, f"No strategy defined for price {last_price} {max_price}")

def solve_captcha(page, debug=True):
    pos = captcha.solve(page)
    if not pos:
        raise NeoError(1, "Failed to solve captcha")
    captcha_canvas = page.query_selector('input[type="image"][src*="/captcha_show.phtml"]')
    bb = captcha_canvas.bounding_box()
    mx, my = pos
    mx += bb['x']
    my += bb['y']
    _G.log_info(f"Clicking captcha at {mx}, {my}")
    if debug:
        action.draw_debug_point(page, mx, my)
    else:
        page.mouse.click(mx, my)


def rounded_up(last_price, max_price, depth):
    if depth > 5:
        return max_price
    if last_price == 0:
        return int(max_price * 0.4 // 10 * 10)
    delta = max_price - last_price
    step  = 20
    if delta > 500:
        step = 100
    elif delta > 100:
        step = 50
    ret = max(1, min(max_price, last_price + int(delta * 0.4 // step * step)))
    if ret == last_price:
        ret = int(max_price // 10 * 10)
    return ret

def calc_numkey_interval(current, next):
    keys = '1234567890..........E'
    delta = abs(keys.index(current) - keys.index(next))
    ret = 0.2
    for _ in range(delta):
        ret += randint(10, 30) / 100.0
    return ret

if 'SOLD OUT!' in page.content():
    _G.log_info("Item is sold out")


last_price = 0
depth = 0

purpose_node = page.query_selector('#shopkeeper_makes_deal')
action.scroll_to(page, 0, max(0, purpose_node.bounding_box()['y'] - 300))
max_price = utils.str2int(purpose_node.text_content())
bargain_price = determine_strategy(last_price, max_price, depth)
inp_node = page.query_selector('input[name=current_offer]')
action.click_node(page, inp_node)
page.keyboard.press('Control+A')
input_str = str(bargain_price)+'E'
for i,digit in enumerate(input_str):
    if digit == 'E':
        break
    page.keyboard.press(digit)
    _G.wait(calc_numkey_interval(input_str[i], input_str[i+1]))

solve_captcha(page)
last_price = bargain_price
depth += 1

solve_captcha(page, 0)

items = []
nodes = page.query_selector_all('.petCare-itemgrid-item')
for node in nodes:
    name = node.get_attribute('data-itemname')
    if not name:
        continue
    items.append(NeoItem(**{
        'name': name,
        'id': node.get_attribute('id'),
        'image': node.get_attribute('data-image'),
        'description': node.get_attribute('data-itemdesc'),
        'rariry': node.get_attribute('data-rarity'),
        'value_npc': node.get_attribute('data-itemvalue'),
        'value_pc': 0,
        'item_type': node.get_attribute('data-itemtype'),
    }))

jn.batch_search([item.name for item in items])