from argparse import ArgumentParser
from urllib import parse
import _G

parser = ArgumentParser()
parser.add_argument("token",nargs='?')
parser.add_argument("-n", '--repeats', help='Repeat times')
parser.add_argument('-s', '--star-brust-stream', action="store_true",help='もっと早く！\n[WARNING] Potential DOS the server, use at your own risk')
parser.add_argument('-a', '--auto-reauth', action="store_true", help='Attempt to re-auth the game if token is invalid')
parser.add_argument('--no-persist-cache', action="store_true", help='Disable some caches so data will be synced every time, program might run slower')
parser.add_argument('--user-agent', help="Use specified user agent instead of python request's")
parser.add_argument('-l', '--less', action="store_true", help='Less information logging')
parser.add_argument('-v', '--verbose', action="store_true", help='Debug verbose logging')
parser.add_argument('-o', '--output', help="Output combat statics to specified file")

def load():
  args = parser.parse_args()
  if args.verbose:
    _G.VerboseLevel = 4
  _G.ARGV = args
  return args