# server-panel

Lightweight server administration panel (Samba, storage, Docker management).

Ziel: Debian 12 (Backend läuft als root auf dem Host). Das Projekt ist als leichtes, erweiterbares Scaffold angelegt — Backend in Python (FastAPI), simples Frontend, Docker‑Integration (verwaltet lokale Docker‑Container über den Docker Socket) und Tools/Docs für Bare‑Metal‑Deployment.

Wichtiges:
- Backend ist entworfen, um als systemd Service auf dem Host mit Root‑Rechten zu laufen (für mount/raid/samba/mdadm).
- Für die lokale Entwicklung steht ein Docker‑Compose Setup bereit. Für volle Hardware‑Funktionen (RAID, mount, Samba) empfiehlt sich bare‑metal Deployment.

Schnellstart (Entwicklung):

1) Build & Run (lokal, Entwicklung):

   cd backend
   docker build -t server-panel-backend .
   docker run --rm -it -p 8000:8000 \
     -v /var/run/docker.sock:/var/run/docker.sock \
     -v $(pwd)/backend:/app \
     server-panel-backend

2) Auf dem Host (Debian 12) als systemd Service:
   - Siehe docs/DEPLOYMENT.md für das systemd template und Anweisungen.

Was noch fehlt / Nächste Schritte:
- Frontend (Svelte) Integration: aktuelles Scaffold enthält Platzhalter und Hinweise.
- Authentifizierung + RBAC (Platzhalter für zukünftige Implementierung).
- Tests und Sicherheits‑Härtung.


