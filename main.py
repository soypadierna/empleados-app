import webview

from app.business.empleado_service import EmpleadoService
from app.data.archivos import ruta_datos, ruta_recurso
from app.data.repositorio_json import RepositorioJSON
from app.data.repositorio_xml import RepositorioXML
from app.presentation.api import Api


def main():
    fuentes = {
        "json": lambda: RepositorioJSON(ruta_datos("empleados.json")),
        "xml": lambda: RepositorioXML(ruta_datos("empleados.xml")),
    }
    servicio = EmpleadoService(fuentes["json"]())
    api = Api(servicio, fuentes)
    webview.create_window(
        "Gestión de Empleados",
        url=str(ruta_recurso("app", "ui", "index.html")),
        js_api=api,
        width=1000,
        height=650,
        min_size=(900, 600),
    )
    webview.start()


if __name__ == "__main__":
    main()