import _G
import utils
import os
import page_action as action
import argv_parse
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
from jobs.snowager import SnowagerJob
from jobs.daily_quest import DailyQuestJob
from jobs.daily_puzzle import DailyPuzzleJob
from jobs.forgotten_shore import ForgottenShoreJob
from jobs.apple_bobbing import AppleBobbingJob
from jobs.deserted_tomb import DesertedTombJob
from jobs.lunar_temple import LunarTempleJob
from jobs.negg_cave import NeggCaveJob
from jobs.bank_interest import BankInterestJob
from jobs.wise_king import WiseKingJob
from jobs.grumpy_king import GrumpyKingJob
from jobs.altador_council import AltadorCouncilJob
from jobs.faerie_crossword import FaerieCrosswordJob

Scheduler = None

def create_context(pw, profile_name, enable_extensions=True):
    _G.log_info(f"Creating browser context#{profile_name}")
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--disable-features=IsolateOrigins,site-per-process',
        '--auto-open-devtools-for-tabs',
    ]
    if enable_extensions:
        args.append(f"--disable-extensions-except={os.getenv('BROWSER_EXTENSION_PATHS')}")
        args.append(f"--load-extension={os.getenv('BROWSER_EXTENSION_PATHS')}")
    _G.log_info(f"Launching browser context#{profile_name} with args: {args}")
    kwargs = {
        'headless': False,
        'handle_sigint': False,
        'color_scheme': 'dark',
        'args': args
    }
    proxy = _G.ARGV.proxy
    if not proxy:
        proxy = os.getenv(f"PROFILE_PROXY_{profile_name.upper()}")
    if proxy:
        kwargs['proxy'] = {'server': proxy, 'bypass': 'neopass.neopets.com'}
        auth = os.getenv(f"PROFILE_PROXY_{profile_name.upper()}_AUTH")
        if auth:
            kwargs['proxy']['username'] = auth.split(':')[0]
            kwargs['proxy']['password'] = auth.split(':')[1]
    return pw.chromium.launch_persistent_context(
        f"{_G.BROWSER_PROFILE_DIR}/profile_{profile_name}",
        **kwargs
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
        DailyQuestJob(),
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
        SnowagerJob(),
        DailyPuzzleJob(),
        ForgottenShoreJob(),
        AppleBobbingJob(),
        DesertedTombJob(),
        LunarTempleJob(),
        NeggCaveJob(),
        BankInterestJob(),
        WiseKingJob(),
        GrumpyKingJob(),
        AltadorCouncilJob(),
        FaerieCrosswordJob(),
    )
    for job in jobs:
        Scheduler.queue_job(job, False)
    Scheduler.load_status(_G.BROWSER_PROFILE_DIR)

def main():
    global Scheduler
    last_tick_time = datetime.now()
    profile_name = _G.ARGV.profile_name
    pw = sync_playwright().start()
    context = create_context(pw, profile_name)
    Scheduler = JobScheduler(pw, context, profile_name, save_path=_G.BROWSER_PROFILE_DIR)
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
    argv_parse.load()
    main()
