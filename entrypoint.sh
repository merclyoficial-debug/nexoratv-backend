#!/bin/bash
set -e

# Inicia Xvfb (display virtual para o Chrome)
Xvfb :99 -screen 0 1280x1024x24 &
export DISPLAY=:99

# Espera o Xvfb subir
sleep 3

# Inicia Gunicorn
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 180 --capture-output --access-logfile - --error-logfile - sistema_iptv_roku:app