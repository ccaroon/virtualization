/opt/homebrew/bin/qemu-system-aarch64  \
    -machine virt,accel=hvf,highmem=on \
    -cpu host \
    -smp 2 \
    -m 4G \
    -device virtio-net-device,netdev=net0 \
    -netdev user,id=net0,hostfwd=tcp::50022-:22 \
    -serial stdio \
    -bios /opt/homebrew/opt/qemu/share/qemu/edk2-aarch64-code.fd \
    -drive if=virtio,format=qcow2,file=./output/packer-al2023
