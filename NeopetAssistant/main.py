import _G
import utils
import os
import json
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
from jobs.daily_quest_touch import DailyQuestTouchJob
from jobs.daily_puzzle import DailyPuzzleJob
from jobs.stock_market import StockMarketJob
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
from jobs.pet_cares import PetCaresJob
from jobs.quick_restock import QuickRestockJob
from jobs.restocking import RestockingJob
from jobs.potato_counter import PotatoCounterJob
from jobs.market_price import MarketPriceJob
from jobs.scratchcards import ScratchcardsJob

Scheduler = None

def create_context(pw, profile_name, enable_extensions=True):
    _G.log_info(f"Creating browser context#{profile_name}")
    args = [
        '--disable-blink-features=AutomationControlled',
        '--disable-infobars',
        '--disable-features=IsolateOrigins,site-per-process',
    ]
    if _G.ARGV.debug:
        args.append('--auto-open-devtools-for-tabs')
    if enable_extensions:
        bases = os.getenv('BROWSER_EXTENSION_PATHS') or ''
        ext_paths = []
        for path in bases.split(','):
            if not path:
                continue
            path.replace('\\', '/')
            version = utils.str2int(path.split('/')[-1])
            if not version:
                versions = os.listdir(path)
                latest = max(versions, key=lambda x: utils.str2int(x))
                path = os.path.join(path, latest)
            if not os.path.exists(path):
                _G.log_warning(f"Extension path not found: {path}")
                continue
            with open(os.path.join(path, 'manifest.json'), 'r') as f:
                manifest = json.load(f)
                _G.log_info(f"Loading extension: {manifest['name']} {manifest['version']}")
                ext_paths.append(path)
            ext_paths.append(path)
        args.append(f"--disable-extensions-except={','.join(ext_paths)}")
        args.append(f"--load-extension={','.join(ext_paths)}")
    _G.log_info(f"Launching browser context#{profile_name} with args: {args}")
    kwargs = {
        'headless': False,
        'handle_sigint': False,
        'color_scheme': 'dark',
        'args': args
    }
    ch = os.getenv('DRIVER_CHANNEL')
    if ch:
        kwargs['channel'] = ch
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
        DailyQuestTouchJob(),
        DailyQuestJob(),
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
        PetCaresJob(),
        StockMarketJob(),
        QuickRestockJob(),
        PotatoCounterJob(),
        RestockingJob(scheduler=Scheduler),
        MarketPriceJob(),
        ScratchcardsJob(),
    )
    for job in jobs:
        Scheduler.queue_job(job, False)
    Scheduler.load_status(_G.BROWSER_PROFILE_DIR)
    # always check login first
    login_job = Scheduler.get_job("login")
    login_job.calc_next_run('now')

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
