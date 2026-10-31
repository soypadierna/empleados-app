from dataclasses import dataclass
from datetime import date, datetime

FORMATO_FECHA = "%Y-%m-%d"


@dataclass
class Empleado:
    IdEmpleado: int = 0
    StrNombre: str = ""
    NumDocumento: int = 0
    StrDireccion: str = ""
    StrTelefono: str = ""
    StrEmail: str = ""
    DtmIngreso: datetime | None = None

    def to_dict(self) -> dict:
        return {
            "IdEmpleado": self.IdEmpleado,
            "StrNombre": self.StrNombre,
            "NumDocumento": self.NumDocumento,
            "StrDireccion": self.StrDireccion,
            "StrTelefono": self.StrTelefono,
            "StrEmail": self.StrEmail,
            "DtmIngreso": self.DtmIngreso.strftime(FORMATO_FECHA) if self.DtmIngreso else "",
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Empleado":
        return cls(
            IdEmpleado=int(d.get("IdEmpleado") or 0),
            StrNombre=str(d.get("StrNombre", "")).strip(),
            NumDocumento=int(d.get("NumDocumento") or 0),
            StrDireccion=str(d.get("StrDireccion", "")).strip(),
            StrTelefono=str(d.get("StrTelefono", "")).strip(),
            StrEmail=str(d.get("StrEmail", "")).strip(),
            DtmIngreso=_parsear_fecha(d.get("DtmIngreso")),
        )


def _parsear_fecha(valor) -> datetime | None:
    if not valor:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime(valor.year, valor.month, valor.day)
    return datetime.strptime(str(valor).strip(), FORMATO_FECHA)