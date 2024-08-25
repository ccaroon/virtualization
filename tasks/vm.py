import os

from invoke import task

import utils

FORMAT_MAP = {
    ".img": "raw"
}

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


@task(iterable="port")
def run(ctx, name, cdrom=None, boot=None, port=None):
    """
    Run the specified VM Image with QEMU.

    name (str): Known image shortname or path to image file
    """
    image = name2image(name)
    img_arch = image['arch']
    image_url = image['url']

    # Always map 50022 -> 22 (SSH)
    port_fwds = "hostfwd=tcp::50022-:22"
    for port_map in port:
        (host, guest) = port_map.split(":", 2)
        port_fwds += f",hostfwd=tcp::{host}-:{guest}"

    if image_url.startswith("file://"):
        img_path = image['file']
        img_pid = f"{os.path.basename(img_path)}.pid"
    else:
        img_path = f"images/{image['file']}"
        img_pid = f"{name}.pid"

    if not os.path.exists(img_path):
        raise FileNotFoundError(f"Image Not Found: [{img_path}]")

    # System / Arch specifics
    specs = utils.qemu_specs()
    img_ext = os.path.splitext(img_path)[1]
    img_fmt = FORMAT_MAP.get(img_ext, img_ext[1:])

    cmd = [
        f"qemu-system-{img_arch}",
        f"-accel {specs['accel']}",
        f"-machine {specs['machine']}",
        "-cpu host",
        "-smp 4",
        "-m 4G",
        # TODO: don't really need this?
        # f"-bios {specs['bios']['code]}",
        f"-drive if=virtio,format={img_fmt},file={img_path}",
        "-serial stdio",
        f"-netdev user,id=net0,{port_fwds}",
        f"-device {specs['net_device']},netdev=net0",
        f"-pidfile {img_pid}"
    ]

    if cdrom:
        cmd.append(f"-drive file={cdrom},media=cdrom,readonly=on")

    if boot:
        cmd.append(f"-boot once={boot}")

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

    if images:
        image_url = images.get(arch)
        image_file = None

        if not image_url:
            raise ValueError(f"Unknown Architecture: [{arch}]")
        else:
            image_file = os.path.basename(image_url)
    else:
        if os.path.exists(name):
            image_url = f"file://{name}"
            image_file = name
        else:
            raise FileNotFoundError(f"Invalid Image Name or Path: [{name}]")

    return {
        "url": image_url,
        "file": image_file,
        "arch": arch
    }
