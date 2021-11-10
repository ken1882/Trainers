from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument('-u', '--uma', nargs='?', help='Specified Umamusume for training')
parser.add_argument('-i', '--ignore-stats', action='store_true', help='Ignore stats when determine race')

def load():
  args = parser.parse_args()
  if args.ignore_stats:
    _G.IgnoreStatLimit = True
    _G.log_info("Ignore stats when determine races")
  return args