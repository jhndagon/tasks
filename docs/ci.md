# Integración continua (GitHub Actions)

El workflow `.github/workflows/ci.yml` valida que el proyecto siga funcionando antes de integrar cambios.

## Cuándo se ejecuta

Se ejecuta en estos eventos:

- Pull requests hacia `main` o `develop`.
- Pushes directos a `main` o `develop`.

Para pull requests, corre cuando el PR se abre, reabre, actualiza con nuevos commits, pasa a estado listo para revisión o se edita.

## Control de concurrencia

El workflow usa `concurrency` con el grupo `ci-${{ github.workflow }}-${{ github.ref }}`.

Esto evita que queden varias ejecuciones antiguas corriendo para la misma rama o referencia. Si llega un nuevo commit mientras hay una ejecución en curso, GitHub Actions cancela la anterior y conserva la más reciente.

## Job principal

El job `tests` se muestra como `Tests (Python 3.11)` y corre en `ubuntu-latest`.

Tiene un tiempo máximo de 10 minutos. Si la instalación o los tests se quedan bloqueados, GitHub Actions detiene el job automáticamente.

## Pasos del workflow

1. `Checkout`: descarga el código del repositorio usando `actions/checkout@v4`.
2. `Setup Python`: instala Python 3.11 con `actions/setup-python@v5`.
3. `Install dependencies`: actualiza `pip` e instala las dependencias de desarrollo desde `requirements-dev.txt`.
4. `Run test suite`: ejecuta `pytest -q`.

El paso de Python habilita caché de `pip` y usa como referencia `requirements.txt` y `requirements-dev.txt`. Cuando estas dependencias no cambian, las ejecuciones siguientes pueden instalar más rápido.

## Política de ramas comentada

El archivo conserva un bloque comentado para validar el flujo de ramas:

- PRs hacia `main` desde ramas `release/*`.
- PRs hacia `develop` desde ramas `feature/*`.

Actualmente esa validación está deshabilitada porque todo el bloque está comentado. Sirve como referencia si más adelante se quiere volver a imponer esa política desde CI.

## Resultado esperado

La ejecución pasa correctamente cuando todas las dependencias se instalan y `pytest -q` finaliza sin errores.

Si falla, el PR o commit queda marcado con error en GitHub Actions y se debe revisar el log del paso que falló, normalmente `Install dependencies` o `Run test suite`.

## Job de seguridad

El job `security` se muestra como `Security scans` y ejecuta controles complementarios:

1. Instala dependencias del proyecto.
2. Ejecuta `pip-audit` contra `requirements.txt` y `requirements-dev.txt`.
3. Ejecuta Snyk si el repositorio tiene configurado el secret `SNYK_TOKEN`.
4. Ejecuta SonarQube si existen `SONAR_TOKEN` y `SONAR_HOST_URL`.

La configuracion de SonarQube esta en `sonar-project.properties`. El analisis usa `app` como codigo fuente y `tests` como suite de pruebas.

Secrets requeridos para escaneos externos:

- `SNYK_TOKEN`
- `SONAR_TOKEN`
- `SONAR_HOST_URL`
