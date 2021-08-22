from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument('-n', '--ntimes', nargs='?', help="Times for specified job to repeat")

def load():
  args = parser.parse_args()
  _G.ConsoleArgv = args
  return args