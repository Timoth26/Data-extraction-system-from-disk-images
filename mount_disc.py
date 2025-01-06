import os
import subprocess
import sys

class DiskImageManager:
    def __init__(self, image_path, mount_base='/tmp/disk_mount/'):
        self.image_path = image_path
        self.loop_device = None
        self.mount_points = []
        self.mount_base = mount_base
        self.mount_all_partitions()
        
    def __del__(self):
        self.cleanup()
        
    def __str__(self):
        return str(self.mount_points)

    def setup_loop_device(self):
        try:
            subprocess.run(['sudo', 'losetup', '-fP', self.image_path], check=True)
            self.loop_device = subprocess.check_output(['losetup', '-j', self.image_path]).decode().split(':')[0]
            print(f"[INFO] Loop device attached: {self.loop_device}")
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Error while setting up the loop device: {e}")
            sys.exit(1)

    def is_valid_filesystem(self, partition):
        try:
            output = subprocess.check_output(['sudo', 'blkid', partition])
            return 'TYPE=' in output.decode()
        except subprocess.CalledProcessError:
            return False

    def mount_partition(self, partition, mount_point):
        try:
            subprocess.run(['sudo', 'mount', '-o', 'ro', partition, mount_point], check=True)
            print(f"[INFO] Partition {partition} mounted at {mount_point}.")
            self.mount_points.append(mount_point)
            return True
        except subprocess.CalledProcessError:
            print(f"[ERROR] Unable to mount partition {partition}. Skipping.")
            return False

    def mount_all_partitions(self):
        if not self.loop_device:
            self.setup_loop_device()

        os.makedirs(self.mount_base, exist_ok=True)

        partitions = [f"/dev/{part}" for part in os.listdir('/dev') if part.startswith(os.path.basename(self.loop_device))]
        
        for i, partition in enumerate(partitions):
            if self.is_valid_filesystem(partition):
                print(f"\n[INFO] Partition {partition} has a valid filesystem, attempting to mount...")
                temp_mount_point = os.path.join(self.mount_base, f"part{i}")
                os.makedirs(temp_mount_point, exist_ok=True)
                self.mount_partition(partition, temp_mount_point)
            else:
                print(f"\n[WARNING] Partition {partition} does not have a valid filesystem. Skipping.")
        return self.mount_points

    def unmount_all(self):
        for mount_point in self.mount_points:
            try:
                subprocess.run(['sudo', 'umount', mount_point], check=True)
                print(f"[INFO] Unmounted from {mount_point}.")
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Error unmounting {mount_point}. It may already be unmounted. Error: {e}")
        self.mount_points.clear()

    def detach_loop_device(self):
        if self.loop_device:
            try:
                subprocess.run(['sudo', 'losetup', '-d', self.loop_device], check=True)
                print(f"[INFO] Loop device {self.loop_device} detached.")
                self.loop_device = None
            except subprocess.CalledProcessError as e:
                print(f"[ERROR] Error detaching loop device {self.loop_device}. Error: {e}")

    def cleanup(self):
        self.unmount_all()
        self.detach_loop_device()