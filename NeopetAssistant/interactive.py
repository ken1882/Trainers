# copy-paste to python interactive shell to test
import _G
import utils
import os
from playwright.sync_api import sync_playwright
from scheduler import JobScheduler
from jobs.login import LoginJob
from jobs.trudys_surprise import TrudysSurpriseJob


Scheduler = None

def create_context(pw, id, enable_extensions=True):
    _G.logger.info(f"Creating browser context#{id}")
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--disable-features=IsolateOrigins,site-per-process',
    ]
    if enable_extensions:
        args.append(f"--disable-extensions-except={os.getenv('BROWSER_EXTENSION_PATHS')}")
        args.append(f"--load-extension={os.getenv('BROWSER_EXTENSION_PATHS')}")
    _G.logger.info(f"Launching browser context#{id} with args: {args}")
    return pw.chromium.launch_persistent_context(
        "./profiles/profile_{:04d}".format(id),
        headless=False,
        handle_sigint=False,
        color_scheme='dark',
        args=args
    )


pw = sync_playwright().start()
context = create_context(pw, 1)
page = context.new_page()
page.goto('https://www.neopets.com/objects.phtml?type=shop&obj_type=56')
page.wait_for_load_state('networkidle')


import _G
import utils
from random import randint
from errors import NeoError
import page_action as action
import captcha

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
    _G.logger.info(f"Clicking captcha at {mx}, {my}")
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
    _G.logger.info("Item is sold out")


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
