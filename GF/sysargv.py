import sys, const, G, argparse, util

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
parser.add_argument("-acc", "--autocombat-count", help="Auto-combat count, if hit to zero won't send again.", default=-1, type=int)
parser.add_argument("-ls", "--list-grind-levels", help="List available grindable levels", action=Ptrue)
parser.add_argument("-gl", "--grind-level", help="Grind level, notice that you should have pre-setup before excute this command", type=str, default='')
parser.add_argument("-fr", "--fast-repair", help="Use fast repair when grinding", action=Ptrue)
parser.add_argument("-swmg", "--swap-first-main-gunner", help="Swap first grinding main gunner", action=Ptrue)
parser.add_argument("-lgdy", "--level-grind-delay", help="Delay time in seconds before start level grind", type=int)

def load_mode(args):
  if args.backup:
    G.Mode = 1
  elif args.like:
    G.Mode = 2

  G.GrindLevel = G.GrindLevel.upper()
  try:
    if not const.EnterLevelPos[G.GrindLevel]:
      G.FlagGrindLevel = False
    else:
      G.FlagGrindLevel = True
  except Exception:
    G.FlagGrindLevel = False

def load():  
  args = parser.parse_args()
  if args.list_grind_levels:
    G.Mode = -1
    return list_grind_levels()
  G.Mode = args.mode
  G.FlagDebug  = args.debug
  G.FlagVerbose = args.verbose
  G.FlagTest = args.test 
  G.FlagAlign = args.align
  G.FlagAutoCombat = args.autocombat
  G.FlagFastRepair = args.fast_repair
  G.AutoCombatCount = args.autocombat_count
  G.GrindLevel = args.grind_level
  load_mode(args)
  print("Grind Level: ", G.FlagGrindLevel, G.GrindLevel)
  G.setup()

  if args.swap_first_main_gunner:
    G.LastMainGunner = 1
  if args.level_grind_delay:
    G.RepairOKTimestamp = util.get_current_time_sec() + args.level_grind_delay + 10

def show_help():
  parser.print_help()

def list_grind_levels():
  print("Available levels for grinding:")
  for k in const.TeamDeployPos:
    print(k.upper())