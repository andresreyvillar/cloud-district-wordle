"""Un Postgres desechable con las migraciones del repositorio aplicadas, para probar la base de datos sin
tocar producción.

Levanta un clúster en un directorio temporal, crea los roles que usa Supabase (`anon`, `authenticated`,
`service_role`) con los privilegios por defecto que da Supabase a las tablas nuevas, una `wordle_results`
mínima, y aplica **todas** las migraciones de `supabase/migrations/` en orden, tal cual. Si la máquina no
tiene Postgres, los tests que lo usan se saltan.
"""

from __future__ import annotations

import shutil
import socket
import subprocess
import tempfile
from pathlib import Path

import pytest

MIGRACIONES = Path(__file__).resolve().parents[1] / "supabase" / "migrations"


def _binario(nombre: str) -> str | None:
    return shutil.which(nombre) or next(
        (str(p) for p in Path("/opt/homebrew/opt").glob(f"postgresql@*/bin/{nombre}") if p.exists()), None
    )


INITDB, PG_CTL, PSQL = _binario("initdb"), _binario("pg_ctl"), _binario("psql")

sin_postgres = pytest.mark.skipif(not (INITDB and PG_CTL and PSQL), reason="no hay Postgres local")

ESQUEMA_MINIMO = """
create role anon nologin;
create role authenticated nologin;
create role service_role nologin bypassrls;
create table public.wordle_results (
  id bigserial primary key,
  player_name text, wordle_id integer, score integer, date date, slack_user_id text, pattern text
);
grant select on public.wordle_results to anon, authenticated;
-- Lo que hace Supabase con las tablas nuevas: todos los privilegios a los roles de la API.
alter default privileges in schema public grant all on tables to anon, authenticated, service_role;
grant usage on schema public to anon, authenticated, service_role;
"""


def _puerto_libre() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def postgres_con_migraciones(filas_sql: str = ""):
    """Generador para un fixture: rinde `sql(consulta, rol=None) -> CompletedProcess` y apaga al salir.

    `filas_sql` se ejecuta entre el esquema mínimo y las migraciones: son los datos de partida.
    """
    directorio = Path(tempfile.mkdtemp(prefix="pg-local-"))
    datos, enchufe = directorio / "datos", directorio / "enchufe"
    enchufe.mkdir()
    puerto = _puerto_libre()
    subprocess.run([INITDB, "-D", str(datos), "-U", "postgres", "--auth=trust"], check=True, capture_output=True)
    subprocess.run(
        [PG_CTL, "-D", str(datos), "-w", "-l", str(directorio / "log"),
         "-o", f"-p {puerto} -k {enchufe} -c listen_addresses=''", "start"],
        check=True, capture_output=True,
    )

    def sql(consulta: str, rol: str | None = None) -> subprocess.CompletedProcess:
        prefijo = f"set role {rol};\n" if rol else ""
        return subprocess.run(
            [PSQL, "-X", "-q", "-At", "-v", "ON_ERROR_STOP=1", "-h", str(enchufe), "-p", str(puerto),
             "-U", "postgres", "-d", "postgres"],
            input=prefijo + consulta, text=True, capture_output=True,
        )

    try:
        esquema = sql(ESQUEMA_MINIMO)
        assert esquema.returncode == 0, esquema.stderr
        if filas_sql:
            insercion = sql(filas_sql)
            assert insercion.returncode == 0, insercion.stderr
        for migracion in sorted(MIGRACIONES.glob("*.sql")):
            aplicada = sql(migracion.read_text(encoding="utf-8"))
            assert aplicada.returncode == 0, f"{migracion.name}: {aplicada.stderr}"
        yield sql
    finally:
        subprocess.run([PG_CTL, "-D", str(datos), "-m", "immediate", "stop"], capture_output=True)
        shutil.rmtree(directorio, ignore_errors=True)
