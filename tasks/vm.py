import os
from invoke import task

import utils

IMAGE_DIR = f"{utils.ROOT_DIR}/images"
IMAGES = {
    "al2023": {
        "aarch64": "https://cdn.amazonlinux.com/al2023/os-images/2023.5.20240722.0/kvm-arm64/al2023-kvm-2023.5.20240722.0-kernel-6.1-arm64.xfs.gpt.qcow2",
        "x86_64": "https://cdn.amazonlinux.com/al2023/os-images/2023.5.20240730.0/kvm/al2023-kvm-2023.5.20240730.0-kernel-6.1-x86_64.xfs.gpt.qcow2"
    },
    "fedora40": {
        "aarch64": "https://download.fedoraproject.org/pub/fedora/linux/releases/40/Server/aarch64/images/Fedora-Server-KVM-40-1.14.aarch64.qcow2",
        "x86_64": "https://download.fedoraproject.org/pub/fedora/linux/releases/40/Server/x86_64/images/Fedora-Server-KVM-40-1.14.x86_64.qcow2"
    }
}


@task
def run(ctx, name, cdrom=None):
    """
    Run the specified VM Image with QEMU.

    name (str): Known image shortname or path to image file
    """
    image = name2image(name)
    img_arch = image['arch']
    image_url = image['url']

    if not image_url:
        img_path = name
        img_pid = f"{os.path.basename(img_path)}.pid"
    else:
        img_pid = f"{name}.pid"
        img_path = f"images/{image['file']}"

    if not os.path.exists(img_path):
        raise ValueError(f"Invalid Image: [{name}]")

    # System / Arch specifics
    bios_file = None
    machine = None
    if utils.host() == "Linux-x86_64":
        bios_file = "/usr/share/qemu/OVMF.fd"
        machine = "pc,accel=kvm"
        net_device = "e1000"
    elif utils.host().startswith("Darwin-"):
        bios_file = f"/opt/homebrew/opt/qemu/share/qemu/edk2-{img_arch}-code.fd"
        machine = "virt,accel=hvf,highmem=on"
        net_device = "virtio-net-device"

    cmd = [
        f"qemu-system-{img_arch}",
        f"-machine {machine}",
        "-cpu host",
        "-smp 2",
        "-m 4G",
        f"-bios {bios_file}",
        f"-drive if=virtio,format=qcow2,file={img_path}",
        "-serial stdio",
        "-netdev user,id=net0,hostfwd=tcp::50022-:22",
        f"-device {net_device},netdev=net0",
        f"-pidfile {img_pid}"
    ]

    if cdrom:
        cmd.append(f"-drive file={cdrom},media=cdrom,readonly=on")

    ctx.run(" ".join(cmd), pty=True, echo=True)


@task
def fetch_image(ctx, name):
    """
    Download an Image
    """
    download = True
    image = name2image(name)

    if os.path.exists(f"{IMAGE_DIR}/{image['file']}"):
        download = False
        overwrite = input(f"Image '{name}' for '{image['arch']}' already exists. Overwrite (yes|no)? ")
        if overwrite.strip() == "yes":
            download = True

    if download:
        print(f"=> Fetching {name} for {image['arch']}...")
        ctx.run(f"wget -P {IMAGE_DIR} {image['url']}", pty=True)
    else:
        print(f"Not overwriting '{image['file']}' / '{image['url']}'")


@task
def ssh(ctx, user="ec2-user", port=50022):
    """
    SSH login to a VM
    """
    ctx.run(f"ssh {user}@127.0.0.1 -p {port}", pty=True)

# ------------------------------------------------------------------------------
def name2image(name):
    arch = utils.arch()
    images = IMAGES.get(name)

    if not images:
        raise ValueError(f"Invalid Image Name: [{name}]")

    image_url = images.get(arch)
    image_file = None

    if not image_url:
        raise ValueError(f"Unknown Architecture: [{arch}]")
    else:
        image_file = os.path.basename(image_url)

    return {
        "url": image_url,
        "file": image_file,
        "arch": arch
    }