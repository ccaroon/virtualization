locals {
  is_iso = substr(var.base_image.id, -3, 3) == "iso"
}

source "qemu" "image" {
  qemu_binary = "qemu-system-${var.arch}"
  vm_name     = "${var.vm_name}.qcow2"

  iso_url      = var.base_image.id
  iso_checksum = var.base_image.checksum
  // Is `is_url` an QCOW2 image instead of an ISO?
  disk_image = !local.is_iso

  // seed ISO
  cd_label = "cidata"
  cd_content = {
    "meta-data" = file("${var.working_dir}/meta-data")
    "user-data" = file("${var.working_dir}/user-data")
  }

  ssh_username         = var.ssh_username
  ssh_private_key_file = "~/.ssh/id_rsa"

  efi_firmware_code = var.bios.code
  efi_firmware_vars = var.bios.vars

  headless            = true
  use_backing_file    = !local.is_iso
  use_default_display = true

  accelerator  = var.accel
  cpu_model    = "host"
  cpus         = 2
  disk_size    = var.disk_size
  machine_type = var.machine_type
  memory       = 4096

  // Output Format
  format           = "qcow2"
  output_directory = "${var.working_dir}/image"
}
