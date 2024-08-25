// locals {
//   arch_aliases = {
//     aarch64 = "arm64"
//     x86_64  = "amd64"
//   }
// }

build {
  sources = [
    "source.qemu.image"
  ]

  // provisioner "shell" {
  //   inline = [
  //     "sudo dnf install -y nginx",
  //     "sudo systemctl enable nginx"
  //   ]
  // }

  provisioner "ansible" {
    user = var.ansible.user
    // extra_arguments = [
    //   "-vvv",
    // ]
    playbook_file = var.ansible.playbook
  }

  // post-processor "vagrant" {
  //   output              = "./output/packer_{{.BuildName}}_{{.Provider}}_{{.Architecture}}.box"
  //   keep_input_artifact = true
  // }
}
