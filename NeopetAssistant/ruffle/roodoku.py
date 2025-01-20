import _G, utils
from random import randint
from errors import NeoError
from ruffle.base_flash import BaseFlash
from copy import deepcopy
import cv2
import numpy as np
import pytesseract

def solve_sudoku(sudoku):
    def is_valid_move(x, y, n):
        for i in range(9):
            if sudoku[x][i] == n or sudoku[i][y] == n:
                return False
        x0, y0 = 3 * (x // 3), 3 * (y // 3)
        for i in range(3):
            for j in range(3):
                if sudoku[x0 + i][y0 + j] == n:
                    return False
        return True

    def solve():
        for x in range(9):
            for y in range(9):
                if sudoku[x][y] == 0:
                    for n in range(1, 10):
                        if is_valid_move(x, y, n):
                            sudoku[x][y] = n
                            if solve():
                                return True
                            sudoku[x][y] = 0
                    return False
        return True

    if solve():
        return sudoku
    return None

class Roodoku(BaseFlash):
    def __init__(self, page):
        super().__init__(page, "https://www.neopets.com/games/game.phtml?game_id=805")

    def start_loop(self):
        for _ in range(3):
            yield from self.start_game()
            yield from self.send_score()
            yield from _G.rwait(1)

    def start_game(self):
        pass

    def send_score(self):
        yield from _G.rwait(60)

    def go_sudoku(self):
        self.interpret_image()
        yield
        sudoku = self.read_sudoku_image('.tmp/sudoku.png')
        _G.log_info(f"Grids: {sudoku}")
        solution = solve_sudoku(deepcopy(sudoku))
        _G.log_info(f"Solution: {solution}")
        sx, sy  = 502, 484
        n_delta = 15
        grid_delta = 44
        for i in range(9):
            for j in range(9):
                _G.log_info(f"{i},{j} = ({sudoku[i][j]} -> {solution[i][j]})")
                if sudoku[i][j] == 0:
                    mx = sx + j * grid_delta + ((solution[i][j] - 1) % 3 - 1) * n_delta
                    my = sy + i * grid_delta + ((solution[i][j] - 1) // 3 - 1) * n_delta
                    _G.log_info(f"Clicking {mx},{my}")
                    wt = randint(300, 2000) / 1000.0
                    # Input.click(mx, my)
                    yield from _G.rwait(1+wt)
                    # Input.set_cursor_pos(942, 337
                    wt = randint(300, 2000) / 1000.0
                    yield from _G.rwait(1+wt)
                    yield

    def interpret_image(self):
        _G.flush()
        utils.ocr_rect(
            (483, 465, 875, 855),
            fname='sudoku.png',
            whitelist='0123456789',
            binarization_colors=[(0, 0, 0)]
        )


    def read_sudoku_image(self, path):
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
                text = pytesseract.image_to_string(cell, config='--psm 10 -c tessedit_char_whitelist=0123456789')
                text = text.strip()
                # Fill empty cells with 0
                row.append(int(text) if text.isdigit() else 0)
            sudoku_array.append(row)
        return sudoku_array
