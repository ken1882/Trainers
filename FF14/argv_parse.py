from argparse import ArgumentParser
from datetime import datetime, timedelta
import _G

parser = ArgumentParser()
parser.add_argument("job",nargs='?')
parser.add_argument("-n", '--repeats', help='Repeat times')
parser.add_argument("-g", '--gather-target')
parser.add_argument("-d", '--crafting-delta')
parser.add_argument("-c", '--crafting-cp')
parser.add_argument('--crafting-sequence')
parser.add_argument('--patience-fishing')
parser.add_argument('--enable-rotation', action='store_true')
parser.add_argument('--ttl', type=int, help="Terminate worker after N minutes")

def load():
  args = parser.parse_args()
  _G.ARGV = args
  if args.ttl: 
    _G.WORKER_TTL = datetime.now() + timedelta(minutes=args.ttl)
  return args