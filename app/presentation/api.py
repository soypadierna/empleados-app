import csv
import functools

import webview

_ENCABEZADOS = ["ID", "Nombre", "Documento", "Dirección",
                "Teléfono", "Email", "Fecha de ingreso"]
_CAMPOS = ["IdEmpleado", "StrNombre", "NumDocumento", "StrDireccion",
           "StrTelefono", "StrEmail", "DtmIngreso"]


def _seguro(f):
    @functools.wraps(f)
    def envoltura(self, *args, **kwargs):
        try:
            return {"ok": True, "data": f(self, *args, **kwargs), "error": ""}
        except ValueError as e:
            return {"ok": False, "data": None, "error": str(e)}
        except Exception as e:
            return {"ok": False, "data": None, "error": f"Error inesperado: {e}"}
    return envoltura


class Api:
    def __init__(self, servicio, fuentes):
        self._servicio = servicio
        self._fuentes = fuentes

    @staticmethod
    def _lista(empleados):
        return [e.to_dict() for e in empleados]

    @_seguro
    def listar(self):
        return self._lista(self._servicio.listar())

    @_seguro
    def buscar(self, texto):
        return self._lista(self._servicio.buscar(texto))

    @_seguro
    def agregar(self, datos):
        return self._servicio.agregar(datos).to_dict()

    @_seguro
    def editar(self, id_empleado, datos):
        return self._servicio.editar(id_empleado, datos).to_dict()

    @_seguro
    def eliminar(self, id_empleado):
        self._servicio.eliminar(id_empleado)
        return None

    @_seguro
    def cambiar_fuente(self, fuente):
        fabrica = self._fuentes.get(str(fuente).lower())
        if fabrica is None:
            raise ValueError("Fuente de datos no válida. Use 'json' o 'xml'.")
        self._servicio.cambiar_repositorio(fabrica())
        return self._lista(self._servicio.listar())

    @_seguro
    def exportar_csv(self):
        tipo = (webview.FileDialog.SAVE if hasattr(webview, "FileDialog")
                else webview.SAVE_DIALOG)
        ruta = webview.windows[0].create_file_dialog(
            tipo, save_filename="empleados.csv",
            file_types=("Archivos CSV (*.csv)",))
        if not ruta:
            return None  # cancelado
        if isinstance(ruta, (list, tuple)):
            ruta = ruta[0]
        ruta = str(ruta)
        if not ruta.lower().endswith(".csv"):
            ruta += ".csv"
        with open(ruta, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(_ENCABEZADOS)
            for e in self._servicio.listar():
                d = e.to_dict()
                w.writerow([d[c] for c in _CAMPOS])
        return ruta