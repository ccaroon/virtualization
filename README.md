# Virtualization

## Misc
* https://cloudinit.readthedocs.io/en/latest/index.html

## AL2023
* https://docs.aws.amazon.com/linux/al2023/ug/outside-ec2-download.html
* https://docs.aws.amazon.com/linux/al2023/ug/seed-iso.html
* https://docs.aws.amazon.com/linux/al2023/ug/kvm-supported-configurations.html
* https://www.itwriting.com/blog/12160-amazon-linux-2023-on-hyper-v.html


## Vagrant
* https://developer.hashicorp.com/vagrant/docs
* https://developer.hashicorp.com/vagrant/vagrant-cloud/boxes/create
* https://developer.hashicorp.com/vagrant/docs/boxes/base#creating-a-base-box
* https://www.engineyard.com/blog/building-a-vagrant-box-from-start-to-finish/



## Mini How-Tos

### Create empty RAW disk image

```bash
qemu-img create myimage.raw 50g
```

OR

```bash
inv build.disk myimage 50g
```

### Boot from CDROM/ISO with Empty RAW disk image. Useful to install OS onto empty disk.

```bash
qemu-system-x86_64 -m 4G -smp 2 \
    -drive if=virtio,format=raw,file=EMPTY-DISK.raw \
    -drive file=/PATH/TO/IMAGE.iso,media=cdrom,readonly=on \
    -boot d
```

OR

```bash
inv vm.run EMPTY-DISK.raw --cdrom /PATH/TO/IMAGE.iso --boot d
```
