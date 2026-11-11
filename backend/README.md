# Microservicio de Recomendación — Plataforma de Residencias Profesionales

Microservicio de machine learning construido con **FastAPI**. Lo consume el backend principal
(Spring Boot, puerto 8080) para:

- **Recomendar proyectos** a un alumno según sus habilidades.
- **Sugerir habilidades** que le conviene aprender.
- **Identificar su perfil profesional** (Backend Java, Frontend web, Cloud y DevOps…).
- Ofrecer el **catálogo de habilidades** reconocidas (p. ej. para autocompletar formularios).

El modelo se entrena en `analisis/modelo/notebooks/entrenamiento_modelo.ipynb` y sus archivos se copian a
`backend/artefactos/`, de modo que esta carpeta se puede desplegar por sí sola.

## Integración con Spring Boot

```
Frontend → Spring Boot (8080) → este microservicio (8000)
           · autenticación (JWT)      · no conoce usuarios ni roles
           · reglas de roles          · recibe los datos en cada petición
           · base de datos            · responde con recomendaciones
```

- Spring Boot sigue siendo el único punto de entrada para el frontend y aplica las reglas de roles.
- El microservicio **no accede a la base de datos**: Spring Boot le envía las habilidades del alumno y
  los proyectos a evaluar en cada petición.
- La comunicación se protege con una clave compartida en el header **`X-API-Key`** (variable `API_KEY`).

## Arquitectura (Modelo – Vista – Controlador)

```
backend/
├── app/
│   ├── main.py                        # Crea la app, carga el modelo y registra vistas y errores
│   ├── core/                          # Elementos transversales
│   │   ├── config.py                  #   Configuración (variables de entorno)
│   │   ├── dependencias.py            #   Inyección del modelo en las vistas
│   │   ├── seguridad.py               #   Verificación del header X-API-Key
│   │   └── errores.py                 #   Errores de negocio
│   ├── models/                        # MODELO: acceso al modelo de ML
│   │   ├── recomendador.py            #   Carga el .pkl: afinidad, sugerencias y perfil
│   │   └── normalizador_habilidades.py#   "reactjs" → React, "Golang" → Go
│   ├── schemas/                       # Contratos de entrada/salida (Pydantic)
│   │   ├── recomendacion.py
│   │   ├── habilidad.py
│   │   ├── modelo.py
│   │   └── salud.py
│   ├── controllers/                   # CONTROLADOR: lógica de negocio
│   │   ├── recomendacion_controller.py
│   │   ├── habilidad_controller.py
│   │   ├── modelo_controller.py
│   │   └── salud_controller.py
│   └── views/                         # VISTA: endpoints HTTP
│       ├── __init__.py                #   Agrupa los routers y aplica la clave de API
│       ├── recomendacion_view.py
│       ├── habilidad_view.py
│       ├── modelo_view.py
│       └── salud_view.py
├── artefactos/                        # Modelo entrenado (.pkl) y sus archivos JSON
├── tests/                             # Pruebas automáticas (pytest)
├── requirements.txt                   # Dependencias de producción
├── requirements-dev.txt               # Producción + pruebas
├── pytest.ini
└── README.md
```

Flujo de una petición:

```
Petición HTTP → Vista (valida con el esquema) → Controlador (normaliza y orquesta) → Modelo (ML) → respuesta
```

| Capa | Responsabilidad | No debe |
|---|---|---|
| **Vista** (`views/`) | Definir rutas, recibir la petición y devolver la respuesta | Contener lógica de negocio |
| **Controlador** (`controllers/`) | Normalizar habilidades, consultar el modelo y armar la respuesta | Conocer detalles de HTTP |
| **Modelo** (`models/`) | Cargar los artefactos y hacer los cálculos de ML | Conocer FastAPI ni los esquemas |
| **Esquemas** (`schemas/`) | Definir y validar la forma de los datos | — |

### Cómo agregar un recurso nuevo
1. `schemas/<recurso>.py` — esquemas de entrada y salida.
2. `models/<recurso>.py` — acceso a datos o al modelo (si hace falta).
3. `controllers/<recurso>_controller.py` — lógica.
4. `views/<recurso>_view.py` — router con los endpoints.
5. Registrar el router en `views/__init__.py`.
6. `tests/test_<recurso>.py` — pruebas.

## Puesta en marcha

Desde la carpeta `backend/`, con el entorno virtual activado:

```bash
pip install -r requirements-dev.txt
python -m app
```

El servidor arranca en **http://127.0.0.1:8000** (el 8080 lo ocupa el backend de Spring Boot) con
recarga automática. El host, el puerto y la recarga se cambian con las variables `HOST`, `PUERTO` y `RECARGA`
(ver *Configuración*). También se puede arrancar directamente con uvicorn:

```bash
uvicorn app.main:app --port 8000 --reload
```

- Documentación interactiva (Swagger): http://127.0.0.1:8000/docs
- Documentación alternativa (ReDoc): http://127.0.0.1:8000/redoc

## Endpoints

| Método | Ruta | Clave | Descripción |
|---|---|---|---|
| GET | `/api/v1/salud` | No | Estado del servicio y si el modelo está cargado |
| GET | `/api/v1/modelo` | Sí | Métricas y perfiles del modelo |
| GET | `/api/v1/habilidades?categoria=&busqueda=` | Sí | Catálogo de habilidades reconocidas |
| POST | `/api/v1/recomendaciones/proyectos` | Sí | Ordena proyectos por afinidad con el alumno |
| POST | `/api/v1/recomendaciones/habilidades` | Sí | Habilidades sugeridas para el alumno |
| POST | `/api/v1/recomendaciones/perfil` | Sí | Perfil profesional del alumno |

Las habilidades pueden escribirse de cualquier forma razonable (`reactjs`, `React.js`, `React JS`):
el servicio las normaliza y devuelve en `habilidades_no_reconocidas` las que no conoce.

### `POST /api/v1/recomendaciones/proyectos`

Petición (Spring Boot envía el alumno y los proyectos `DISPONIBLE` a evaluar):

```json
{
  "habilidades": ["Java", "Spring Boot", "SQL", "Git", "HTML"],
  "proyectos": [
    {"id": 1, "titulo": "Sistema de inventarios web", "habilidades": ["Java", "Spring Boot", "PostgreSQL", "REST API", "Docker"]},
    {"id": 2, "titulo": "Firmware para sensor IoT", "habilidades": ["C", "Embedded Systems", "RTOS", "I2C"]}
  ],
  "limite": 10
}
```

Respuesta (ordenada de mayor a menor afinidad):

```json
{
  "habilidades_reconocidas": ["Java", "Spring Boot", "SQL", "Git", "HTML"],
  "habilidades_no_reconocidas": [],
  "total_proyectos": 2,
  "resultados": [
    {"id": 1, "titulo": "Sistema de inventarios web", "afinidad": 0.4925,
     "habilidades_coincidentes": ["Java", "Spring Boot"],
     "habilidades_faltantes": ["PostgreSQL", "REST API", "Docker"],
     "habilidades_no_reconocidas": []},
    {"id": 2, "titulo": "Firmware para sensor IoT", "afinidad": 0.0, "...": "..."}
  ]
}
```

### `POST /api/v1/recomendaciones/habilidades`

```json
{"habilidades": ["Java", "Spring Boot", "SQL", "Git", "HTML"], "limite": 5}
```

```json
{
  "habilidades_reconocidas": ["Java", "Spring Boot", "SQL", "Git", "HTML"],
  "habilidades_no_reconocidas": [],
  "sugerencias": [
    {"habilidad": "JavaScript", "categoria": "Lenguajes", "relevancia": 1.0},
    {"habilidad": "Agile", "categoria": "Metodologías y gestión", "relevancia": 0.83},
    {"habilidad": "AWS", "categoria": "Cloud", "relevancia": 0.81}
  ]
}
```

### `POST /api/v1/recomendaciones/perfil`

```json
{"habilidades": ["Java", "Spring Boot", "SQL", "Git", "HTML"]}
```

```json
{
  "habilidades_reconocidas": ["Java", "Spring Boot", "SQL", "Git", "HTML"],
  "habilidades_no_reconocidas": [],
  "perfil": "Backend Java",
  "habilidades_clave": ["Java", "Agile", "SQL", "Git", "Spring Boot", "REST API", "Spring", "Jira", "Jenkins", "Scrum"],
  "habilidades_clave_faltantes": ["Agile", "REST API", "Spring", "Jira", "Jenkins", "Scrum"]
}
```

### Códigos de error
- **401** — falta el header `X-API-Key` o es incorrecto (solo si `API_KEY` está definida).
- **422** — datos inválidos (lista vacía, campo faltante o sobrante, límites superados) o el alumno
  no tiene ninguna habilidad técnica reconocida (la respuesta incluye `habilidades_no_reconocidas`).
- **503** — el modelo no se pudo cargar al iniciar (ver los registros del servidor). `/salud` también
  responde 503 en ese caso, para que Render no dé por bueno el despliegue.

Límites: hasta 100 habilidades por alumno o proyecto y hasta 500 proyectos por petición.

## Configuración

Todas las variables son opcionales:

| Variable | Valor por defecto |
|---|---|
| `HOST` | `127.0.0.1` (usar `0.0.0.0` para aceptar conexiones de otras máquinas) |
| `PUERTO` | `8000` |
| `RECARGA` | `true` (recarga automática al cambiar el código; usar `false` en producción) |
| `API_KEY` | *(sin definir: no se exige clave; definirla en producción)* |
| `MODELO_RUTA` | `backend/artefactos/modelo_recomendador.pkl` |
| `METADATOS_RUTA` | `backend/artefactos/metadatos_recomendador.json` |
| `NORMALIZACION_RUTA` | `backend/artefactos/normalizacion_habilidades.json` |
| `CORS_ORIGENES` | `http://localhost:3000,http://localhost:5173` (separados por comas) |
| `API_PREFIJO` | `/api/v1` |
| `APP_NOMBRE` / `APP_VERSION` | Nombre y versión mostrados en la documentación |

## Pruebas

```bash
pytest
```

Cubren la normalización de habilidades, el orden de los proyectos, las sugerencias, los perfiles,
la validación de entradas, la clave de API y el comportamiento sin modelo.

## Notas
- El modelo se carga **una sola vez** al iniciar el servidor, no en cada petición.
- `pickle` puede ejecutar código al cargar un archivo: carga solo modelos `.pkl` de confianza.
- El `.pkl` depende de la versión de scikit-learn con la que se entrenó (fijada en `requirements.txt`);
  si no coincide, el servidor lo indica en los registros al arrancar.
- Tras reentrenar el modelo no hay que tocar el código: copia los 3 archivos de `analisis/modelo/artefactos/`
  a `backend/artefactos/` y vuelve a desplegar. `pytest` avisa si las dos carpetas no coinciden.

## Despliegue en Render

El servicio se construye desde la **raíz del repositorio** (no hace falta configurar *Root Directory*)
y solo instala y ejecuta la carpeta `backend/`:

- `requirements.txt` (raíz) remite a `backend/requirements.txt`: no instala pandas ni matplotlib.
- `.python-version` fija Python 3.12.1, la versión con la que se entrenó y probó el modelo.
- `render.yaml` define el servicio si se crea como Blueprint.

1. Sube el proyecto a un repositorio de GitHub (`.gitignore` ya excluye el entorno virtual y los datos originales).
2. En Render, **New → Blueprint** y elige el repositorio; escribe el valor de `API_KEY` cuando lo pida.
   Si creas el servicio a mano (**New → Web Service**), usa:

   | Campo | Valor |
   |---|---|
   | Root Directory | *(vacío)* |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT` |
   | Health Check Path | `/api/v1/salud` |
   | Variables | `API_KEY` (y opcionalmente `PYTHON_VERSION=3.12.1`) |

3. Comprueba `https://<tu-servicio>.onrender.com/api/v1/salud`: debe responder `"estado": "ok"`.
4. En Spring Boot define estas variables:

   | Variable | Valor |
   |---|---|
   | `RECOMENDACIONES_URL` | `https://<tu-servicio>.onrender.com` |
   | `RECOMENDACIONES_API_KEY` | El mismo valor de `API_KEY` |
   | `RECOMENDACIONES_TIMEOUT_SEGUNDOS` | `90` en el plan gratuito |

En el plan gratuito, el servicio se apaga tras 15 minutos sin tráfico y tarda cerca de un minuto en
despertar; por eso el tiempo de espera debe ser mayor en Spring Boot.
