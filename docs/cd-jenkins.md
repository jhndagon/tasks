# Pipeline CD con Jenkins

El archivo `Jenkinsfile` define un pipeline de entrega continua para construir y publicar la imagen Docker del microservicio.

Este pipeline está pensado como una definición base de CD. Para ejecutarlo en un Jenkins real, el servidor debe tener Docker disponible y una credencial configurada para publicar en el registro de imágenes.

## Estructura general

El pipeline usa sintaxis declarativa de Jenkins:

- `agent any`: permite que Jenkins ejecute el pipeline en cualquier agente disponible.
- `environment`: centraliza los valores reutilizables del pipeline.
- `stages`: define las fases principales del proceso de CD.
- `post`: define acciones que se ejecutan al finalizar el pipeline.

## Variables del pipeline

El bloque `environment` define estos valores:

- `DOCKER_REGISTRY`: registro Docker donde se publicará la imagen. Actualmente usa `docker.io`.
- `DOCKER_IMAGE`: nombre completo de la imagen. Actualmente usa `jhndagon11/tasks`.
- `DOCKER_CREDENTIALS_ID`: identificador de la credencial configurada en Jenkins. Actualmente usa `dockerhub-credentials`.
- `IMAGE_TAG`: tag versionado de la imagen. Actualmente usa el número de build de Jenkins con `${env.BUILD_NUMBER}`.

Estas variables permiten cambiar el registro, repositorio o credencial sin modificar todos los stages.

## Stage: Clonar repositorio

El stage `Clonar repositorio` obtiene el código fuente del repositorio:

```groovy
checkout scm
```

`checkout scm` usa la configuración del job o del multibranch pipeline en Jenkins para clonar la rama que disparó la ejecución.

## Stage: Construir imagen Docker

El stage `Construir imagen Docker` crea la imagen Docker usando el `Dockerfile` ubicado en la raíz del proyecto:

```bash
docker build -t ${DOCKER_IMAGE}:${IMAGE_TAG} -t ${DOCKER_IMAGE}:latest .
```

La imagen se construye con dos tags:

- `${IMAGE_TAG}`: tag único asociado al número de build de Jenkins.
- `latest`: tag flotante que apunta a la última imagen publicada.

Esto permite identificar una versión específica y, al mismo tiempo, tener una referencia simple a la versión más reciente.

## Stage: Publicar imagen en registro

El stage `Publicar imagen en registro` inicia sesión en DockerHub o en el registro configurado y publica la imagen:

```bash
docker push "${DOCKER_IMAGE}:${IMAGE_TAG}"
docker push "${DOCKER_IMAGE}:latest"
```

La autenticación se realiza con `withCredentials`:

```groovy
usernamePassword(
    credentialsId: "${DOCKER_CREDENTIALS_ID}",
    usernameVariable: 'DOCKER_USERNAME',
    passwordVariable: 'DOCKER_PASSWORD'
)
```

Jenkins inyecta temporalmente el usuario y la contraseña en variables de entorno. El password se envía a `docker login` usando `--password-stdin`, evitando escribir el secreto directamente en el comando.

## Acciones posteriores

El bloque `post` contiene dos acciones:

- `always`: ejecuta `docker logout` al finalizar, incluso si el pipeline falla.
- `success`: muestra el nombre y tag de la imagen publicada cuando el pipeline termina correctamente.

## Credencial requerida en Jenkins

Para que el stage de publicación funcione, Jenkins debe tener una credencial de tipo usuario y contraseña con este ID:

```text
dockerhub-credentials
```

Esa credencial debe corresponder a una cuenta con permisos para publicar en el repositorio configurado en `DOCKER_IMAGE`.

## Resultado esperado

Cuando el pipeline finaliza correctamente:

1. Jenkins clona el repositorio.
2. Docker construye la imagen del microservicio.
3. Jenkins inicia sesión en el registro configurado.
4. Se publican los tags `${BUILD_NUMBER}` y `latest`.
5. Jenkins cierra la sesión del registro.

El resultado principal es una imagen Docker disponible en el registro configurado, lista para ser usada por un proceso posterior de despliegue.
