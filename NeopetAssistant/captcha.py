import _G, utils
import os
from datetime import datetime
from PIL import Image, ImageDraw

SAVE_DIR = './.captcha'

def solve(page, debug=True):
    image_path = grab_captcha(page)
    if not image_path:
        return
    if debug:
        output_image_path = image_path.replace(".png", "_debug.png")
    return process_captcha(image_path, output_image_path)

def get_captcha_url(page):
    try:
        captcha = page.query_selector('input[type="image"][src*="/captcha_show.phtml"]')
        return captcha.get_property('src').json_value()
    except Exception:
        return ''

def grab_captcha(page):
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    if 'SOLD OUT!' in page.content():
        _G.log_info("Item is sold out")
        return
    try:
        image_url = get_captcha_url(page)
        res = page.request.get(image_url)
        if res.status != 200:
            _G.log_warning(f"Failed to get captcha image ({res.status})")
            return
        filename = f"{SAVE_DIR}/captcha_{int(datetime.now().timestamp())}.png"
        with open(filename, 'wb') as f:
            f.write(res.body())
        return filename
    except Exception as err:
        _G.log_warning("Error while getting captcha canvas")
        utils.handle_exception(err)
        return


def process_captcha(input_image_path, output_image_path=None):
    image = Image.open(input_image_path).convert("RGB")
    pixels = image.load()

    min_luminance = float("inf")
    click_position = (0, 0)

    # Find the darkest pixel
    for y in range(image.height):
        for x in range(image.width):
            r, g, b = pixels[x, y]

            # Calculate luminance (brightness)
            luminance = (max(r, g, b) + min(r, g, b)) / 2

            if luminance < min_luminance:
                min_luminance = luminance
                click_position = (x, y)

    if output_image_path:
        debug_image = image.copy()
        draw = ImageDraw.Draw(debug_image)
        dot_radius = 5
        draw.ellipse(
            [
                (click_position[0] - dot_radius, click_position[1] - dot_radius),
                (click_position[0] + dot_radius, click_position[1] + dot_radius),
            ],
            fill="red",
        )
        debug_image.save(output_image_path)
    return click_position


# Example usage
if __name__ == "__main__":
    for image in os.listdir(".captcha"):
        if image.startswith("debug_"):
            continue
        input_image = f".captcha/{image}"
        output_image = f".captcha/debug_{image}"
        print(input_image, process_captcha(input_image, output_image))
