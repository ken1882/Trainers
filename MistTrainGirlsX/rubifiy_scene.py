from glob import glob
import requests
import urllib.parse
import json
import os

from requests.api import request

MaruHeaders = {
  'Accept-Encoding': 'gzip, deflate, br',
  'Accept': 'text/plain, */*; q=0.01',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Host': 'www.jpmarumaru.com',
  'Origin': 'https://www.jpmarumaru.com',
  'Referer': 'https://www.jpmarumaru.com/tw/toolKanjiFurigana.asp'
}

LinewrapSymbol = '＊'
CommonTitleCache = {}
SceneMeta = {}
for obj in requests.get('https://assets3.mist-train-girls.com/production-client-web-static/MasterData/MSceneViewModel.json').json():
  SceneMeta[obj['Id']] = obj

###

def rubifiy_japanese(text):
  res = requests.post(
    "https://www.jpmarumaru.com/tw/api/json_KanjiFurigana.asp",
    'Text='+urllib.parse.quote_plus(text),
    headers=MaruHeaders
  )
  print(res.content.decode())
  return res.content.decode()

def rubifiy_file(file):
  with open(file, 'r') as fp:
    data = json.load(fp)
    if 'r' in data:
      data = data['r']
  if type(data) == list:
    data = data[0]
  id = data['MSceneId']
  dst = f'scenes_ruby/{id}.json'
  if os.path.exists(dst):
    print(f"'{dst}' already exists, skip")
    return
  dialogs = sorted(data['MSceneDetailViewModel'], key=lambda x:x['GroupOrder']+x['ViewOrder']*0.01)
  for i,dia in enumerate(dialogs):
    text = dia['Phrase']
    text = text.replace('\\n', LinewrapSymbol)
    text = text.replace('\u3000', '')
    ruby = rubifiy_japanese(text)
    ruby = ruby.replace(
      '<ruby><rb>一</rb><rt>いち</rt></ruby><ruby><rb>人</rb><rt>にん</rt></ruby>',
      '<ruby><rb>一人</rb><rt>ひとり</rt></ruby>',
    )
    ruby = ruby.replace(
      '<ruby><rb>二</rb><rt>に</rt></ruby><ruby><rb>人</rb><rt>にん</rt></ruby>',
      '<ruby><rb>二人</rb><rt>ふたり</rt></ruby>',
    )
    ruby = ruby.replace(
      '<ruby><rb>幻</rb><rt>まぼろし</rt></ruby><ruby><rb>霧</rb><rt>きり</rt></ruby>',
      '<ruby><rb>幻</rb><rt>げん</rt></ruby><ruby><rb>霧</rb><rt>む</rt></ruby>'
    )
    dialogs[i]['Ruby'] = ruby
  data['MSceneDetailViewModel'] = dialogs
  # Title
  t = SceneMeta[id]['Title']
  if t in CommonTitleCache:
    data['Title'] = CommonTitleCache[t]
  else:
    data['Title'] = rubifiy_japanese(t)
    CommonTitleCache[t] = data['Title']
  with open(dst, 'w') as fp:
    json.dump(data, fp)

### 

files = glob('scenes/*.json')
for file in files:
  print("Processing", file)
  try:
    rubifiy_file(file)
  except Exception as err:
    print(f"An error occurred during processing '{file}'\n", err)