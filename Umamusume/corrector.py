import _G,util

DateYear  = ['ジュニア級','クラシック級','シニア級']
DateMonth = [
  'デビュー前',
  '1月前', '1月後', '2月前', '2月後', '3月前', '3月後', 
  '4月前', '4月後', '5月前', '5月後', '6月前', '6月後', 
  '7月前', '7月後', '8月前', '8月後', 
  '9月前', '9月後', '10月前', '10月後', '11月前', '11月後', '12月前', '12月後',
]

def skill_name(name):
  max_r = 0.1
  ret = name
  for sk in _G.UmaSkillData:
    rate = util.diff_string(name, sk['Name'])
    if rate > max_r:
      ret = sk['Name']
      max_r = rate
  return ret

def date(ori):
  ori = ori.split('級')
  year, month = 0, ''
  yrate = [util.diff_string(year, y) for y in DateYear]
  year  = DateYear[yrate.index(max(yrate))]
  ori[1] = ori[1].translate(str.maketrans('符','後')).strip()
  for m in DateMonth:
    if m in ori[1]:
      month = m
      break
  return year,month