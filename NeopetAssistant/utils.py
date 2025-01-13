import _G
import traceback
from datetime import datetime
import pytz, tzlocal

def handle_exception(err, errinfo=None):
    if not errinfo:
        errinfo = traceback.format_exc()
    _G.logger.error(f"An error occured during runtime!\n{str(err)}\n{errinfo}")

def pst2localt(pst: datetime):
    '''
    Convert PST to local time.
    '''
    pst_tz = pytz.timezone('US/Pacific')
    local_tz = tzlocal.get_localzone()
    pst = pst_tz.localize(pst)
    local_time = pst.astimezone(local_tz)
    return local_time

nst2localt = pst2localt # Neopets server time is in PST