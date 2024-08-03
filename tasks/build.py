import os
import platform
import shutil
from invoke import task

import utils

TMP_DIR = f"{utils.ROOT_DIR}/tmp"
SEED_ROOT = f"{TMP_DIR}/seedconfig"
SEED_ISO = f"{TMP_DIR}/seed.iso"


@task
def seed_data(ctx, hostname="caroon-al2023"):
    """
    Create data files for a seed image.

    See: https://docs.aws.amazon.com/linux/al2023/ug/seed-iso.html
    """
    # 1. On a Linux or macOS computer, create a new folder named seedconfig and navigate into it.
    os.makedirs(SEED_ROOT, exist_ok=True)

    # 2. Create the meta-data configuration file
    meta_data = f"""
local-hostname: {hostname}
"""
    print("=> Write meta-data ...")
    write_file(f"{SEED_ROOT}/meta-data", meta_data)

    # 3. Create the user-data configuration file
    # Read Public SSH Key
    print("=> Read Public SSH key ...")
    pub_key = read_file(os.path.expanduser("~/.ssh/id_rsa.pub"))

    user_data = f"""#cloud-config
users:
- default
- name: ec2-user
  ssh_authorized_keys:
    - {pub_key}
- name: ccaroon
  sudo: ALL=(ALL) NOPASSWD:ALL
  ssh_authorized_keys:
    - {pub_key}
"""
    print("=> Write user-data ...")
    write_file(f"{SEED_ROOT}/user-data", user_data)

    # 4. (Optional) Create the network-config configuration file.
    # TODO, if necessary


@task(pre=[seed_data])
def seed_iso(ctx):
    """
    Create an ISO with the see data.

    See: https://docs.aws.amazon.com/linux/al2023/ug/seed-iso.html
    """
    # 5. Create the seed.iso disk image using the meta-data, user-data, and optional network-config configuration files created in the previous steps.
    if os.path.exists(SEED_ISO):
        os.unlink(SEED_ISO)

    # NOTE: Assumes MacOS tools
    print("=> Creating Seed ISO ...")
    if platform.system() == "Darwin":
        ctx.run(f"hdiutil makehybrid -o {SEED_ISO} -hfs -joliet -iso -default-volume-name cidata {SEED_ROOT}/", hide=True)
    elif platform.system() == "Linux":
        ctx.run(f"mkisofs -input-charset utf-8 -output {SEED_ISO} -volid cidata -joliet -rock {SEED_ROOT}/user-data {SEED_ROOT}/meta-data")


@task(pre=[seed_data])
def packer(ctx):
    """
    Build the Image specified in the `packer` dir
    """
    with ctx.cd(f"{utils.ROOT_DIR}/packer"):
        ctx.run("packer build .")


@task
def clean(ctx):
    """ Clean Up Build Artifacts """

    # tmp
    print(f"=> {TMP_DIR} ...")
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

    # packer/output
    packer_out_dir = f"{utils.ROOT_DIR}/packer/output"
    print(f"=> {packer_out_dir} ...")
    if os.path.exists(packer_out_dir):
        shutil.rmtree(packer_out_dir)

# ------------------------------------------------------------------------------
def read_file(path):
    contents = None
    with open(path, "r") as fptr:
        contents = fptr.read()
    return contents

def write_file(path, contents):
    with open(path, "w") as fptr:
        fptr.write(contents.strip())
