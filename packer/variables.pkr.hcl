
variable "accel" {
  type        = string
  description = "Virtualization Accelarator type"
}

variable "ssh_username" {
  type        = string
  description = "User used to connect to the base image"
}

variable "vm_name" {
  type = string
}

variable "disk_size" {
  type = string
}

variable "working_dir" {
  type        = string
  description = "Working directory for input and outputs"
}

variable "arch" {
  type    = string
  default = "x86_64"
}

variable "machine_type" {
  type = string
}

variable "bios" {
  type = object({
    code = string
    vars = string
  })
  description = "BIOS / UFI Firmware Files"
}

variable "base_image" {
  type = object({
    id       = string
    checksum = string
  })
  description = "Base Image Info"
}

variable "ansible" {
  type = object({
    user = string
    playbook = string
  })
}
