import os
import subprocess
from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/samba", tags=["samba"])

SHARES_DIR = "/etc/samba/shares"

class ShareCreate(BaseModel):
    name: str
    path: str
    valid_users: List[str] = []
    browseable: bool = True
    read_only: bool = False


def ensure_shares_dir():
    try:
        os.makedirs(SHARES_DIR, exist_ok=True)
    except Exception as e:
        raise


@router.get("/shares")
def list_shares():
    """List share files in the configured shares directory (parses filenames only).
    """
    ensure_shares_dir()
    shares = []
    for fname in os.listdir(SHARES_DIR):
        if fname.endswith('.conf'):
            shares.append(fname[:-5])
    return {"shares": shares}


@router.post("/shares")
def create_share(payload: ShareCreate):
    """Create a samba share file and reload smbd.

    WARNING: This function writes to /etc/samba/shares and reloads the Samba daemon. The backend is expected to run as root.
    """
    ensure_shares_dir()
    # Basic validation
    if '/' in payload.name or '\\' in payload.name:
        raise HTTPException(status_code=400, detail="Invalid share name")

    share_file = os.path.join(SHARES_DIR, f"{payload.name}.conf")
    if os.path.exists(share_file):
        raise HTTPException(status_code=400, detail="Share already exists")

    # Create path if missing
    try:
        os.makedirs(payload.path, exist_ok=True)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create path: {e}")

    valid_users = ','.join(payload.valid_users)
    conf = [f"[{payload.name}]", f"\tpath = {payload.path}", f"\tbrowseable = {'yes' if payload.browseable else 'no'}", f"\tread only = {'yes' if payload.read_only else 'no'}"]
    if valid_users:
        conf.append(f"\tvalid users = {valid_users}")

    try:
        with open(share_file, 'w') as f:
            f.write('\n'.join(conf) + '\n')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write share file: {e}")

    # Validate with testparm
    try:
        subprocess.run(["testparm", "-s"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        # On syntax error, remove created file
        try:
            os.remove(share_file)
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=f"testparm failed: {e.stderr.decode()}")

    # Reload smbd
    try:
        subprocess.run(["systemctl", "reload", "smbd"], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload smbd: {e.stderr.decode()}")

    return {"ok": True, "share": payload.name}


@router.delete("/shares/{name}")
def delete_share(name: str):
    share_file = os.path.join(SHARES_DIR, f"{name}.conf")
    if not os.path.exists(share_file):
        raise HTTPException(status_code=404, detail="Not found")
    try:
        os.remove(share_file)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove: {e}")

    try:
        subprocess.run(["systemctl", "reload", "smbd"], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=500, detail=f"Failed to reload smbd: {e.stderr.decode()}")

    return {"ok": True}
