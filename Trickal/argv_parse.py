from argparse import ArgumentParser
from datetime import datetime, timedelta
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', help='Repeat times')

def load():
  args = parser.parse_args()
  _G.ARGV = args
  return args