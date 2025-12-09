#!/usr/bin/env python3
import json
import subprocess
import requests
import time
import os
from pathlib import Path

class FirecrackerSandbox:
    def __init__(self, vm_id):
        self.vm_id = vm_id
        self.socket_path = f"/tmp/firecracker-{vm_id}.socket"
        self.process = None
        
    def start(self):
        """Start the Firecracker process"""
        # Remove existing socket
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)
            
        # Start Firecracker
        self.process = subprocess.Popen([
            'firecracker',
            '--api-sock', self.socket_path
        ])
        
        # Wait for socket to be ready
        time.sleep(0.5)
        
    def configure_vm(self, kernel_path, rootfs_path, vcpus=1, mem_mib=128):
        """Configure the VM settings"""
        base_url = f"http://localhost"
        session = requests.Session()
        session.mount('http://localhost', 
                     requests.adapters.HTTPAdapter(
                         pool_connections=1,
                         pool_maxsize=1,
                         max_retries=0))
        
        # Configure boot source
        response = session.put(
            f"{base_url}/boot-source",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'kernel_image_path': kernel_path,
                'boot_args': 'console=ttyS0 reboot=k panic=1 pci=off'
            }),
            timeout=5,
            unix_socket=self.socket_path
        )
        
        # Configure rootfs
        session.put(
            f"{base_url}/drives/rootfs",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'drive_id': 'rootfs',
                'path_on_host': rootfs_path,
                'is_root_device': True,
                'is_read_only': False
            }),
            timeout=5,
            unix_socket=self.socket_path
        )
        
        # Configure machine
        session.put(
            f"{base_url}/machine-config",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'vcpu_count': vcpus,
                'mem_size_mib': mem_mib
            }),
            timeout=5,
            unix_socket=self.socket_path
        )
        
    def start_instance(self):
        """Boot the VM"""
        session = requests.Session()
        session.put(
            "http://localhost/actions",
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'action_type': 'InstanceStart'}),
            timeout=5,
            unix_socket=self.socket_path
        )
        
    def cleanup(self):
        """Clean up resources"""
        if self.process:
            self.process.terminate()
            self.process.wait()
        if os.path.exists(self.socket_path):
            os.remove(self.socket_path)

# Example usage
if __name__ == "__main__":
    sandbox = FirecrackerSandbox("test-vm-001")
    
    try:
        print("Starting Firecracker...")
        sandbox.start()
        
        print("Configuring VM...")
        sandbox.configure_vm(
            kernel_path="./vmlinux",
            rootfs_path="./rootfs.ext4",
            vcpus=2,
            mem_mib=512
        )
        
        print("Booting VM...")
        sandbox.start_instance()
        
        print("VM is running!")
        time.sleep(10)  # Keep running for demo
        
    finally:
        print("Cleaning up...")
        sandbox.cleanup()