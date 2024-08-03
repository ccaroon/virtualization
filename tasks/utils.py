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
    return (f"{platform.system()}-{arch()}")
