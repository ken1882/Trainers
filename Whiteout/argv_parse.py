from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument('job',nargs='?')
parser.add_argument('-n', '--repeats', help='Repeat times')
parser.add_argument(
  '-f', '--find-foreground', 
  action='store_true',
  help='Find window by manual switch to foreground, will detect 2 seconds later'
)
parser.add_argument('--train-interval', type=int, help="Interval between troop training in minutes")
parser.add_argument('-m', '--max-troop-count', type=int, help="How many troops can be dispatched (or march)")
parser.add_argument('-g', '--gather-level', type=int, help="Target resource node level when gathering")
parser.add_argument('--min-gather-level', type=int, help="Min target resource node level when gathering")

def load():
  args = parser.parse_args()
  args.max_troop_count = max(args.max_troop_count or 0, 1)
  if not args.min_gather_level:
    args.min_gather_level = 5
  _G.ARGV = args
  return args