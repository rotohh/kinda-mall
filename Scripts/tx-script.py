#!E:\SaleOr\Scripts\python.exe
# EASY-INSTALL-ENTRY-SCRIPT: 'transifex-client==0.13.5','console_scripts','tx'
__requires__ = 'transifex-client==0.13.5'
import re
import sys
from pkg_resources import load_entry_point

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    sys.exit(
        load_entry_point('transifex-client==0.13.5', 'console_scripts', 'tx')()
    )
