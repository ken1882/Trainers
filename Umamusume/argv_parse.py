from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument('-u', '--uma', nargs='?', help='Specified Umamusume for training')
parser.add_argument('-i', '--ignore-stats', action='store_true', help='Ignore stats when determine race')
parser.add_argument('-m', '--skill-pt-mul', type=float, help='Multiplier to min/max points to get skills')
parser.add_argument("-n", '--repeats', help='Repeat times')

def load():
  args = parser.parse_args()
  _G.ARGV = args
  
  if args.ignore_stats:
    _G.IgnoreStatLimit = True
    _G.log_info("Ignore stats when determine races")

  if args.skill_pt_mul:
    _G.MinGetSkillPoints *= args.skill_pt_mul
    _G.MaxGetSkillPoints *= args.skill_pt_mul
    _G.MinGetSkillPoints = int(_G.MinGetSkillPoints)
    _G.MaxGetSkillPoints = int(_G.MaxGetSkillPoints)
    _G.log_info("Skill min/max pts: ", _G.MinGetSkillPoints, _G.MaxGetSkillPoints)
  return args