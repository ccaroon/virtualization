import json
import os
import platform
import shutil

from invoke import task

import yaml
import utils

TMP_DIR = f"{utils.ROOT_DIR}/tmp"
SEED_ROOT = f"{TMP_DIR}/seedconfig"
SEED_ISO = f"{TMP_DIR}/seed.iso"


@task
def image(ctx, image_spec):
    qemu_specs = utils.qemu_specs()

    # read image_spec yaml file
    print("=> Parse Image Spec...")
    build_spec = None
    with open(image_spec, "r") as fptr:
        spec = yaml.safe_load(fptr)
        build_spec = spec.get("BUILD")

    # mkdir spec file name - ext
    image_dir = os.path.dirname(os.path.abspath(image_spec))
    image_name = os.path.splitext(os.path.basename(image_spec))[0]
    image_path = f"{image_dir}"
    if not os.path.exists(image_path):
        print("=> Make Image Data Dir...")
        os.mkdir(image_path)

    # create seed data
    print("=> Create Seed Data...")
    create_seed_data(image_name, build_spec['users'], image_path)

    # create packer vars.json
    pkr_vars_file = f"{image_path}/{image_name}.pkrvars.json"
    pkr_vars_data = {
        "accel": qemu_specs["accel"],
        "arch": utils.arch(),
        "base_image": build_spec["src_image"],
        "disk_size": build_spec.get("disk", {}).get("size", "25G"),
        "bios": qemu_specs["bios"],
        "machine_type": qemu_specs["machine"],
        "ssh_username": build_spec['ssh_username'],
        "vm_name": image_name,
        "working_dir": image_path
    }

    ansible = build_spec.get("ansible")
    if ansible:
        playbook = ansible.get("playbook")
        if not playbook:
            raise ValueError("'ansible.playbook' is required!")

        playbook_path = None
        if os.path.isabs(playbook):
            playbook_path = playbook
        else:
            playbook_path = os.path.abspath(f"{image_dir}/{playbook}")

        pkr_vars_data["ansible"] = {
            "user": ansible.get("user", build_spec["ssh_username"]),
            "playbook": playbook_path
        }

    pkr_vars_json = json.dumps(pkr_vars_data, indent=2)
    utils.write_file(pkr_vars_file, pkr_vars_json)

    # run packer validate
    ctx.run(f"packer validate -var-file {pkr_vars_file} packer")

    # run packer build
    ctx.run(f"packer build -var-file {pkr_vars_file} packer")

@task
def disk(ctx, name, size):
    """
    Use `qemu-img` to create an empty disk image
    """

    ctx.run(f"qemu-img create {name}.raw {size}")

# @task
# def seed_data(ctx, hostname="caroon-al2023"):
#     """
#     Create data files for a seed image.

#     See: https://docs.aws.amazon.com/linux/al2023/ug/seed-iso.html
#     """
#     # 1. On a Linux or macOS computer, create a new folder named seedconfig and navigate into it.
#     os.makedirs(SEED_ROOT, exist_ok=True)

#     # 2. Create the meta-data configuration file
#     meta_data = f"""
# local-hostname: {hostname}
# """
#     print("=> Write meta-data ...")
#     write_file(f"{SEED_ROOT}/meta-data", meta_data)

#     # 3. Create the user-data configuration file
#     # Read Public SSH Key
#     print("=> Read Public SSH key ...")
#     pub_key = read_file(os.path.expanduser("~/.ssh/id_rsa.pub"))

#     user_data = f"""#cloud-config
# users:
# - default
# - name: ec2-user
#   ssh_authorized_keys:
#     - {pub_key}
# - name: ccaroon
#   sudo: ALL=(ALL) NOPASSWD:ALL
#   ssh_authorized_keys:
#     - {pub_key}
# """
#     print("=> Write user-data ...")
#     write_file(f"{SEED_ROOT}/user-data", user_data)

#     # 4. (Optional) Create the network-config configuration file.
#     # TODO, if necessary


# @task(pre=[seed_data])
# def seed_iso(ctx):
#     """
#     Create an ISO with the see data.

#     See: https://docs.aws.amazon.com/linux/al2023/ug/seed-iso.html
#     """
#     # 5. Create the seed.iso disk image using the meta-data, user-data, and optional network-config configuration files created in the previous steps.
#     if os.path.exists(SEED_ISO):
#         os.unlink(SEED_ISO)

#     # NOTE: Assumes MacOS tools
#     print("=> Creating Seed ISO ...")
#     if platform.system() == "Darwin":
#         ctx.run(f"hdiutil makehybrid -o {SEED_ISO} -hfs -joliet -iso -default-volume-name cidata {SEED_ROOT}/", hide=True)
#     elif platform.system() == "Linux":
#         ctx.run(f"mkisofs -input-charset utf-8 -output {SEED_ISO} -volid cidata -joliet -rock {SEED_ROOT}/user-data {SEED_ROOT}/meta-data")



# @task
# def clean(ctx, image_spec):
#     """ Clean Up Build Artifacts """

#     # tmp
#     print(f"=> {TMP_DIR} ...")
#     if os.path.exists(TMP_DIR):
#         shutil.rmtree(TMP_DIR)

#     # packer/output
#     packer_out_dir = f"{utils.ROOT_DIR}/packer/output"
#     print(f"=> {packer_out_dir} ...")
#     if os.path.exists(packer_out_dir):
#         shutil.rmtree(packer_out_dir)

# ------------------------------------------------------------------------------
def create_seed_data(hostname, users, output_path):
    """
    Create data files for a seed image.

    See: https://docs.aws.amazon.com/linux/al2023/ug/seed-iso.html
    """

    # 2. Create the meta-data configuration file
    meta_data = f"""
local-hostname: {hostname}
"""
    print("=> Write meta-data ...")
    utils.write_file(f"{output_path}/meta-data", meta_data)

    # 3. Create the user-data configuration file
    # Read Public SSH Key
    print("=> Read Public SSH key ...")
    pub_key = utils.read_file(os.path.expanduser("~/.ssh/id_rsa.pub"))

    users_text = ""
    for username in users:
        users_text += f"""
- name: {username}
  sudo: ALL=(ALL) NOPASSWD:ALL
  ssh_authorized_keys:
    - {pub_key}
"""

    user_data = f"""
#cloud-config
users:
- default
{users_text}
"""

    print("=> Write user-data ...")
    utils.write_file(f"{output_path}/user-data", user_data)

    # 4. (Optional) Create the network-config configuration file.
    # TODO, if necessary
