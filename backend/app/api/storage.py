import os
import json
import subprocess
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/storage", tags=["storage"])

class DeviceListResponse(BaseModel):
    devices: List[dict]


@router.get("/devices", response_model=DeviceListResponse)
def list_devices():
    """Return lsblk -J output (JSON) to the client.
    """
    try:
        completed = subprocess.run(["lsblk", "-J", "-o", "NAME,SIZE,TYPE,MOUNTPOINT,UUID,MODEL"], check=True, stdout=subprocess.PIPE)
        data = json.loads(completed.stdout)
        return {"devices": data.get('blockdevices', [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"lsblk failed: {e}")


class MountRequest(BaseModel):
    device: str
    mount_point: str
    fstab: bool = True
    fs_type: str = "auto"


@router.post("/mount")
def mount_device(req: MountRequest):
    # Basic validation
    if not os.path.exists(req.device):
        raise HTTPException(status_code=404, detail="Device not found")
    try:
        os.makedirs(req.mount_point, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cannot create mount point: {e}")

    try:
        subprocess.run(["mount", req.device, req.mount_point], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"mount failed: {e.stderr}")

    # Optionally append to fstab
    if req.fstab:
        try:
            completed = subprocess.run(["blkid", "-s", "UUID", "-o", "value", req.device], check=True, stdout=subprocess.PIPE)
            uuid = completed.stdout.decode().strip()
        except Exception:
            uuid = None
        line = f"UUID={uuid} {req.mount_point} {req.fs_type} defaults 0 2\n" if uuid else f"{req.device} {req.mount_point} {req.fs_type} defaults 0 2\n"
        try:
            with open('/etc/fstab', 'a') as f:
                f.write(line)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to write fstab: {e}")

    return {"ok": True}


class RaidCreateRequest(BaseModel):
    name: str
    level: int
    devices: List[str]


@router.post("/raid")
def create_raid(req: RaidCreateRequest):
    # WARNING: Destructive action. This implementation is a simple wrapper and does not perform checks.
    # TODO: Add confirmations, dry-run, backups and device locks.
    raid_device = f"/dev/md/{req.name}"
    try:
        subprocess.run(["mdadm", "--create", raid_device, "--level=%d" % req.level, "--raid-devices=%d" % len(req.devices)] + req.devices, check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"mdadm failed: {e}")

    # Persist mdadm config
    try:
        completed = subprocess.run(["mdadm", "--detail", "--scan"], check=True, stdout=subprocess.PIPE)
        with open('/etc/mdadm/mdadm.conf', 'a') as f:
            f.write(completed.stdout.decode())
    except Exception as e:
        # non-fatal
        pass

    return {"ok": True, "device": raid_device}
