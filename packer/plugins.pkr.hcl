
packer {
  required_plugins {
    ansible = {
      version = "~> 1.1"
      source  = "github.com/hashicorp/ansible"
    }
    qemu = {
      version = "~> 1.1"
      source  = "github.com/hashicorp/qemu"
    }
    vagrant = {
      version = "~> 1.1"
      source  = "github.com/hashicorp/vagrant"
    }
  }
}
