import xml.etree.ElementTree as ET
from pathlib import Path

from app.data.archivos import escribir_atomico
from app.models.empleado import Empleado

_DECLARACION = b'<?xml version="1.0" encoding="UTF-8"?>\n'


class RepositorioXML:
    def __init__(self, ruta):
        self._ruta = Path(ruta)
        if not self._ruta.exists():
            self.guardar_todos([])

    def cargar_todos(self) -> list[Empleado]:
        if self._ruta.stat().st_size == 0:
            return []
        raiz = ET.parse(self._ruta).getroot()
        return [
            Empleado.from_dict({hijo.tag: (hijo.text or "") for hijo in nodo})
            for nodo in raiz.findall("Empleado")
        ]

    def guardar_todos(self, empleados: list[Empleado]) -> None:
        raiz = ET.Element("Empleados")
        for e in empleados:
            nodo = ET.SubElement(raiz, "Empleado")
            for campo, valor in e.to_dict().items():
                ET.SubElement(nodo, campo).text = str(valor)
        ET.indent(raiz, space="  ")
        cuerpo = ET.tostring(raiz, encoding="utf-8", xml_declaration=False)
        escribir_atomico(self._ruta, _DECLARACION + cuerpo + b"\n")