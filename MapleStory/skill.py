from datetime import date, datetime,timedelta
import Input

class Skill:
  def __init__(self, name, cd, keycode):
    '''
    A Skill Struct

    - Arguments:
      - name: Skill name
      - cd: Cool down time of skill, in seconds
      - keycode: Corresponding MapleStory keycode linked to skill
    '''
    self.name    = name
    self.cd      = timedelta(seconds=cd)
    self.keycode = keycode
    self.last_used_time = 0
  
  def is_ready(self):
    return datetime.now() - self.last_used_time > self.cd

  def use(self):
    pass

Skill()