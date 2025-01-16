import _G
import traceback
from datetime import datetime
import pytz, tzlocal
from difflib import SequenceMatcher

def handle_exception(err, errinfo=None):
    if not errinfo:
        errinfo = traceback.format_exc()
    _G.log_error(f"An error occured during runtime!\n{str(err)}\n{errinfo}")

def pst2localt(pst: datetime):
    pst_tz = pytz.timezone('US/Pacific')
    local_tz = tzlocal.get_localzone()
    pst = pst_tz.localize(pst)
    local_time = pst.astimezone(local_tz)
    return local_time

def localt2pst(localt: datetime):
    pst_tz = pytz.timezone('US/Pacific')
    local_tz = pytz.timezone(tzlocal.get_localzone().key)
    localt = local_tz.localize(localt)
    pst = localt.astimezone(pst_tz)
    return pst

# Neopets server time is in PST
nst2localt = pst2localt
localt2nst = localt2pst

def diff_string(a,b):
    return SequenceMatcher(None,a,b).ratio()

def str2int(ss):
    try:
        return int("".join([n for n in ss if n.isdigit()]))
    except ValueError:
        return None
