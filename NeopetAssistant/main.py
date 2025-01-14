import _G
import utils
import os
from playwright.sync_api import sync_playwright
from scheduler import JobScheduler
from jobs.login import LoginJob
from jobs.trudys_surprise import TrudysSurpriseJob

KEYBOARD_ENABLED = False
if os.geteuid() == 0:
    import keyboard
    KEYBOARD_ENABLED = True

Scheduler = None
EventThread = None

def create_context(pw, id):
    _G.logger.info(f"Creating browser context#{id}")
    args = []
    _G.logger.info(f"Launching browser context#{id} with args: {args}")
    return pw.chromium.launch_persistent_context(
        "./profile_{:04d}".format(id),
        headless=False,
        handle_sigint=False,
        channel='msedge',
        args=args
    )

def update_inputs():
    if not KEYBOARD_ENABLED:
        return
    if keyboard.is_pressed('q'):
        exit(0)

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
        # LoginJob(email=os.getenv('NEO_EMAIL'), password=os.getenv('NEO_PASSWORD')),
        TrudysSurpriseJob(),
    )
    for job in jobs:
        Scheduler.queue_job(job, False)

def main():
    global Scheduler
    pw = sync_playwright().start()
    context = create_context(pw, 1)
    Scheduler = JobScheduler(pw, context)
    queue_jobs()
    Scheduler.start()
    try:
        while True:
            _G.wait(_G.FPS*2)
            main_loop()
    except (KeyboardInterrupt, SystemExit):
        _G.logger.info("Exiting...")
        Scheduler.stop()

if __name__ == '__main__':
    main()
