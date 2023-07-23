from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument('-v', '--verbose', action='store_true', help="Debug output")
parser.add_argument('-a', '--auxiliary', action='store_true', help="Auxiliary mode")
parser.add_argument('-n', '--repeats', nargs='?', type=int, help="Times for specified job to repeat")

def load():
  args = parser.parse_args()
  if args.verbose:
    _G.VerboseLevel = 4
  _G.ConsoleArgv = args
  return args