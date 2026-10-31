import os
import shutil
import sys
import tempfile
from pathlib import Path


def ruta_base() -> Path:
    """Carpeta del proyecto, o carpeta del .exe si está empaquetado."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]


def ruta_recurso(*partes: str) -> Path:
    """Recursos de solo lectura (ui, etc.): _MEIPASS si está empaquetado."""
    base = Path(getattr(sys, "_MEIPASS", ruta_base()))
    return base.joinpath(*partes)


def ruta_datos(nombre: str) -> Path:
    """Archivo de datos escribible junto al proyecto/.exe.
    Si está empaquetado y no existe, copia la semilla desde _MEIPASS."""
    destino = ruta_base() / "datos" / nombre
    if not destino.exists() and getattr(sys, "frozen", False):
        semilla = Path(getattr(sys, "_MEIPASS", "")) / "datos" / nombre
        if semilla.is_file():
            destino.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(semilla, destino)
    return destino


def escribir_atomico(ruta: Path, contenido: bytes) -> None:
    """Escribe a un temporal en la misma carpeta y reemplaza el original."""
    ruta.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=ruta.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(contenido)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, ruta)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
        