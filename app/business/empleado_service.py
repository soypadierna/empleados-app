import re
from datetime import datetime

from app.models.empleado import Empleado, FORMATO_FECHA

_MAX_TEXTO = 50
_MAX_BIGINT = 2**63 - 1
_RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_RE_FECHA = re.compile(r"\d{4}-\d{2}-\d{2}")


class EmpleadoService:
    def __init__(self, repositorio):
        self._repo = None
        self._empleados: list[Empleado] = []
        self._ultimo_id = 0
        self.cambiar_repositorio(repositorio)

    def cambiar_repositorio(self, repositorio) -> None:
        empleados = repositorio.cargar_todos()  # si falla, no se cambia nada
        self._repo = repositorio
        self._empleados = empleados
        self._ultimo_id = max((e.IdEmpleado for e in empleados), default=0)

    def listar(self) -> list[Empleado]:
        return list(self._empleados)

    def obtener(self, id_empleado) -> Empleado:
        id_empleado = int(id_empleado)
        for e in self._empleados:
            if e.IdEmpleado == id_empleado:
                return e
        raise ValueError(f"No existe un empleado con ID {id_empleado}.")

    def agregar(self, datos: dict) -> Empleado:
        nuevo = self._validar(datos)
        nuevo.IdEmpleado = self._siguiente_id()
        lista = self._empleados + [nuevo]
        self._repo.guardar_todos(lista)
        self._empleados = lista
        self._ultimo_id = nuevo.IdEmpleado
        return nuevo

    def editar(self, id_empleado, datos: dict) -> Empleado:
        actual = self.obtener(id_empleado)
        editado = self._validar(datos, id_actual=actual.IdEmpleado)
        editado.IdEmpleado = actual.IdEmpleado
        lista = [editado if e.IdEmpleado == actual.IdEmpleado else e
                 for e in self._empleados]
        self._repo.guardar_todos(lista)
        self._empleados = lista
        return editado

    def eliminar(self, id_empleado) -> None:
        actual = self.obtener(id_empleado)
        lista = [e for e in self._empleados if e.IdEmpleado != actual.IdEmpleado]
        self._repo.guardar_todos(lista)
        self._empleados = lista

    def buscar(self, texto: str) -> list[Empleado]:
        t = (texto or "").strip().casefold()
        if not t:
            return self.listar()
        return [
            e for e in self._empleados
            if t in e.StrNombre.casefold()
            or t in str(e.NumDocumento)
            or t in e.StrEmail.casefold()
        ]

    # ---------- internos ----------
    def _siguiente_id(self) -> int:
        maximo = max((e.IdEmpleado for e in self._empleados), default=0)
        return max(maximo, self._ultimo_id) + 1

    def _validar(self, datos: dict, id_actual: int | None = None) -> Empleado:
        nombre = str(datos.get("StrNombre") or "").strip()
        direccion = str(datos.get("StrDireccion") or "").strip()
        telefono = str(datos.get("StrTelefono") or "").strip()
        email = str(datos.get("StrEmail") or "").strip()

        if not nombre:
            raise ValueError("El nombre es obligatorio.")
        if not email:
            raise ValueError("El email es obligatorio.")

        for etiqueta, valor in (("nombre", nombre), ("dirección", direccion),
                                ("teléfono", telefono), ("email", email)):
            if len(valor) > _MAX_TEXTO:
                raise ValueError(
                    f"El {etiqueta} no puede superar {_MAX_TEXTO} caracteres.")

        raw = datos.get("NumDocumento")
        if isinstance(raw, float) and raw.is_integer():
            raw = int(raw)
        doc_txt = str(raw if raw is not None else "").strip()
        if not doc_txt:
            raise ValueError("El documento es obligatorio.")
        if not (doc_txt.isascii() and doc_txt.isdigit()):
            raise ValueError("El documento debe contener solo dígitos.")
        documento = int(doc_txt)
        if documento > _MAX_BIGINT:
            raise ValueError("El documento es demasiado largo.")

        if not _RE_EMAIL.match(email):
            raise ValueError("El email no tiene un formato válido.")

        if any(e.NumDocumento == documento and e.IdEmpleado != id_actual
               for e in self._empleados):
            raise ValueError(f"Ya existe un empleado con el documento {documento}.")

        fecha_txt = str(datos.get("DtmIngreso") or "").strip()
        if not fecha_txt:
            raise ValueError("La fecha de ingreso es obligatoria.")
        if not _RE_FECHA.fullmatch(fecha_txt):
            raise ValueError("La fecha de ingreso debe tener formato yyyy-MM-dd.")
        if not 1900 <= fecha.year <= 2100:
            raise ValueError("La fecha de ingreso debe estar entre 1900 y 2100.")
        try:
            fecha = datetime.strptime(fecha_txt, FORMATO_FECHA)
        except ValueError:
            raise ValueError("La fecha de ingreso no es una fecha válida.") from None

        return Empleado(
            IdEmpleado=0,
            StrNombre=nombre,
            NumDocumento=documento,
            StrDireccion=direccion,
            StrTelefono=telefono,
            StrEmail=email,
            DtmIngreso=fecha,
        )