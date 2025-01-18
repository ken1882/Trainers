from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("profile_name", nargs='?', default='default')

def load():
  args = parser.parse_args()
  _G.ARGV = args
  return args