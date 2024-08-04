source "qemu" "image" {
  qemu_binary = "qemu-system-${var.arch}"
  vm_name     = "${var.vm_name}.qcow2"

  iso_url      = var.base_image.id
  iso_checksum = var.base_image.checksum

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

  accelerator         = var.accel
  disk_image          = true
  disk_size =         var.disk_size
  format              = "qcow2"
  headless            = false
  use_backing_file    = true
  use_default_display = true

  cpu_model    = "host"
  cpus         = 2
  machine_type = var.machine_type
  memory       = 4096

  output_directory = "${var.working_dir}/image"
}
