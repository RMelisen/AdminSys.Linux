# kvm/__init__.py

from .manager import clone_vms, destroy_vms, start_vms, stop_vms

# This allows you to do:
# from kvm import start_vm, stop_vm
