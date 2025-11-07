from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', type=int, help='Repeat times')
parser.add_argument("-i", '--index', default=0, type=int, help='Index, job-specific argument')
parser.add_argument("-j", '--jndex', default=0, type=int, help='Secondary index, job-specific argument')
parser.add_argument("-l", '--letter', default=False, action='store_true')
parser.add_argument("-m", '--move', default=False, action='store_true')
parser.add_argument("-t", '--timeout', type=int, default=0)

def load():
  args = parser.parse_args()
  _G.ARGV = args
  return args