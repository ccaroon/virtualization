import os
import platform

ROOT_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")


def arch():
    """
    Standardize architecture names to the generic names
    """
    arch = platform.machine()
    if arch == "arm64":
        arch = "aarch64"
    elif arch == "amd64":
        arch = "x86_64"

    return arch


def host():
    """
    Calculate System Type & Arch

    Output: SYSTEM-ARCH. Ex: Linux-x86_64
    """
    return (f"{platform.system()}-{arch()}")


def qemu_specs():
    # QEMU System / Arch Specifics

    specs = {
        "accel": None,
        "bios": {
            "code": None,
            "vars": None
        },
        "machine": None,
        "net_device": None
    }

    if host() == "Linux-x86_64":
        specs["accel"] = "kvm"
        specs["bios"] = {
            "code": "/usr/share/qemu/OVMF.fd",
            "vars": "/usr/share/OVMF/OVMF_VARS_4M.fd"
        }
        specs["machine"] = f"pc"
        specs["net_device"] = "e1000"
    elif host().startswith("Darwin-"):
        specs["accel"] = "hvf"
        specs["bios"] = {
            "code": f"/opt/homebrew/opt/qemu/share/qemu/edk2-{arch()}-code.fd",
            "vars": "/opt/homebrew/opt/qemu/share/qemu/edk2-arm-vars.fd"
        }
        specs["machine"] = f"virt,highmem=on"
        specs["net_device"] = "virtio-net-device"

    return specs

def read_file(path):
    """
    Wrapper around read the contents of a file
    """
    contents = None
    with open(path, "r") as fptr:
        contents = fptr.read()
    return contents


def write_file(path, contents):
    """
    Wrapper around writing some content to a file
    """
    with open(path, "w") as fptr:
        fptr.write(contents.strip())
