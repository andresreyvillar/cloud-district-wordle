# Wordle Analytics 📊

Web estática para analizar la evolución y estadísticas de un grupo de jugadores de Wordle.

## 📁 Estructura del Proyecto

- `index.html`: Estructura principal de la web.
- `css/`: Estilos personalizados (basados en la estética de Wordle).
- `js/`: Lógica para procesar estadísticas y generar gráficos (Plotly.js).
- `data/data.json`: **Base de datos de resultados**. Aquí es donde debes añadir los nuevos datos.

## 🚀 Cómo añadir nuevos datos

Para añadir un nuevo resultado, abre `data/data.json` y añade un objeto al final del array:

```json
{
  "date": "2026-01-26",
  "user": "Tu Nombre",
  "num": "1481",
  "score": 4
}
```

## ☁️ Despliegue en Cloudflare Pages

1. Sube este proyecto a un repositorio de GitHub.
2. En Cloudflare, crea un nuevo proyecto de **Pages** conectado a ese repositorio.
3. Cloudflare detectará automáticamente los archivos estáticos y desplegará la web.
4. Cada vez que hagas `git push` con nuevos datos en el JSON, la web se actualizará sola.
