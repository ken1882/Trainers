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
