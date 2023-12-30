raw='''
'''
import re

def transcode():
    for line in raw.split('\n'):
        res = re.search(r"t\.(.+)\s=\s", line)
        if not res:
            continue
        fname = res.groups()[0]
        if 'function' in line:
            print(f"('{fname}', list, (\n\n)),")
        else:
            print(f"'{fname}',")
