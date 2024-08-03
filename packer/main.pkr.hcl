locals {
  base_image_id       = "https://cdn.amazonlinux.com/al2023/os-images/2023.5.20240722.0/kvm-arm64/al2023-kvm-2023.5.20240722.0-kernel-6.1-arm64.xfs.gpt.qcow2"
  base_image_checksum = "sha256:a042326f3e81317d306639f34855ff45505fbc6fb027207a486c4c7c85d0f4c2"

  ssh_username = "ec2-user"

  arch_aliases = {
    arm64 = "aarch64",
    amd64 = "x86_64"
  }
}

build {
  sources = [
    "source.qemu.al2023"
  ]

  // provisioner "shell" {
  //   inline = [
  //     "sudo dnf install -y nginx",
  //     "sudo systemctl enable nginx"
  //   ]
  // }

  provisioner "ansible" {
    user = "ec2-user"
    // extra_arguments = [
    //   "-vvv",
    // ]
    playbook_file = "./ansible/provision.yml"
  }

  post-processor "vagrant" {
    output              = "./output/packer_{{.BuildName}}_{{.Provider}}_{{.Architecture}}.box"
    keep_input_artifact = true
  }
}
