import json
from pathlib import Path

from app.data.archivos import escribir_atomico
from app.models.empleado import Empleado


class RepositorioJSON:
    def __init__(self, ruta):
        self._ruta = Path(ruta)
        if not self._ruta.exists():
            self.guardar_todos([])

    def cargar_todos(self) -> list[Empleado]:
        texto = self._ruta.read_text(encoding="utf-8").strip()
        if not texto:
            return []
        datos = json.loads(texto)
        return [Empleado.from_dict(d) for d in datos.get("Empleados", [])]

    def guardar_todos(self, empleados: list[Empleado]) -> None:
        datos = {"Empleados": [e.to_dict() for e in empleados]}
        texto = json.dumps(datos, indent=2, ensure_ascii=False)
        escribir_atomico(self._ruta, texto.encode("utf-8"))