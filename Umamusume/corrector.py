import _G,util
from _G import log_info

DateYear  = ['ジュニア級','クラシック級','シニア級', 'ファイナルズ']
DateMonth = [
  'デビュー前',
  '1月前', '1月後', '2月前', '2月後', '3月前', '3月後', 
  '4月前', '4月後', '5月前', '5月後', '6月前', '6月後', 
  '7月前', '7月後', '8月前', '8月後', 
  '9月前', '9月後', '10月前', '10月後', '11月前', '11月後', '12月前', '12月後',
  '開催中'
]

def skill_name(name,cost=0):
  max_r = 0.1
  ret = name
  for sk in _G.UmaSkillData:
    rate = util.diff_string(name, sk['Name'])
    if 'Cost' in sk and cost > sk['Cost']:
      continue
    if rate > max_r:
      ret = sk['Name']
      max_r = rate
  log_info(f'`{name}` => `{ret}`')
  return ret

def date(ori, log=True):
  try:
    year, month = ori.split('級')
  except ValueError:
    year, month = ori.split(' ')
  yrate = [util.diff_string(year, y) for y in DateYear]
  year  = DateYear[yrate.index(max(yrate))]
  month = month.translate(str.maketrans('符','後')).strip()
  mrate = [util.diff_string(month, m) for m in DateMonth]
  month = DateMonth[mrate.index(max(mrate))]
  if log:
    log_info(f'`{ori}` => `{year} {month}`')
  return DateYear.index(year)*24 + DateMonth.index(month)

def readable_date(datn):
  year  = DateYear[datn // 24]
  month = DateMonth[datn % 24]
  return f"{year} {month}"

def skill_cost(cost):
  ret = util.str2int(cost)
  if not ret:
    print(f"[Warning] Unable to ocr a skill cost of {cost} from {ret}")
    return 9999
  if ret > 400:
    return ret % 100
  return ret