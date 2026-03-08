# Tasks Microservice (FastAPI)

Microservicio REST para gestión de tareas (CRUD) construido con FastAPI, SQLAlchemy async y una arquitectura basada en Clean Architecture + DDD + Hexagonal.

## ¿Qué hace este proyecto?

Expone una API HTTP para:

- Verificar estado del servicio (`/healthz`)
- Crear tareas
- Listar tareas
- Actualizar tareas
- Eliminar tareas

Modelo principal:

- `Task`
- Campos: `id`, `title`, `done`, `created_at`

## Endpoints

- `GET /`
- `GET /healthz`
- `GET /tasks`
- `GET /tasks?done=true|false`
- `GET /tasks?title_contains=<texto>`
- `POST /tasks`
- `PUT /tasks/{task_id}`
- `DELETE /tasks/{task_id}`

## Cómo está construido

Estructura de capas actual:

- `app/domain/`: reglas de negocio puras (entidad, value object, contratos de repositorio, errores).
- `app/application/`: casos de uso por operación (`create_task`, `list_tasks`, `update_task`, `delete_task`) con `command/query`, `port`, `handler`.
- `app/infrastructure/`: adaptadores técnicos.
- `app/infrastructure/config`: configuración y dependency injection.
- `app/infrastructure/persistence/sqlalchemy`: persistencia SQLAlchemy async.
- `app/infrastructure/http/rest`: adaptador HTTP REST (controllers, routes, request/response schemas).
- `app/main.py`: bootstrap de FastAPI y ciclo de vida (init/close de DB).

Regla de dependencias:

- `Infrastructure -> Application -> Domain`

## Requisitos

- Python 3.9+
- `pip`

## Configuración

### 1. Crear entorno virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Instalar dependencias base

```bash
pip install -r requirements-dev.txt
```

### 3. Variables de entorno

Puedes usar `.env` (basado en `.env.example`).

Ejemplo rápido para local con SQLite:

```env
PORT=8000
TURSO_DATABASE_URL=sqlite+aiosqlite:///./local.db
TURSO_AUTH_TOKEN=
```

### 4. (Opcional) Soporte Turso/libsql

Si usarás `libsql://...`, instala también:

```bash
pip install -r requirements-turso.txt
```

## Ejecutar el servicio

### Opción recomendada

```bash
uvicorn app.main:app --reload --port 8000
```

### Opción alternativa

```bash
python -m app.main
```

API docs:

- Swagger UI: `http://localhost:8000/docs`

## Ejecutar con Docker

### Build estándar (sin dependencias Turso)

```bash
docker build -t tasks-microservice .
```

### Run estándar

```bash
docker run --rm -p 8000:8000 --env-file .env tasks-microservice
```

### Build con soporte Turso/libsql

```bash
docker build --build-arg INSTALL_TURSO=true -t tasks-microservice:turso .
```

### Run con soporte Turso/libsql

```bash
docker run --rm -p 8000:8000 --env-file .env tasks-microservice:turso
```

## Deploy con Helm

El chart de Helm está en `helm/python-api`.

### Instalar/reinstalar

```bash
helm upgrade --install python-api ./helm/python-api \
  --namespace default \
  --set env.config.TURSO_DATABASE_URL="sqlite+aiosqlite:////tmp/local.db" \
  --set env.secret.TURSO_AUTH_TOKEN=""
```

### Validar chart

```bash
helm lint ./helm/python-api
helm template python-api ./helm/python-api
```

## Publicación a DockerHub (GitHub Actions)

Se agregó el workflow `.github/workflows/release-dockerhub.yml` que en cada push a `main`:

- Crea/pushea un tag Git con formato `v0.1.<run_number>`.
- Construye la imagen desde `Dockerfile`.
- Publica en DockerHub `jhndagon11/tasks` con tags:
  - `v0.1.<run_number>`
  - `latest`
  - `sha-<commit_sha>`

Secrets requeridos en GitHub:

- `DOCKERHUB_USERNAME`
- `DOCKERHUB_TOKEN`
- `RELEASE_TOKEN` (opcional, recomendado si `GITHUB_TOKEN` no puede crear tags por políticas del repo)

## Turso token sin exponerlo en Git (ArgoCD/Helm)

Puedes usar un Secret ya existente en el cluster y referenciarlo desde Helm.

1. Crear secret en el namespace de la app:

```bash
kubectl -n default create secret generic python-api-turso \
  --from-literal=TURSO_AUTH_TOKEN='tu_token'
```

2. En tus values de ArgoCD/Helm:

```yaml
env:
  secret:
    create: false
    existingSecretName: python-api-turso
    existingSecretKey: TURSO_AUTH_TOKEN
```

Asi el token no queda en `values.yaml` ni en el repo.

## Ejecutar tests

```bash
pytest -q
```

La configuración de `pytest` ya incluye `pythonpath = .` en `pytest.ini`, por lo que no necesitas exportar `PYTHONPATH` manualmente.

## Tipos de tests incluidos

- `tests/domain/`: tests unitarios de dominio
- `tests/application/`: tests unitarios de casos de uso
- `tests/infrastructure/`: tests de repositorio SQLAlchemy (integración)
- `tests/test_main.py`: tests de API end-to-end
- `tests/test_architecture.py`: reglas de arquitectura (dependencias por capa)

## Notas

- La tabla `tasks` se crea automáticamente en startup.
- Si no instalas dependencias de Turso y usas `libsql://`, el servicio mostrará un error claro indicando instalar `requirements-turso.txt`.
