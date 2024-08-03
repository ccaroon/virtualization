source "qemu" "al2023" {
  qemu_binary = "qemu-system-${local.arch_aliases[var.arch]}"
  // vm_name           = "tdhtest"

  iso_url      = local.base_image_id
  iso_checksum = local.base_image_checksum

  // seed ISO
  cd_label = "cidata"
  cd_content = {
    "meta-data" = file("${var.working_dir}/meta-data")
    "user-data" = file("${var.working_dir}/user-data")
  }

  ssh_username         = local.ssh_username
  ssh_private_key_file = "~/.ssh/id_rsa"

  efi_firmware_code = "/opt/homebrew/opt/qemu/share/qemu/edk2-aarch64-code.fd"
  efi_firmware_vars = "/opt/homebrew/opt/qemu/share/qemu/edk2-arm-vars.fd"

  accelerator         = "hvf"
  disk_image          = true
  format              = "qcow2"
  headless            = false
  use_backing_file    = true
  use_default_display = true

  cpu_model    = "host"
  cpus         = 2
  machine_type = "virt,highmem=on"
  memory       = 4096

  output_directory = "output"
}
