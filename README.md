# Gestión de Empleados

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![pywebview](https://img.shields.io/badge/UI-pywebview-2563eb)
![Datos](https://img.shields.io/badge/Datos-JSON%20%7C%20XML-orange)
![Dependencias](https://img.shields.io/badge/Dependencias-solo%20pywebview-brightgreen)
![Plataforma](https://img.shields.io/badge/Plataforma-Windows-0078D6?logo=windows&logoColor=white)

App de escritorio CRUD (Python 3.10+ y pywebview). Los datos se guardan en JSON o XML. Solo usa la librería estándar para los datos.

![Captura de la aplicación](docs/captura.png)


## Funcionalidades
| | Función | Detalle |
|---|---|---|
| 📋 | Listar | Tabla de 7 columnas, carga inicial desde JSON |
| ➕ | Agregar | ID autoincremental, validaciones en español |
| ✏️ | Editar | Clic en fila, carga el formulario en modo edición |
| 🗑️ | Eliminar | Con confirmación previa |
| 🔍 | Buscar | En vivo por nombre, documento o email |
| 🔄 | Fuente | Alternar entre JSON y XML sin reiniciar |
| 📤 | Exportar | CSV en UTF-8 con BOM |

## Arquitectura por capas
```mermaid
flowchart LR
    UI["ui<br/>HTML · CSS · JS"] -->|js_api| API["presentation<br/>Api"]
    API --> SVC["business<br/>EmpleadoService"]
    SVC -.usa.-> MOD["models<br/>Empleado"]
    SVC --> REPO{{"data<br/>Repositorio"}}
    REPO --> JSON[("empleados.json")]
    REPO --> XML[("empleados.xml")]
```

## Flujo de guardado
```mermaid
sequenceDiagram
    actor U as Usuario
    participant J as app.js
    participant A as Api
    participant S as EmpleadoService
    participant R as Repositorio
    U->>J: Clic en Guardar
    J->>A: agregar(datos) / editar(id, datos)
    A->>S: agregar / editar
    S->>S: Validar (ValueError si falla)
    S->>R: guardar_todos(lista)
    R-->>S: escritura atómica OK
    S-->>A: Empleado
    A-->>J: {ok, data, error}
    J-->>U: Tabla actualizada + mensaje de estado
```

## Modelo de datos
```mermaid
classDiagram
    class Empleado {
        +int IdEmpleado
        +str StrNombre
        +int NumDocumento
        +str StrDireccion
        +str StrTelefono
        +str StrEmail
        +datetime DtmIngreso
        +to_dict() dict
        +from_dict(d) Empleado
    }
```

## Instalación
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Ejecución
```
python main.py
```

## Estructura por capas
| Capa | Carpeta | Responsabilidad |
|---|---|---|
| Modelo | `app/models` | Dataclass `Empleado` (`to_dict` / `from_dict`) |
| Datos | `app/data` | `RepositorioJSON`, `RepositorioXML`, rutas y escritura atómica |
| Negocio | `app/business` | `EmpleadoService`: validaciones, IDs, CRUD y búsqueda |
| Presentación | `app/presentation` | `Api` expuesta a JS (`{ok, data, error}`) |
| UI | `app/ui` | `index.html`, `style.css`, `app.js` |

Los datos de ejemplo están en `datos/`.

## Empaquetado (.exe)
```
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --name GestionEmpleados --add-data "app/ui;app/ui" --add-data "datos;datos" main.py
```
El ejecutable queda en `dist/`. Al primer arranque crea la carpeta `datos/` junto al `.exe`.