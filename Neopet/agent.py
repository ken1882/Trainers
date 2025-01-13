import requests
import os
from bs4 import BeautifulSoup as BS
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

Agent = requests.Session()
Agent.headers.update({
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "priority": "u=0, i",
    "referer": "https://www.jellyneo.net/",
    "sec-ch-ua": '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "cross-site",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
})

with open('.cookie', 'r') as fp:
    lines = fp.read().split(';')
    for line in lines:
        k, v = line.split('=', 1)
        Agent.cookies.set(k.strip(), v)

# res = Agent.get('https://www.neopets.com/objects.phtml?type=shop&obj_type=56')
# with open('.tmp/shop.html', 'w', encoding='utf8') as fp:
#     fp.write(res.text)

def start_driver(url='https://www.neopets.com', visible=True):
    options = Options()
    options.headless = not visible

    driver = webdriver.Firefox(options=options)
    driver.get(url)

    return driver
