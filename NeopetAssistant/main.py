import _G
import utils
import os
import page_action as action
from playwright.sync_api import sync_playwright
from scheduler import JobScheduler
from console import NeoConsole
from datetime import datetime, timedelta
from jobs.login import LoginJob
from jobs.trudys_surprise import TrudysSurpriseJob
from jobs.giant_jelly import GiantJellyJob
from jobs.giant_omelette import GiantOmeletteJob
from jobs.tdmbgpop import TDMBGPOPJob
from jobs.tombola import TombolaJob
from jobs.coltzan_shrine import ColtzanShrineJob
from jobs.fishing import FishingJob
from jobs.rich_slorg import RichSlorgJob
from jobs.monthly_freebies import MonthlyFreebiesJob
from jobs.healing_springs import HealingSpringsJob
from jobs.anchor_management import AnchorManagementJob
from jobs.fruit_machine import FruitMachineJob
from jobs.qasalan_expellibox import QasalanExpelliboxJob
from jobs.game_room import GameRoomJob

Scheduler = None

def create_context(pw, id, enable_extensions=True):
    _G.log_info(f"Creating browser context#{id}")
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--disable-features=IsolateOrigins,site-per-process',
        '--auto-open-devtools-for-tabs',
    ]
    if enable_extensions:
        args.append(f"--disable-extensions-except={os.getenv('BROWSER_EXTENSION_PATHS')}")
        args.append(f"--load-extension={os.getenv('BROWSER_EXTENSION_PATHS')}")
    _G.log_info(f"Launching browser context#{id} with args: {args}")
    return pw.chromium.launch_persistent_context(
        "{}/profile_{:04d}".format(_G.BROWSER_PROFILE_DIR, id),
        headless=False,
        handle_sigint=False,
        color_scheme='dark',
        args=args
    )

def main_loop():
    global Scheduler
    try:
        Scheduler.update()
    except Exception as e:
        _G.log_error(f"Scheduler aborted with unhandled exception!")
        utils.handle_exception(e)

def queue_jobs():
    global Scheduler
    jobs = (
        LoginJob(),
        MonthlyFreebiesJob(),
        TrudysSurpriseJob(),
        GiantJellyJob(),
        GiantOmeletteJob(),
        TombolaJob(),
        TDMBGPOPJob(),
        ColtzanShrineJob(),
        FishingJob(),
        RichSlorgJob(),
        HealingSpringsJob(),
        AnchorManagementJob(),
        FruitMachineJob(),
        QasalanExpelliboxJob(),
        GameRoomJob(),
    )
    for job in jobs:
        Scheduler.queue_job(job, False)
    Scheduler.load_status(_G.BROWSER_PROFILE_DIR)

def main():
    global Scheduler
    last_tick_time = datetime.now()
    pw = sync_playwright().start()
    context = create_context(pw, 1)
    Scheduler = JobScheduler(pw, context, save_path=_G.BROWSER_PROFILE_DIR)
    queue_jobs()
    _G.Console = NeoConsole(globals=globals(), locals=locals())
    Scheduler.start()
    try:
        while _G.FlagRunning:
            _G.Console.update()
            if (datetime.now() - last_tick_time).total_seconds() >= _G.FPS:
                main_loop()
                last_tick_time = datetime.now()
    except (KeyboardInterrupt, SystemExit):
        _G.log_info("Exiting...")
        Scheduler.terminate()

if __name__ == '__main__':
    main()
