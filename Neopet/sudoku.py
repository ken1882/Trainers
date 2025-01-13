import _G, utils
import pytesseract
from copy import deepcopy
import cv2
import Input

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

def go_sudoku():
    interpret_image()
    yield
    sudoku = read_sudoku_image('.tmp/sudoku.png')
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
                Input.click(mx, my)
                _G.wait(0.5)
                Input.set_cursor_pos(942, 337)
                _G.wait(0.5)
                yield

def interpret_image():
    _G.flush()
    utils.ocr_rect(
        (483, 465, 875, 855),
        fname='sudoku.png',
        whitelist='0123456789',
        binarization_colors=[(0, 0, 0)]
    )


def read_sudoku_image(path):
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
