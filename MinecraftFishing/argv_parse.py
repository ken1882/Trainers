from argparse import ArgumentParser
from datetime import datetime, timedelta
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', help='Repeat times')
parser.add_argument('--ttl', type=int, help="Terminate worker after N minutes")

def load():
  args = parser.parse_args()
  _G.ARGV = args
  if args.ttl: 
    _G.WORKER_TTL = datetime.now() + timedelta(minutes=args.ttl)
  return args