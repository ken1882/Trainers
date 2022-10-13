from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', help='Repeat times')
parser.add_argument("-t", '--target', help='Battle target stage')

def load():
  args = parser.parse_args()
  _G.ARGV = args
  return args