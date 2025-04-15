import os
from .text_colors import TColors


def check_script_parameters(args):
    if args.action not in ['clone', 'destroy', 'start', 'stop', 'inventory']:
        print(f'{TColors.FAIL}You must supply an -a (--action) [in clone|destroy|start|stop|inventory]{TColors.ENDC}')
        return False
    if not args.file:
        print(f'{TColors.FAIL}You must supply a valid -f (--file){TColors.ENDC}')
        return False
    if not os.path.isfile(args.file):
        print(f'{TColors.FAIL}The supplied file do not exists, please check the path{TColors.ENDC}')
        return False
    return True
