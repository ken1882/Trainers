import sys, const, G, argparse

Version_str = "Current version: {}".format(const.Version)

Ptrue  = "store_true"
Pfalse = "store_false"
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", help="Output current version", action='version', version=Version_str)
parser.add_argument("--verbose", help="Output all debug information", action=Ptrue)
parser.add_argument("--debug", help="Output debug information, add `--verbose` to output all infos", action=Ptrue)
parser.add_argument("-m", "--mode", help="Set mode", type=int, default=0)
parser.add_argument("-t", "--test", help=argparse.SUPPRESS, action=Ptrue)
parser.add_argument("-a", "--align", help="Align window to (0,0)", action=Ptrue)
parser.add_argument("-b", "--backup", help="Auto run backup(Logistic Support)", action=Ptrue)
parser.add_argument("-l", "--like", help="Auto press like to friends", action=Ptrue)
parser.add_argument("-ac", "--autocombat", help="Once auto-combat ends, send the team again (Note if max T-dolls is reached this program will terminate)", action=Ptrue)

def load_mode(args):
  if args.backup:
    G.Mode = 1
  elif args.like:
    G.Mode = 2

def load():  
  args = parser.parse_args()
  G.Mode = args.mode
  G.FlagDebug  = args.debug
  G.FlagVerbose = args.verbose
  G.FlagTest = args.test 
  G.FlagAlign = args.align
  G.FlagAutoCombat = args.autocombat
  load_mode(args)
  G.setup()

def show_help():
  parser.print_help()