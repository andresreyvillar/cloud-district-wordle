"""Servidor local de la v2.0, con el mismo fallback que el Worker.

    python3 tools/serve_v2.py            # http://localhost:8788
    python3 tools/serve_v2.py --puerto 9000

Existe porque `python3 -m http.server` **no sirve para probar esto**: devuelve 404 en `/t/2026-07` y el
router nunca llegaría a ejecutarse. Cloudflare, con `not_found_handling: single-page-application`, devuelve
`index.html` con 200 para cualquier ruta que no sea un archivo real, y este servidor hace lo mismo — así lo
que se ve en local es lo que se verá publicado.

Solo lee archivos de `v2/`. No toca la base de datos: la web habla con Supabase directamente desde el
navegador con la clave publicable.
"""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent / "v2"
PUERTO = 8788


class ManejadorSPA(SimpleHTTPRequestHandler):
    """Sirve archivos reales y, para todo lo demás, `index.html` con 200."""

    def send_head(self):  # noqa: N802 - la firma es de la clase base
        ruta = Path(self.translate_path(self.path))
        if not ruta.exists() or (ruta.is_dir() and not (ruta / "index.html").exists()):
            self.path = "/index.html"
        return super().send_head()

    def end_headers(self):
        # Sin caché: en desarrollo, un módulo cacheado es media hora buscando un fallo que ya arreglaste.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, formato, *argumentos):
        print(f"  {self.command} {self.path} → {argumentos[1]}")


def main(argv: list[str] | None = None) -> int:
    analizador = argparse.ArgumentParser(description="Servidor local de la v2.0 con fallback SPA.")
    analizador.add_argument("--puerto", type=int, default=PUERTO)
    argumentos = analizador.parse_args(argv)

    if not (RAIZ / "index.html").exists():
        print(f"No encuentro {RAIZ / 'index.html'}")
        return 1

    manejador = partial(ManejadorSPA, directory=str(RAIZ))
    with ThreadingHTTPServer(("127.0.0.1", argumentos.puerto), manejador) as servidor:
        print(f"v2.0 en http://localhost:{argumentos.puerto}  (Ctrl+C para parar)")
        print(f"  sirviendo {RAIZ}")
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\nparado")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
