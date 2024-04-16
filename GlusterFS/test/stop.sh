#!/bin/bash
echo "Deleting the NFS test pods..."

kubectl delete -f test-1.yaml -f test-2.yaml

echo "Cleaning up the NFS mount point..."

# Define the NFS mount point and NFS server
MOUNT_POINT="/mnt/nfs"
NFS_SERVER="192.168.1.56:/srv/nfs/k8s/simple-nfs-test"
NFS_FILES="testfile.txt"

# Function to check and create the NFS mount folder
check_create_folder() {
    echo "Checking if the folder $MOUNT_POINT exists..."
    if [ ! -d "$MOUNT_POINT" ]; then
        echo "The folder $MOUNT_POINT does not exist. Creating folder..."
        sudo mkdir -p "$MOUNT_POINT"
    else
        echo "The folder $MOUNT_POINT exists."
    fi
}

# Function to mount the NFS server to the mount point
mount_nfs() {
    echo "Mounting $NFS_SERVER to $MOUNT_POINT"
    sudo mount -t nfs "$NFS_SERVER" "$MOUNT_POINT" && echo "NFS mount successful." || echo "Error: NFS mount failed."
}

# Function to check for an active NFS mount
check_mount() {
    echo "Checking for an active NFS mount on $MOUNT_POINT..."
    if mount | grep $MOUNT_POINT > /dev/null; then
        echo "An active NFS mount is found on $MOUNT_POINT."
        return 0
    else
        echo "No active NFS mount found on $MOUNT_POINT."
        return 1
    fi
}

# Function to delete all files in the mount point
delete_files() {
    echo "Mount point $MOUNT_POINT contains the following files:"
    ls -l "$MOUNT_POINT"
    echo "Deleting all files in $MOUNT_POINT..."
    rm -rf --preserve-root "$MOUNT_POINT/$NFS_FILES" && echo "All files in $MOUNT_POINT have been successfully deleted." || echo "Error: Failed to delete files in $MOUNT_POINT."
}

# Function to unmount NFS
unmount_nfs() {
    echo "Unmounting $MOUNT_POINT..."
    sudo umount "$MOUNT_POINT" && echo "$MOUNT_POINT unmounted successfully." || echo "Error: Failed to unmount $MOUNT_POINT."
}

# Main script execution
check_create_folder

# Check for active mount; Delete files and unmount if active; Otherwise, mount the NFS server
if check_mount; then
    delete_files
    unmount_nfs
else
    mount_nfs
    # After mounting, perform a check again and delete files if mount is successful
    if check_mount; then
        delete_files
        unmount_nfs
    fi
fi
