import _G, utils
import re
import os
from bs4 import BeautifulSoup as BS
from datetime import datetime, timedelta
from threading import Thread, Lock
from urllib.parse import quote
import json
import requests

HTTP_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

WORKER_COUNT = 20
DB_LOCK = Lock()
WorkerThreads = []
WorkerFlags   = [False] * WORKER_COUNT

Agent = requests.Session()
Agent.headers.update(HTTP_HEADERS)

AgentPool = []
for i in range(WORKER_COUNT):
    AgentPool.append(requests.Session())
    AgentPool[-1].headers.update(HTTP_HEADERS)

CACHE_FILE = "cache/items.json"
CACHE_TTL  = 60*60*24*3

Database = {}

if os.path.exists(CACHE_FILE):
    try:
        with open(CACHE_FILE, 'r') as f:
            Database = json.loads(f.read())
    except Exception as e:
        utils.handle_exception(e)
        _G.log_warning("Failed to load jellyneo item cache file")

def get_item_details_by_name(item_name, full_price_history=False, forced=False, agent=None):
    item_name = item_name.lower()
    global Database, Agent
    if not agent:
        agent = Agent
    if not forced and item_name.lower() in Database:
        ret = Database[item_name]
        if ret['rarity'] > 300: # cash item
            return ret
        if (datetime.now() - datetime.fromtimestamp(Database[item_name.lower()]["price_timestamp"])).total_seconds() < CACHE_TTL:
            return ret
    _G.log_info(f"Getting item details for {item_name}")
    ret = {
        "id": "",
        "name": "",
        "price": 0,
        "restock_price": 0,
        "price_timestamp": datetime(1999, 11, 15).timestamp(),
        "recent_prices": [],
        "price_dates": [],
        "rarity": 0,
        "category": "",
        "image": "",
        "restock_shop_link": "",
        "effects": [],
    }
    item_name = quote(item_name)
    url = f"https://items.jellyneo.net/search?name={item_name}&name_type=3"
    response = agent.get(url)
    page = BS(response.content, "html.parser")
    try:
        reg = re.search(r"items\.jellyneo\.net\/item\/(\d+)", str(page))
        ret["id"] = reg.group(1)
        link = f"https://{reg.group()}"
    except Exception as e:
        utils.handle_exception(e)
        return ret
    try:
        pn = page.select('.price-history-link')[0]
        ret["price"] = utils.str2int(pn.text)
        ret["price_timestamp"] = datetime.strptime(pn.attrs['title'], "%B %d, %Y").timestamp()
    except Exception:
        _G.log_warning(f"Failed to get price for {item_name}, probably cash item or heavily inflated")
        ret["price"] = 10**10
        ret["price_timestamp"] = datetime.now().timestamp()
    res = agent.get(link)
    doc = BS(res.content, "html.parser")
    try:
        ret["name"] = doc.select('h1')[0].text.strip()
        ul = doc.select('.small-block-grid-2')[0]
        grids = ul.select('.text-center')
        ret["rarity"] = utils.str2int(grids[0].text.strip())
        ret["category"] = grids[1].text.strip()
        ret["restock_price"] = utils.str2int(grids[2].text.strip())
        ret["image"] = grids[-1].select('a')[0]['href']
    except Exception as e:
        utils.handle_exception(e)
        return ret
    try:
        rows = doc.select('.special-categories-row')
        effect_row_started = False
        for row in rows:
            if row.text.strip().lower() == 'effects':
                effect_row_started = True
                continue
            if not effect_row_started:
                continue
            try:
                ret["effects"].append(row.select('.special-categories-title')[0].text.strip().lower())
            except Exception as e:
                pass
    except Exception as e:
        utils.handle_exception(e)
        return ret
    save_cache(ret)
    return ret

def save_cache(item=None, padding=True):
    global Database, DB_LOCK
    with DB_LOCK:
        if item:
            Database[item["name"].lower()] = item
        with open(CACHE_FILE, 'w') as f:
            if padding:
                json.dump(Database, f, indent=4)
            else:
                json.dump(Database, f)

def batch_search_worker(items, ret, worker_id):
    global AgentPool, Database, WorkerFlags
    _G.logger.info(f"Worker#{worker_id} started: {items}")
    try:
        for item in items:
            ret_idx = next((i for i, x in enumerate(ret) if x["name"] == item), 0)
            if item.lower() in Database:
                ret[ret_idx] = Database[item.lower()]
            else:
                ret[ret_idx] = get_item_details_by_name(item, agent=AgentPool[worker_id])
    finally:
        WorkerFlags[worker_id] = False
        _G.logger.info(f"Worker#{worker_id} finished: {items}")

def is_busy():
    global WorkerFlags
    return any(WorkerFlags)

def batch_search(items, join=True):
    '''
    Multi-threaded batch search for item details. Note that if `join=False`,
    the function will return immediately and you'll need to fetch the results later using  `is_busy()`.
    '''
    global Database, WorkerThreads, WorkerFlags
    if is_busy():
        _G.log_warning("Search workers are busy")
        return None
    ret = [{'name': item} for item in items]
    thread_args = [[] for _ in range(WORKER_COUNT)]
    for i, item in enumerate(items):
        thread_args[i % WORKER_COUNT].append(item)
    for i in range(WORKER_COUNT):
        if thread_args[i]:
            WorkerThreads.append(Thread(target=batch_search_worker, args=(thread_args[i], ret, i)))
            WorkerFlags[i] = True
            WorkerThreads[-1].start()
    if join:
        for t in WorkerThreads:
            t.join()
    return ret

def update_item_price(item, price):
    global Database
    _G.log_info(f"Updating price for {item} to {price}")
    item = item.lower()
    if item in Database:
        Database[item]["price"] = price
        Database[item]["price_timestamp"] = datetime.now().timestamp()
        save_cache()
        return True
    else:
        item = get_item_details_by_name(item)
        if item:
            item["price"] = price
            item["price_timestamp"] = datetime.now().timestamp()
            save_cache(item)
            return True
    return False
