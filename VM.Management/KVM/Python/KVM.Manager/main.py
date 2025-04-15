#!/usr/bin/python3

import argparse
import datetime
from KVM import clone_vms, destroy_vms, start_vms, stop_vms, manage_inventory
from Validation import check_script_parameters, TColors

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--action', choices=['clone', 'destroy', 'start', 'stop'], help='Action to perform: clone, destroy, start or stop')
    parser.add_argument('-f', '--file', type=str, help='A config file containing the list of VMs to work with')
    args = parser.parse_args()

    if check_script_parameters(args):
        start_time = datetime.datetime.now()
        if args.action == 'clone':
            clone_vms(args.file, "/home/rmeli/Documents/KVM/KVM/")  # Image disks folder
        elif args.action == 'destroy':
            destroy_vms(args.file)
        elif args.action == 'start':
            start_vms(args.file)
        elif args.action == 'stop':
            stop_vms(args.file)
        elif args.action == 'inventory':
            manage_inventory(args.file)
        stop_time = datetime.datetime.now()
        operation_time = stop_time - start_time
        print(f'{TColors.OKCYAN}The [{args.action}] took {str(operation_time)}s{TColors.ENDC}')
    else:
        parser.print_help()


main()
