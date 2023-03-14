from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', help='Repeat times')
parser.add_argument("-t", '--target', help='Battle target stage')
parser.add_argument("-v", '--verbose', action='store_true', help='Verbose output')

def load():
  args = parser.parse_args()
  if args.verbose:
    _G.VerboseLevel = 4
  
  _G.ARGV = args
  return args