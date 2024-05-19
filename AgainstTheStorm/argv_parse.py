from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', type=int, help='Repeat times')
parser.add_argument("-s", '--stage', help='Stage name to fight')
parser.add_argument("-i", '--index', default=0, type=int, help='Index, job-specific argument')
parser.add_argument("-j", '--jndex', default=0, type=int, help='Secondary index, job-specific argument')
parser.add_argument("-w", '--wait', default=60, type=int, help='Wait duration between fights in seconds')
parser.add_argument("-b", '--battle-swap', action='store_true', default=False, help='Swap fleet battle boss/minion')
parser.add_argument("-t", '--team-swap', action='store_true', default=False, help='Swap fleet team each battle')
parser.add_argument('--no-enhance', action='store_true', default=False, help='Disable enhance after battles')

def load():
  args = parser.parse_args()
  _G.ARGV = args
  return args