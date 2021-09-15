from argparse import ArgumentParser
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')

def load():
  args = parser.parse_args()
  return args