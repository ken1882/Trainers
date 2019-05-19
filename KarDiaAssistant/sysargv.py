import sys, const, G, argparse

Version_str = "Current version: {}".format(const.Version)

Ptrue  = "store_true"
Pfalse = "store_false"
parser = argparse.ArgumentParser()
parser.add_argument("-v", "--version", help="Output current version", action='version', version=Version_str)
parser.add_argument("--verbose", help="Output all debug information", action=Ptrue)
parser.add_argument("--debug", help="Output debug information, add `--verbose` to output all infos", action=Ptrue)
parser.add_argument("-m", "--mode", help="Set mode", type=int, default=0)
parser.add_argument("-c", "--control", help="Manually control program update progress", action=Ptrue)
parser.add_argument("-d", "--difficulty", help="Set level difficulty", type=int, default=0)
parser.add_argument("-t", "--test", help="test program, using `-m` to set which mode to testing", action=Ptrue)
parser.add_argument("-a", "--align", help="Align window to (0,0)", action=Ptrue)
parser.add_argument("--slime", help="Set the mode to 1(auto-play slime minigame)", action=Ptrue)
parser.add_argument("--straw", help="Set the mode to 2(auto-play running away from scarecrow minigame)", action=Ptrue)
parser.add_argument("--unrestricted", help="Play the mini game until game over", action=Pfalse, default=True)
parser.add_argument("-r", "--repeat", help="Repeat playing same mini game until out of token", action=Ptrue, default=False)

def load_mode(args):
  if args.slime:
    G.Mode = 1
  elif args.straw:
    G.Mode = 2

def load():
  args = parser.parse_args()
  G.Mode = args.mode
  G.Difficulty = args.difficulty
  G.FlagDebug  = args.debug
  G.FlagVerbose = args.verbose
  G.FlagManualControl = args.control
  G.FlagTest = args.test 
  G.FlagAlign = args.align
  G.FlagRestricted = args.unrestricted
  G.FlagRepeat = args.repeat
  load_mode(args)
  setup()

def setup():
  if G.Mode == 1:
    G.InternUpdateTime = 60
  elif G.Mode == 2:
    G.InternUpdateTime = 1
    G.ScreenTimeout = 50

def show_help():
  parser.print_help()