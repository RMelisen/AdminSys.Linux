import re
import subprocess
import os


def read_config_file(filename: str):
    with open(filename) as f:
        vms = []
        vms_config = []
        for lines in f:
            line = lines.rstrip()
            if not re.search('^#', line) and not re.search('^$', line):
                vms.append(line)
        for vm in vms:
            details = create_vm_object(vm)
            vms_config.append(details)
        return vms_config


def create_vm_object(vm: str):
    vm_details = vm.split("|")
    return {
        "name": vm_details[0],
        "flavour": vm_details[1],
        "ram": vm_details[2],
        "lan": vm_details[3]
    }


def run_and_ignore_stderr(cmd):
    try:
        with open(os.devnull, 'w') as devnull:
            subprocess.check_call(cmd, stderr=devnull)
    except subprocess.CalledProcessError:
        return
