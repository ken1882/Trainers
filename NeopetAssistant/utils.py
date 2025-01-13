import _G
import traceback

def handle_exception(err, errinfo=None):
    if not errinfo:
        errinfo = traceback.format_exc()
    _G.logger.error(f"An error occured during runtime!\n{str(err)}\n{errinfo}")