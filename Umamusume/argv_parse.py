from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument('-u', '--uma', nargs='?', help='Specified Umamusume for training')

def load():
  args = parser.parse_args()
  return args