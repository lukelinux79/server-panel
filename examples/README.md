# Example snippets and commands to help during initial setup

## Samba include snippet

Append to /etc/samba/smb.conf:

    include = /etc/samba/shares/*.conf

Create shares directory:

    sudo mkdir -p /etc/samba/shares
    sudo chown root:root /etc/samba/shares
    sudo chmod 0755 /etc/samba/shares


## Example fstab line (after creating FS on /dev/md0):

    UUID=YOUR-UUID /mnt/data ext4 defaults,noatime 0 2

## Example mdadm - create raid1 (careful, destructive):

    sudo mdadm --create --verbose /dev/md0 --level=1 --raid-devices=2 /dev/sdb /dev/sdc

