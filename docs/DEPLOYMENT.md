# Deployment notes for Debian 12

This file describes a minimal deployment approach for running the backend as a systemd service on Debian 12.

1) Copy files to /opt/server-panel (recommendation)

   sudo mkdir -p /opt/server-panel
   sudo chown root:root /opt/server-panel
   # copy project files to /opt/server-panel

2) Create a Python virtualenv and install requirements

   python3 -m venv /opt/server-panel/venv
   source /opt/server-panel/venv/bin/activate
   pip install -r /opt/server-panel/backend/requirements.txt

3) Systemd unit

   Edit backend/systemd/server-panel.service.template -> save as /etc/systemd/system/server-panel.service

   sudo systemctl daemon-reload
   sudo systemctl enable --now server-panel.service

4) Samba configuration

   Ensure /etc/samba/smb.conf contains an include line:

      include = /etc/samba/shares/*.conf

   Create /etc/samba/shares and set permissions.

5) Docker management

   To allow the backend to manage local Docker, the service needs access to /var/run/docker.sock (the service already runs as root in this deployment).

Security notes:
- Running as root is intentionally chosen for full system control, but increases risk. Hardening recommendations:
  - Run behind a reverse proxy (Caddy/nginx) with TLS and IP restrictions
  - Enable Firewall to allow only trusted networks
  - Add authentication (OAuth2 / local users) before production use
  - Limit capabilities where possible

