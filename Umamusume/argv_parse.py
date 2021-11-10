from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument('-u', '--uma', nargs='?', help='Specified Umamusume for training')
parser.add_argument('-m', '--skill-pt-mul', type=float, help='Multiplier to min/max points to get skills')

def load():
  args = parser.parse_args()

  if args.skill_pt_mul:
    _G.MinGetSkillPoints *= args.skill_pt_mul
    _G.MaxGetSkillPoints *= args.skill_pt_mul
  return args