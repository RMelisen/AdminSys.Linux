from .utils import read_config_file
from .commands import clone_vm, destroy_vm, start_vm, shutdown_vm, set_ram, set_lan


def clone_vms(filename, diskPath):
    vms = read_config_file(filename)
    for vm in vms:
        clone_vm(vm['name'], vm['flavour'], diskPath)
        set_ram(vm['name'], vm['ram'])
        set_lan(vm['name'], vm['lan'])
        start_vm(vm['name'])


def destroy_vms(filename):
    vms = read_config_file(filename)
    for vm in vms:
        destroy_vm(vm['name'])


def start_vms(filename):
    vms = read_config_file(filename)
    for vm in vms:
        start_vm(vm['name'])


def stop_vms(filename):
    vms = read_config_file(filename)
    for vm in vms:
        shutdown_vm(vm['name'])
