from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("profile_name", nargs='?', default='default')
parser.add_argument("--proxy", default=None)
parser.add_argument("--debug", action='store_true', default=False)

def load():
  args = parser.parse_args()
  _G.ARGV = args
  return args