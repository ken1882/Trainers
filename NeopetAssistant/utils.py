import _G
import traceback
import os
import pytz, tzlocal
import numpy as np
from datetime import datetime
from difflib import SequenceMatcher
from PIL import Image

try:
    import pytesseract
except Exception:
    _G.log_warning("Pytesseract not available, OCRs won't be available")


def handle_exception(err, errinfo=None):
    if not errinfo:
        errinfo = traceback.format_exc()
    _G.log_error(f"An error occurred during runtime!\n{str(err)}\n{errinfo}")

def pst2localt(pst: datetime):
    pst_tz = pytz.timezone('US/Pacific')
    local_tz = tzlocal.get_localzone()
    try:
        pst = pst_tz.localize(pst)
    except ValueError:
        pst = pst.replace(tzinfo=pst_tz)
    local_time = pst.astimezone(local_tz)
    return local_time

def localt2pst(localt: datetime):
    pst_tz = pytz.timezone('US/Pacific')
    local_tz = pytz.timezone(tzlocal.get_localzone().key)
    try:
        localt = local_tz.localize(localt)
    except ValueError:
        localt = localt.replace(tzinfo=local_tz)
    pst = localt.astimezone(pst_tz)
    return pst

# Neopets server time is in PST
nst2localt = pst2localt
localt2nst = localt2pst

def diff_string(a,b):
    return SequenceMatcher(None,a,b).ratio()

def str2int(ss):
    neg_mul = 1
    if ss.strip().startswith('-'):
        neg_mul = -1
    try:
        return int("".join([n for n in ss if n.isdigit()])) * neg_mul
    except ValueError:
        return None

def resize_image(size, src_fname, dst_fname):
    img = Image.open(src_fname)
    ret = img.resize(size)
    ret.save(dst_fname)
    return ret

def img2str(image_file, lang='jpn', config='--psm 12 --psm 13'):
    if not os.path.exists(image_file) and not image_file.startswith(_G.DCTmpFolder):
        image_file = f"{_G.DCTmpFolder}/{image_file}"
    return pytesseract.image_to_string(image_file, lang=lang, config=config) or ''

def ocr_rect(rect, fname, zoom=1.0, lang='jpn', config='--psm 12 --psm 13', **kwargs):
    _G.log_info(f"Processing OCR for {fname}")
    if kwargs.get('num_only'):
        lang = 'eng'
        config += ' -c tessedit_char_whitelist=1234567890'
    elif kwargs.get('whitelist'):
        lang = 'eng'
        config += f" -c tessedit_char_whitelist={kwargs.get('whitelist')}"
    if not os.path.exists(fname):
        fname = f"{_G.DCTmpFolder}/{fname}"
        img = graphics.take_snapshot(rect, fname)
    if zoom != 1.0:
        size = (int(img.size[0]*zoom), int(img.size[1]*zoom))
        resize_image(size, fname, fname)
    bin_colors = kwargs.get('binarization_colors')
    tolerance = kwargs.get('bias_tolerance', 15)
    img.close()
    if bin_colors:
        img = Image.open(fname)
        img = img.convert('RGB')
        a = np.array(img)
        # Convert matched colors to white (255, 255, 255), everything else to black (0, 0, 0)
        mask = np.zeros_like(a[..., 0], dtype=bool)
        for color in bin_colors:
            mask |= (
                (a[..., 0] >= color[0] - tolerance) & (a[..., 0] <= color[0] + tolerance) &
                (a[..., 1] >= color[1] - tolerance) & (a[..., 1] <= color[1] + tolerance) &
                (a[..., 2] >= color[2] - tolerance) & (a[..., 2] <= color[2] + tolerance)
            )
        a[~mask] = [0, 0, 0]  # Set unmatched pixels to black
        a[mask]  = [255, 255, 255]  # Set matched pixels to white
        img = Image.fromarray(a)
        img.save(fname)
        if kwargs.get('trim'):
            PADDING = 2
            a2 = np.where(mask, 255, 0).astype(np.uint8)
            nonzero_cols = np.argwhere(a2.max(axis=0) > 0)
            left_col = nonzero_cols.min()
            right_col = nonzero_cols.max()
            bbox = (left_col - PADDING, 0, right_col + 1 + PADDING, a2.shape[0])
            cropped_img = img.crop(bbox)
            cropped_img.save(fname)
        img.close()
    return img2str(fname, lang, config).translate(str.maketrans('。',' ')).strip()

def snake2pascal(snake_str):
    return ''.join([word.capitalize() for word in snake_str.split('_')])
