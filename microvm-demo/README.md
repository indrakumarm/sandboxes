# Firecracker MicroVM Lab Quickstart

## Prerequisites
- Linux host with KVM enabled
- Firecracker binary (see below)
- curl, wget, and Docker (for rootfs customization)

## 1. Download Firecracker binary

```bash
ARCH="$(uname -m)"
release_url="https://github.com/firecracker-microvm/firecracker/releases"
latest=$(basename $(curl -fsSLI -o /dev/null -w %{url_effective} ${release_url}/latest))
curl -L ${release_url}/download/${latest}/firecracker-${latest}-${ARCH}.tgz | tar -xz
sudo mv release-${latest}-$(uname -m)/firecracker-${latest}-${ARCH} /usr/local/bin/firecracker
sudo chmod +x /usr/local/bin/firecracker
```

## 2. Download  kernel and rootfs

```bash
mkdir -p ~/firecracker-lab && cd ~/firecracker-lab
wget https://s3.amazonaws.com/spec.ccfc.min/img/hello/kernel/hello-vmlinux.bin
wget https://s3.amazonaws.com/spec.ccfc.min/img/hello/fsfiles/hello-rootfs.ext4
```

## 3. Launch Firecracker

```bash
rm -f /tmp/firecracker.socket
firecracker --api-sock /tmp/firecracker.socket &
sleep 2

curl --unix-socket /tmp/firecracker.socket -X PUT 'http://localhost/boot-source' \
  -H 'Content-Type: application/json' \
  -d '{"kernel_image_path": "./hello-vmlinux.bin", "boot_args": "console=ttyS0 reboot=k panic=1 pci=off"}'

curl --unix-socket /tmp/firecracker.socket -X PUT 'http://localhost/drives/rootfs' \
  -H 'Content-Type: application/json' \
  -d '{"drive_id": "rootfs", "path_on_host": "./hello-rootfs.ext4", "is_root_device": true, "is_read_only": false}'

curl --unix-socket /tmp/firecracker.socket -X PUT 'http://localhost/machine-config' \
  -H 'Content-Type: application/json' \
  -d '{"vcpu_count": 1, "mem_size_mib": 512}'

curl --unix-socket /tmp/firecracker.socket -X PUT 'http://localhost/actions' \
  -H 'Content-Type: application/json' \
  -d '{"action_type": "InstanceStart"}'
```

## 4. Customizing the rootfs (optional)
- For a shell, build a rootfs with `/bin/sh` as init using Alpine or BusyBox
- See Firecracker docs for advanced networking, vsock, and guest workload setup

---

**For more details:**
- Firecracker GitHub: https://github.com/firecracker-microvm/firecracker
- AWS Lambda Architecture: https://aws.amazon.com/lambda/
- Kata Containers: https://katacontainers.io/
