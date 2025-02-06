import _G, utils
from random import randint
from errors import NeoError
from ruffle.base_flash import BaseFlash
from copy import deepcopy
from threading import Thread
import numpy as np

MODULE_ENABLED = False
try:
    import cv2
    from PIL import Image
    import pytesseract
    MODULE_ENABLED = True
except ImportError:
    _G.log_error("Please install OpenCV, Pillow, and pytesseract to play roodoku")
    pass

IMAGE_PATH = '.tmp/roodoku.png'

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

class Roodoku(BaseFlash):
    def __init__(self, page):
        super().__init__(page, "https://www.neopets.com/games/game.phtml?game_id=820")

    def start_loop(self):
        global MODULE_ENABLED
        if not MODULE_ENABLED:
            _G.log_warning("Please install OpenCV, Pillow, and pytesseract to play roodoku")
            yield
            return
        for _ in range(self.max_plays - self.played_times):
            yield from self.start_game()
            yield from self.send_score()
            yield from _G.rwait(1)

    def start_game(self):
        _G.log_info("Starting game")
        self.click(120, 500)
        yield from _G.rwait(2)
        self.click(230, 355)
        yield from _G.rwait(1)
        self.hover(20, 200)
        yield from _G.rwait(20)
        _G.log_info("Playing sudoku")
        yield from self.go_sudoku()
        yield from self.send_score()

    def send_score(self):
        _G.log_info("Sending score")
        yield from _G.rwait(1)
        self.click(300, 350)
        yield from _G.rwait(1)
        self.click(300, 350)
        yield from _G.rwait(10)
        self.click(300, 341, random_x=(-20, 20), random_y=(-2, 2))

    def go_sudoku(self):
        sudoku = []
        yield from self.interpret_image(sudoku)
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
                    wt = randint(300, 1000) / 1000.0
                    self.click(mx, my, random_x=(0, 0), random_y=(0, 0))
                    yield from _G.rwait(wt)
                    self.hover(20, 200)
                    wt = randint(300, 1500) / 1000.0
                    yield from _G.rwait(wt)
            yield
        yield from _G.rwait(30)

    def interpret_image(self, ret):
        _G.log_info("Interpreting sudoku image")
        screenshot_bytes = self.find_flash().screenshot()
        def _do_ocr(cls_self, screenshot_bytes):
            utils.preprocess_image(
                buffer=screenshot_bytes,
                rect=(50, 100, 400, 450), bin_colors=[(0,0,0)],
                output=IMAGE_PATH
            )
            grids = cls_self.read_sudoku_image()
            for row in grids:
                ret.append(row)
        # ridiculously slow when putting off-thread, so blocking here
        _do_ocr(self, screenshot_bytes)
        # th = Thread(target=_do_ocr, args=(self, screenshot_bytes))
        # th.start()
        # while th.is_alive():
        #     yield
        return ret

    def read_sudoku_image(self, path=IMAGE_PATH, cell_rsize=24):
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
