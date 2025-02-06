# copy-paste to python interactive shell to test
import _G
import utils
import os, re
import argv_parse
from playwright.sync_api import sync_playwright
from random import randint
from copy import deepcopy
from collections import defaultdict
from errors import NeoError
from models.mixins.transaction import Transaction, NeoItem
from models import shop
from main import create_context
import page_action as action
import captcha
import jellyneo as jn
from PIL import Image
import cv2, pytesseract
argv_parse.load()

import importlib

FEED_BLACKLIST = [
    r"poison",
    r"rotten",
    r"dung",
    r"glowing",
    r"clay",
    r"smelly",
]

MAX_FEED_VALUE = 1000
MAX_FEED_LEVEL = 8 # full up

HUNGER_LEVEL_MAP = defaultdict(lambda: 10, {
    "dying": 0,
    "starving": 1,
    "famished": 2,
    "very hungry": 3,
    "hungry": 4,
    "not hungry": 5,
    "fine": 6,
    "satiated": 7,
    "full up": 8,
    "very full": 9,
    "bloated": 10,
    "very bloated": 11,
})

fiber = None
def resume():
    return next(fiber)

def wait_for_fiber():
    while True:
        try:
            resume()
        except StopIteration:
            break
        _G.wait(0.1)

pw = sync_playwright().start()
context = create_context(pw, 'default')
page = context.new_page()
page.goto('https://www.neopets.com/faerieland/employ/employment.phtml')

def scan_quests():
    panel = page.query_selector('.content')
    nodes = panel.query_selector_all('tr > td')
    idx = 3
    quests = []
    jn_args = []
    while idx < len(nodes):
        eles = nodes[idx].inner_html().split('<br>')
        name = eles[0].split('</b>')[-1].strip()
        amount = utils.str2int(eles[0].split('</b>')[0].strip())
        reward = utils.str2int(eles[-1].split('</b>')[-1].strip())
        jn_args.append(name)
        quests.append({
            'name': name,
            'amount': amount,
            'reward': reward,
            'cost': 0,
        })
        idx += 5
    jn.batch_search(jn_args)
    for quest in quests:
        item = jn.get_item_details_by_name(quest['name'])
        if item:
            quest['cost'] = item['price'] * quest['amount']
    quests = sorted(quests, key=lambda x: x['reward'] - x['cost'], reverse=True)
    for q in quests:
        print(f"{q['name']} {q['reward'] - q['cost']} (mkt: {q['cost']})")


pets = []
selected_pet = None

def scan_all_pets():
    global pets
    pets = []
    nodes = page.query_selector_all('.hp-carousel-nameplate')
    for node in nodes:
        name = node.get_attribute('data-name')
        if not name:
            continue
        pets.append({
            'name': name,
            'health': node.get_attribute('data-health'),
            'max_health': node.get_attribute('data-maxhealth'),
            'hunger': node.get_attribute('data-hunger'),
            'level': node.get_attribute('data-level'),
            'species': node.get_attribute('data-species'),
            'color': node.get_attribute('data-color'),
            'mood': node.get_attribute('data-mood'),
            'active': node.get_attribute('data-active'),
            'node': node
        })

def select_pet(index):
    global selected_pet
    if index < 0 or index >= len(pets):
        _G.log_warning(f"Invalid pet index: {index} (total pets: {len(pets)})")
        return
    if selected_pet:
        unselect()
    selected_pet = pets[index]
    pets[index]['node'].click()

def unselect():
    global selected_pet
    selected_pet = None
    page.mouse.click(50+randint(-10, 10), 200+randint(-10, 100))

items = []
def scan_usable_items():
    global items
    items = []
    nodes = page.query_selector_all('.petCare-itemgrid-item')
    items_names = []
    for node in nodes:
        name = node.get_attribute('data-itemname')
        if not name:
            continue
        items_names.append(name)
        item = NeoItem(**{
            'name': name,
            'id': node.get_attribute('id'),
            'image': node.get_attribute('data-image'),
            'description': node.get_attribute('data-itemdesc'),
            'rariry': node.get_attribute('data-rarity'),
            'value_npc': node.get_attribute('data-itemvalue'),
            'value_pc': 0,
            'item_type': node.get_attribute('data-itemtype'),
        })
        item.node = node
        items.append(item)
    jn.batch_search(items_names)
    for item in items:
        item.update_jn()

def determine_item_to_feed():
    if not items:
        return
    candidates = []
    for item in items:
        if item.is_rubbish():
            continue
        if any(re.search(pattern, item.name, re.I) for pattern in FEED_BLACKLIST):
            continue
        candidates.append(item)
    for item in sorted(candidates, key=lambda x: x.value_pc):
        if item.value_pc < 1000:
            return items.index(item)
    return -1

def is_hungry():
    if not selected_pet:
        return False
    return HUNGER_LEVEL_MAP[selected_pet['hunger']] < MAX_FEED_LEVEL

def update_pet(index):
    if index < 0 or index >= len(pets):
        _G.log_warning(f"Invalid pet index: {index} (total pets: {len(pets)})")
        return
    node = pets[index]['node']
    pets[index] = {
        'name': node.get_attribute('data-name'),
        'health': node.get_attribute('data-health'),
        'max_health': node.get_attribute('data-maxhealth'),
        'hunger': node.get_attribute('data-hunger'),
        'level': node.get_attribute('data-level'),
        'species': node.get_attribute('data-species'),
        'color': node.get_attribute('data-color'),
        'mood': node.get_attribute('data-mood'),
        'active': node.get_attribute('data-active'),
        'node': node
    }
    return pets[index]

page.query_selector('#petCareLinkFeed').click()
scan_usable_items()
item_index = determine_item_to_feed()
items[item_index].click()
page.query_selector('#petCareUseItem').click()

page.locator('.ddcontainer').hover()
page.mouse.down()
bb = page.locator('#npcma_neopetcustomise').bounding_box()
mx = bb['x'] + randint(20, 50)
my = bb['y'] + randint(20, 50)
page.mouse.move(mx, my, steps=9)
page.mouse.up()


# ---

def buy(id):
    global fiber
    importlib.reload(shop)
    s = shop.NeoShop(id, page=page)
    fiber = s.visit()
    wait_for_fiber()
    s.scan_goods()
    fiber = s.lookup_goods_details()
    wait_for_fiber()
    gs = s.get_profitable_goods()
    if gs:
        print(gs[0]['name'], gs[0]['profit'])
        if gs[0]['profit'] > 1000:
            fiber = s.buy_good(index=gs[0]['index'])
            wait_for_fiber()

for id in shop.NAME_DICT:
    buy(id)

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


page.goto('https://www.neopets.com/games/game.phtml?game_id=820')
IMAGE_PATH = '.tmp/sudoku.png'
def find_flash():
    return page.frame_locator('#game_frame').locator('ruffle-embed')

def interpret_image():
    screenshot_bytes = find_flash().screenshot()
    utils.preprocess_image(
        buffer=screenshot_bytes,
        rect=(50, 100, 400, 450), bin_colors=[(0,0,0)],
        output=IMAGE_PATH
    )
    return read_sudoku_image()

def read_sudoku_image(path=IMAGE_PATH, cell_rsize=24):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    # Threshold the image to make it binary
    _, binary_img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY_INV)
    # Find contours of the grid and cells
    contours, _ = cv2.findContours(binary_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Sort contours to identify the largest grid (Sudoku grid)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    # Get the bounding box of the largest contour
    x, y, w, h = cv2.boundingRect(contours[0])
    grid = img[y:y+h, x:x+w]
    # Resize the grid to a standard size for easier processing
    grid_resized = cv2.resize(grid, (450, 450))
    # Divide the grid into 9x9 cells
    cell_size = 50
    sudoku_array = []
    for i in range(9):
        row = []
        for j in range(9):
            cell = grid_resized[i * cell_size:(i + 1) * cell_size, j * cell_size:(j + 1) * cell_size]
            # Use OCR to extract text from each cell
            cimg = Image.fromarray(cell, 'L')
            cimg.save(f'.tmp/cell_{i}_{j}.png')
            text = pytesseract.image_to_string(cimg, config='--oem 3 --psm 10 -c tessedit_char_whitelist=123456789')
            if not text:
                rimg = cimg.resize((cell_rsize, cell_rsize), Image.Resampling.LANCZOS)
                text = pytesseract.image_to_string(rimg, config='--oem 3 --psm 10 -c tessedit_char_whitelist=123456789')
            text = text.strip()
            # Fill empty cells with 0
            row.append(int(text) if text.isdigit() else 0)
        sudoku_array.append(row)
    return sudoku_array

def solve_sudoku(num_list):
    def is_valid_move(x, y, n):
        for i in range(9):
            if num_list[x][i] == n or num_list[i][y] == n:
                return False
        x0, y0 = 3 * (x // 3), 3 * (y // 3)
        for i in range(3):
            for j in range(3):
                if num_list[x0 + i][y0 + j] == n:
                    return False
        return True
    def solve():
        for x in range(9):
            for y in range(9):
                if num_list[x][y] == 0:
                    for n in range(1, 10):
                        if is_valid_move(x, y, n):
                            num_list[x][y] = n
                            if solve():
                                return True
                            num_list[x][y] = 0
                    return False
        return True
    if solve():
        return num_list
    return None

def go_sudoku():
    sudoku = interpret_image()
    _G.log_info(f"Grids: {sudoku}")
    solution = solve_sudoku(deepcopy(sudoku))
    _G.log_info(f"Solution: {solution}")
    sx = 65
    sy = 118
    n_delta = 12
    grid_delta = 40
    for i in range(9):
        for j in range(9):
            _G.log_info(f"{i},{j} = ({sudoku[i][j]} -> {solution[i][j]})")
            if sudoku[i][j] == 0:
                mx = sx + j * grid_delta + ((solution[i][j] - 1) % 3 - 1) * n_delta
                my = sy + i * grid_delta + ((solution[i][j] - 1) // 3 - 1) * n_delta
                _G.log_info(f"Clicking {mx},{my}")
                wt = randint(100, 500) / 1000.0
                action.locator_click(find_flash(), mx, my, random_x=(0,0), random_y=(0,0))
                _G.wait(wt)
                action.locator_hover(find_flash(), 20, 200)
                wt = randint(100, 500) / 1000.0
                _G.wait(wt)
