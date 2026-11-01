#!/bin/bash
set -e

# Inicia o display virtual
Xvfb :99 -screen 0 1280x1024x24 &
export DISPLAY=:99

# Garante que o nodriver use o Chromium da imagem
export CHROME_PATH="/ms-playwright/chromium-*/chrome-linux/chrome"

sleep 3

exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 180 --capture-output --access-logfile - --error-logfile - sistema_iptv_roku:app