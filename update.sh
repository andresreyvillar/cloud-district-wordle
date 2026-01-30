#!/bin/bash

# Asegurar que el script se ejecuta en el directorio correcto
cd /Users/andres/Projects/wordle-stats || exit

# Cargar variables de entorno si es necesario (opcional, python-dotenv ya lo hace)
# export PATH=$PATH:/usr/local/bin:/opt/homebrew/bin

echo "Starting update process: $(date)" >> update.log

# 1. Pipeline de extracción y procesamiento
# Capturamos output y errores para debugging en caso de fallo silencioso del cron
if /usr/bin/python3 tools/extract_slack.py | /usr/bin/python3 tools/add_results.py >> update.log 2>&1; then
    echo "Extraction finished." >> update.log
else
    echo "Error during extraction." >> update.log
    exit 1
fi

# 2. Verificar si hubo cambios en data/data.json
if git diff --quiet data/data.json; then
    echo "No hay nuevos datos para subir." >> update.log
else
    # 3. Subir a GitHub
    git add data/data.json
    git commit -m "Auto-update stats: $(date +'%Y-%m-%d %H:%M')"
    
    # Intentar push, loguear error si falla
    if git push origin main >> update.log 2>&1; then
        echo "¡Web actualizada en Cloudflare Pages! 🚀" >> update.log
    else
        echo "Error haciendo push a GitHub." >> update.log
    fi
fi
echo "-----------------------------------" >> update.log