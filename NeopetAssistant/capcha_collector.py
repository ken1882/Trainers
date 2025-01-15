import _G, utils
import os


SAVE_DIR = './.capcha'

def grab_capcha(page):
    if not os.path.exists(SAVE_DIR):
        os.mkdir(SAVE_DIR)
    if 'SOLD OUT!' in page.content():
        _G.logger.info("Item is sold out")
        return
    try:
        capcha = page.query_selector('input[type="image"][src*="/captcha_show.phtml"]')
    except Exception as err:
        _G.logger.warning("Error while getting capcha canvas")
        utils.handle_exception(err)
        return
    if not capcha:
        return
    capcha.screenshot(path=f"{SAVE_DIR}/capcha.png")
    return True
