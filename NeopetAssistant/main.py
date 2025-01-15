import _G
import utils
import os, sys
import code
from playwright.sync_api import sync_playwright
from scheduler import JobScheduler
from jobs.login import LoginJob
from jobs.trudys_surprise import TrudysSurpriseJob
from jobs.giant_jelly import GiantJellyJob
from jobs.giant_omelette import GiantOmeletteJob
from jobs.tdmbgpop import TDMBGPOPJob
from jobs.tombola import TombolaJob
from threading import Thread

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

def update_inputs():
    return

def start_interactive_console():
    global Scheduler
    console = code.InteractiveConsole(locals=dict(globals(), **locals()))
    console.interact()
    _G.logger.info("Shutting down")
    _G.FlagRunning = False

def main_loop():
    global Scheduler
    update_inputs()
    try:
        Scheduler.update()
    except Exception as e:
        _G.logger.error(f"Scheduler aborted with unhandled exception!")
        utils.handle_exception(e)

def queue_jobs():
    global Scheduler
    jobs = (
        LoginJob(),
        TrudysSurpriseJob(),
        GiantJellyJob(),
        GiantOmeletteJob(),
        TombolaJob(),
        TDMBGPOPJob(),
    )
    for job in jobs:
        Scheduler.queue_job(job, False)
    Scheduler.load_status('.')

def main():
    global Scheduler
    pw = sync_playwright().start()
    context = create_context(pw, 1)
    Scheduler = JobScheduler(pw, context)
    queue_jobs()
    Scheduler.start()
    th = Thread(target=start_interactive_console)
    th.start()
    try:
        while _G.FlagRunning:
            _G.wait(_G.FPS*2)
            main_loop()
    except (KeyboardInterrupt, SystemExit):
        _G.logger.info("Exiting...")
        Scheduler.terminate()
        th.join()

if __name__ == '__main__':
    main()
