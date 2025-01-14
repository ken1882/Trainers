import re
from bs4 import BeautifulSoup as BS
from datetime import datetime
import requests

HTTP_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
}

Agent = requests.Session()
Agent.headers.update(HTTP_HEADERS)


def get_item_details_by_name(item_name):
    ret = {
        "id": "",
        "name": "",
        "recent_prices": [],
        "price_dates": [],
        "rarity": 0,
        "category": "",
        "image": "",
        "restock_shop_link": "",
    }
    item_name = item_name.replace(" ", "+")
    url = f"https://items.jellyneo.net/search?name={item_name}&name_type=3"
    response = Agent.get(url)
    page = BS(response.content, "html.parser")
    try:
        reg = re.search(r"items\.jellyneo\.net\/item\/(\d+)", str(page))
        ret["id"] = reg.group(1)
        link = f"https://{reg.group()}"
    except Exception :
        return None
    response = Agent.get(link)
    page = BS(response.content, "html.parser")
