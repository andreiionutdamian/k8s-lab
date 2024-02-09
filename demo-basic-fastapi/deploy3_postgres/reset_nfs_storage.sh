source ../utils.sh

APP="basic-test-py-simple"
MOUNT_POINT="/mnt/nfs/$APP"
NFS_SERVER="192.168.1.56:/srv/nfs/k8s/pg_storage/$APP"

log_with_color "Checking mount point $MOUNT_POINT..." yellow
if [ ! -d "$MOUNT_POINT" ]; then
    log_with_color "  Creating mount point $MOUNT_POINT..." yellow
    sudo mkdir -p "$MOUNT_POINT"
    log_with_color "  Mount point $MOUNT_POINT created." green
fi

log_with_color "Mounting $NFS_SERVER to $MOUNT_POINT" yellow
sudo mount -t nfs "$NFS_SERVER" "$MOUNT_POINT" && log_with_color "  NFS mount successful." green || log_with_color "  Error: NFS mount failed." red

log_with_color "Checking if $MOUNT_POINT has files..." yellow
if [ -z "$(ls -A $MOUNT_POINT)" ]; then
    log_with_color "  $MOUNT_POINT is empty." green
else
    log_with_color "  $MOUNT_POINT is not empty." yellow
    log_with_color "  Deleting all files in $MOUNT_POINT..." yellow
    sudo rm -rf --preserve-root "$MOUNT_POINT/*" && log_with_color "    All files in $MOUNT_POINT have been successfully deleted." green || log_with_color "    Error: Failed to delete files in $MOUNT_POINT." red
fi

log_with_color "Unmounting $MOUNT_POINT..." yellow
sudo umount "$MOUNT_POINT" && log_with_color "  $MOUNT_POINT unmounted successfully." green || log_with_color "  Error: Failed to unmount $MOUNT_POINT." red

log_with_color "Deleting mount point $MOUNT_POINT..." yellow
sudo rm -rf "  $MOUNT_POINT" && log_with_color "  Mount point $MOUNT_POINT deleted successfully." green || log_with_color "  Error: Failed to delete mount point $MOUNT_POINT." red

