import _G
import traceback
import os
import io
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

def resize_image(size, img:Image=None, src_file=None, dst_file=None):
    if src_file and dst_file:
        img = Image.open(src_file)
        img = img.resize(size)
        img.save(dst_file)
        return img
    return img.resize(size)

def img2str(image:Image=None, buffer:bytes=None, file:str=None, lang='jpn', config='--psm 12 --psm 13'):
    if file:
        if not os.path.exists(file):
            raise FileNotFoundError(f"Image file not found: {file}")
        image = Image.open(file)
    if buffer:
        image = Image.open(io.BytesIO(buffer))
    if not image:
        raise ValueError("No image provided")
    return pytesseract.image_to_string(image, lang=lang, config=config) or ''

def preprocess_image(
        image:Image=None, buffer:bytes=None, file:str=None, rect:tuple=(),
        zoom=1.0, bin_colors=[], bin_tolerance=15, trim=False, output:str=None
    ):
    """
    Preprocess an image for OCR, including loading, resizing, cropping, binarization, and trimming.

    Parameters:
    - image: The image object to process.
    - buffer: Image data in bytes format.
    - file: Path to the image file.
    - rect: coordinates for cropping the image (left, upper, right, lower).
    - output: If provided, saves the processed image to this path.
    - zoom: Scale factor for resizing the image before OCR (default is 1.0).
    - lang: Language code for Tesseract OCR (default is 'jpn').
    - config: Additional configurations for Tesseract OCR.
    - bin_colors: List of RGB tuples for color-based binarization.
    - bin_tolerance: Color tolerance for binarization (default is 15).
    - num_only: If True, restricts OCR to numbers only.
    - char_whitelist: List of allowed characters for OCR.
    - trim: If True, automatically trims unnecessary empty space.
    - output: If provided, saves the processed image to this path.

    Returns:
        PIL.Image: The preprocessed image.
    """
    # Load the image from file or buffer if provided
    if buffer:
        image = Image.open(io.BytesIO(buffer))
    elif file:
        image = Image.open(file)
    # Make a copy to avoid modifying the original image
    if image:
        image = image.copy()
    # Resize if zoom is different from 1.0
    if zoom != 1.0:
        size = (int(image.size[0] * zoom), int(image.size[1] * zoom))
        image = image.resize(size, Image.ANTIALIAS)
    # Crop if `rect` is provided
    if rect:
        image = image.crop(rect)
    # Apply binarization if colors are provided
    if bin_colors:
        image = image.convert('RGB')
        a = np.array(image)
        # Create a mask for colors within the specified tolerance
        mask = np.zeros_like(a[..., 0], dtype=bool)
        for color in bin_colors:
            mask |= (
                (a[..., 0] >= color[0] - bin_tolerance) & (a[..., 0] <= color[0] + bin_tolerance) &
                (a[..., 1] >= color[1] - bin_tolerance) & (a[..., 1] <= color[1] + bin_tolerance) &
                (a[..., 2] >= color[2] - bin_tolerance) & (a[..., 2] <= color[2] + bin_tolerance)
            )
        # Convert matching colors to white and everything else to black
        a[~mask] = [0, 0, 0]  # Black
        a[mask] = [255, 255, 255]  # White
        image = Image.fromarray(a)
        # Trim whitespace around the detected text
        if trim:
            PADDING = 2
            a2 = np.where(mask, 255, 0).astype(np.uint8)
            nonzero_cols = np.argwhere(a2.max(axis=0) > 0)
            left_col = nonzero_cols.min()
            right_col = nonzero_cols.max()
            bbox = (left_col - PADDING, 0, right_col + 1 + PADDING, a2.shape[0])
            image = image.crop(bbox)
    if output:
        image.save(output)
    return image

def ocr_rect(
        image:Image=None, buffer:bytes=None, file:str=None, rect:tuple[4]=(), output:str=None,
        zoom=1.0, lang='jpn', config='--psm 12 --psm 13',
        bin_colors=[], bin_tolerance=15, num_only=False, char_whitelist=[],
        trim=False
    ):
    '''
    Perform OCR (Optical Character Recognition) on an image, allowing pre-processing such as cropping,
    zooming, binarization, and trimming.

    Parameters:
    - image: The image object to process.
    - buffer: Image data in bytes format.
    - file: Path to the image file.
    - rect: coordinates for cropping the image (left, upper, right, lower).
    - output: If provided, saves the processed image to this path.
    - zoom: Scale factor for resizing the image before OCR (default is 1.0).
    - lang: Language code for Tesseract OCR (default is 'jpn').
    - config: Additional configurations for Tesseract OCR.
    - binarize_colors: List of RGB tuples for color-based binarization.
    - tolerance: Color tolerance for binarization (default is 15).
    - num_only: If True, restricts OCR to numbers only.
    - char_whitelist: List of allowed characters for OCR.
    - trim: If True, automatically trims unnecessary empty space.

    Returns:
        str: The recognized text from the image.

    Notes:
        - One of `image` `buffer` `file` must be provided.
        - If `zoom` is different from 1.0, the image is resized before OCR.
        - If `rect` is specified, the image is cropped before OCR.
        - If `binarize_colors` is used, only matching colors remain visible.
    '''
    _G.log_info(f"Processing OCR")
    if num_only:
        lang = 'eng'
        config += ' -c tessedit_char_whitelist=1234567890'
    elif char_whitelist:
        lang = 'eng'
        config += f" -c tessedit_char_whitelist={char_whitelist}"
    image = preprocess_image(
        image=image, buffer=buffer, file=file, rect=rect, zoom=zoom,
        bin_colors=bin_colors, bin_tolerance=bin_tolerance, trim=trim,
        output=output
    )
    try:
        return img2str(image, lang=lang, config=config).translate(str.maketrans('。',' ')).strip()
    finally:
        image.close()

def snake2pascal(snake_str):
    return ''.join([word.capitalize() for word in snake_str.split('_')])

def ensure_dir_exist(path):
    path = path.split('/')
    path.pop()
    if len(path) == 0:
        return
    pwd = ""
    for dir in path:
        pwd += f"{dir}/"
        if not os.path.exists(pwd):
            os.mkdir(pwd)
