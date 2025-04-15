from .utils import run_and_ignore_stderr


def clone_vm(name: str, vmToClone: str, diskPath: str):
    print(f"Cloning [{vmToClone}]")
    cmd = [
        'virt-clone',
        '--original', vmToClone,
        '--name', name,
        '--file', f"{diskPath}{name}.qcow2"
    ]
    run_and_ignore_stderr(cmd)


def start_vm(name: str):
    cmd = ['virsh', 'start', name]
    run_and_ignore_stderr(cmd)


def shutdown_vm(name: str):
    cmd = ['virsh', 'shutdown', name]
    run_and_ignore_stderr(cmd)


def stop_vm(name: str):
    cmd = ['virsh', 'destroy', name]
    run_and_ignore_stderr(cmd)


def destroy_vm(name: str):
    stop_vm(name)
    cmd = ['virsh', 'undefine', name, '--remove-all-storage']
    run_and_ignore_stderr(cmd)


def set_ram(name: str, ram: str):
    cmd = ['virsh', 'setmaxmem', name, ram, '--config']
    run_and_ignore_stderr(cmd)
    cmd = ['virsh', 'setmem', name, ram, '--config']
    run_and_ignore_stderr(cmd)


def set_lan(name: str, lan: str):
    cmd = ['virsh', 'detach-interface', name, 'network', '--persistent']
    run_and_ignore_stderr(cmd)
    cmd = ['virsh', 'attach-interface', name, "network", lan, '--model', 'virtio', '--persistent']
    run_and_ignore_stderr(cmd)
