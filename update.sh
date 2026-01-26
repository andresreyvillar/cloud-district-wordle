#!/bin/bash

# 1. Ejecutar el script de Python para procesar los datos
python3 tools/add_results.py

# 2. Verificar si hubo cambios en data.json
if git diff --quiet data/data.json; then
    echo "No hay nuevos datos para subir."
else
    # 3. Subir a GitHub
    git add data/data.json
    git commit -m "Update stats: $(date +'%Y-%m-%d')"
    git push origin main
    echo "¡Web actualizada en Cloudflare Pages! 🚀"
fi
