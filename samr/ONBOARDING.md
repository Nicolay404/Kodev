# Guía de Onboarding para Desarrolladores (SAMR)

¡Bienvenido al equipo de desarrollo de SAMR! Esta guía te ayudará a configurar tu entorno local rápidamente para que puedas comenzar a escribir código (ya sea en el Backend, Inteligencia Artificial, o Frontend).

La arquitectura base (Fase 3) ya está completamente construida. Consiste en 12 microservicios independientes, un API Gateway (Nginx), RabbitMQ para eventos y PostgreSQL para persistencia.

---

## 1. Prerrequisitos

Antes de clonar el proyecto, asegúrate de tener instaladas las siguientes herramientas en tu máquina:

- **Git**
- **Docker** y **Docker Compose** (Indispensable para orquestar las bases de datos y microservicios).
- **Python 3.12+** (Para ejecutar tests locales o scripts fuera de los contenedores).
- **Node.js 20+** (Solo si eres desarrollador Frontend).

---

## 2. Clonar el repositorio y configurar el entorno

1. **Clona el repositorio:**
   ```bash
   git clone https://github.com/Nicolay404/Kodev.git
   cd Kodev/samr
   ```

2. **Cambia a la rama principal (o crea la tuya):**
   ```bash
   # Asegúrate de estar en main (o crea tu rama de feature)
   git checkout main
   git pull origin main
   git checkout -b feature/nombre-de-tu-tarea
   ```

3. **Configura las variables de entorno:**
   El proyecto utiliza credenciales locales para desarrollo. Copia el archivo de ejemplo para crear tu `.env` local (este archivo no se subirá a GitHub por seguridad).
   ```bash
   cp .env.example .env
   ```
   *(Nota: Puedes dejar las credenciales que vienen por defecto en el `.env.example` para desarrollo local).*

---

## 3. Inicializar el Clúster Local (Docker)

No necesitas instalar PostgreSQL o RabbitMQ en tu computadora. Todo está contenedorizado.

1. **Construye las imágenes e inicia los contenedores en segundo plano:**
   Esto descargará las imágenes de Python, construirá los 12 microservicios y levantará el clúster. La primera vez puede tardar unos minutos.
   ```bash
   docker-compose up -d --build
   ```

2. **Verifica que los contenedores estén corriendo:**
   ```bash
   docker ps
   ```
   Deberías ver `samr-postgres`, `samr-rabbitmq`, `samr-nginx`, `samr-bff` y todos los servicios internos (ej. `samr-auth`, `samr-patient`).

---

## 4. Inicializar las Bases de Datos y Colas

Una vez que los contenedores están corriendo, debes ejecutar los scripts de inicialización. Esto creará los esquemas aislados para cada microservicio y configurará los tópicos (exchanges) en RabbitMQ.

1. **Crear las bases de datos (solo la primera vez):**
   ```bash
   DATABASES=("auth_db" "patient_db" "solicitud_db" "monitoring_db" "evaluacion_db" "teleconsult_db" "emergency_db" "cierre_db" "historial_db" "audit_db" "admin_db")
   for db in "${DATABASES[@]}"; do
       docker exec -e PGPASSWORD=samr_postgres_password samr-postgres psql -U samr -c "CREATE DATABASE $db OWNER samr ENCODING 'UTF8';" || true
   done
   ```

2. **Ejecutar migraciones (Django):**
   ```bash
   SERVICES=("samr-auth" "samr-patient" "samr-solicitud" "samr-monitoring" "samr-evaluacion" "samr-teleconsult" "samr-emergency" "samr-cierre-caso" "samr-historial-interop" "samr-audit" "samr-admin-integracion")
   for svc in "${SERVICES[@]}"; do
       docker exec $svc python manage.py migrate
   done
   ```

3. **Inicializar topología de RabbitMQ:**
   ```bash
   docker exec samr-nginx sh /tmp/init-rabbitmq.sh
   # Si falla, simplemente ejecútalo desde tu host si tienes curl instalado:
   # ./scripts/init-rabbitmq.sh
   ```

---

## 5. Flujo de Trabajo (Cómo programar)

El código fuente en tu máquina está mapeado a los contenedores (volúmenes de Docker no aplicados estrictamente en prod, pero listos para dev).

### Si eres Desarrollador Backend:
- Abre la carpeta `services/{nombre-del-servicio}/`.
- Escribe tu código (modelos, vistas, tareas Celery).
- Para ver los cambios reflejados, reinicia el contenedor específico:
  ```bash
  docker-compose restart {nombre-del-servicio}
  # Ejemplo: docker-compose restart evaluacion-service
  ```
- Para ver los logs y depurar errores:
  ```bash
  docker logs -f samr-evaluacion
  ```

### Si eres Desarrollador Frontend:
- El único puerto expuesto de nuestro Backend hacia tu aplicación web es el del **API Gateway (Nginx)** en el puerto `80 / 443` y el **BFF Service** en el `8000`.
- Configura tu cliente HTTP (Axios/Fetch) para que apunte a `http://localhost/api/...` o `http://localhost:8000/dashboard/`.

### Si necesitas crear un nuevo evento (RabbitMQ):
1. Usa la función compartida `publicar_evento(routing_key, payload)` ubicada en `samr/shared/events/publisher.py`.
2. Actualiza el archivo `ARCHITECTURE.md` para documentar qué servicio produce y consume el evento.

---

## 6. Apagar el Entorno

Al finalizar tu jornada de trabajo, es recomendable apagar los contenedores para liberar memoria en tu máquina:

```bash
docker-compose down
```
*(Nota: Al usar `down`, no pierdes la información de la base de datos, ya que está guardada de forma persistente en un volumen de Docker `samr_pgdata`).*

¡Éxito con tu desarrollo!

---

## Backend — URL local de RabbitMQ

El vhost raíz `/` debe declararse codificado como `%2F` para que la misma URL funcione en Celery y Pika:

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F
```

## Backend — Ejecutar pruebas

Desde `samr/`, ejecuta pytest dentro del contenedor del servicio que quieras validar:

```bash
docker compose exec auth-service python -m pytest -q
```

## Backend — cifrado de datos de paciente

`patient-service` requiere `PATIENT_DATA_KEY`. El valor de `.env.example` es exclusivamente local; genera una clave Fernet propia para ambientes compartidos o productivos.

## Backend — simuladores MVP

`MVP_FAQ_CONFIDENCE_THRESHOLD` controla el umbral de recuperación FAQ y `MVP_CONSORTIUM_OUTCOME` permite simular `validated`, `rejected` o `timeout`. Redis conserva respuestas FAQ durante 60 segundos mediante `REDIS_URL`. Estas opciones solo sustituyen integraciones externas durante el MVP.

Para IoT, registra primero el dispositivo mediante M4 y usa `MVP_DEVICE_SERVICE_TOKEN` como `X-Service-Token`. `MVP_VITAL_THRESHOLDS` contiene reglas técnicas simuladas; no son parámetros clínicos de producción.

M2 usa `MVP_DEFAULT_RISK_LEVEL` y listas opcionales `MVP_CRITICAL_TERMS`/`MVP_HIGH_TERMS`. El resultado incluye trazabilidad `mvp_rules` y `clinical_validation=false`.

M3 genera una guía de seguridad no clínica desde `MVP_FIRST_AID_GUIDE`; la guía predeterminada solo pide contactar a emergencias y seguir al personal autorizado.

M4 compone localmente un Bundle FHIR y verifica `consent_sharing` por M2M usando `PATIENT_SERVICE_URL`; no transmite datos a MSP/IESS en el modo MVP.

La validación de centros usa `MVP_CENTER_VALIDATION_OUTCOME=validated|rejected`. `serial_number` se transporta en el evento de alta, pero no se persiste porque no forma parte del esquema `devices` aprobado.

La tarea `validate_center_m2m` se ejecuta con Celery; el broker es el mismo `RABBITMQ_URL` del resto del backend.

Para el BFF local usa `BFF_ALLOWED_ORIGINS=http://localhost:3000` y `VERIFY_GATEWAY_TLS=false`. En ambientes compartidos debe ser `true`.

`MVP_NOTIFICATION_BACKEND=log` conserva notificaciones como simulación trazable. Para probar el flujo deben estar activos tanto `notification-service` como `notification-consumer`.

## Backend — arranque automático vigente del MVP

El comando vigente desde `samr/` es:

```bash
docker compose up -d --build
```

En la primera ejecución, PostgreSQL monta `scripts/init-db.sh` y crea exactamente las 11 bases. Cada API aplica sus migraciones automáticamente antes de iniciar Daphne o Gunicorn. Los consumidores crean sus colas quorum, bindings y DLQ al conectarse; `scripts/init-rabbitmq.sh` queda disponible para una declaración administrativa explícita, pero no es requisito del arranque local.

Los workers Celery de solicitud, evaluación, historial, auditoría, administración y notificaciones usan colas separadas y concurrencia 1 en el MVP. Para inspeccionar todos los procesos:

```bash
docker compose ps
```

Las dependencias incorporadas son `celery==5.3.6` para `admin-integracion-service` y `redis==5.0.3` para `solicitud-service` e `historial-interop-service`; se instalan al reconstruir las imágenes.

---

## 7. Instrucciones para Levantar el Entorno (Base de Datos)

De acuerdo a las últimas actualizaciones de la arquitectura (Fase 3 / v4.0), la inicialización de las bases de datos y la ejecución de las migraciones se realizan siguiendo estos pasos:

1. **Asegurar variables de entorno:**
   Verifica que tienes el archivo `.env` configurado en la raíz de `samr/` (como se indica en la sección 2). Asegúrate de tener `POSTGRES_USER=samr` y `DB_PASSWORD` / `PGPASSWORD` definidos de forma local.

2. **Levantar Docker Compose:**
   Levanta la red de contenedores, en particular la base de datos:
   ```bash
   docker-compose up -d --build
   ```
   *Nota 1: En el primer arranque, PostgreSQL ejecutará internamente el script `scripts/init-db.sh` mapeado en su volumen de inicialización (`docker-entrypoint-initdb.d`). Este script aprovisionará las 11 bases de datos aisladas y aplicará las reglas DDL de seguridad e inmutabilidad directamente desde el motor de la base de datos (ej. creación de los schemas con el tipo de dato JSONB, cifrado BYTEA, UUID, y la aplicación estricta de `REVOKE UPDATE, DELETE` en `audit_log`).*
   *Nota 2: La configuración del `docker-compose.yml` ya incluye el uso correcto del alias de red `postgres` y la definición explícita de `DB_HOST=samr-postgres` para garantizar la conexión entre los servicios backend y la base de datos de manera aislada.*

3. **Ejecutar las migraciones de Django:**
   Si bien el script de BD inicializa la estructura de las tablas obligatorias asegurando las reglas DDL de negocio, los microservicios continúan aplicando sus migraciones con el ORM automáticamente durante su arranque. Para lanzar las migraciones manualmente en todo el cluster si necesitas resincronizar sin destruir el volumen, puedes usar:
   ```bash
   SERVICES=("samr-auth" "samr-patient" "samr-solicitud" "samr-monitoring" "samr-evaluacion" "samr-teleconsult" "samr-emergency" "samr-cierre-caso" "samr-historial-interop" "samr-audit" "samr-admin-integracion")
   for svc in "${SERVICES[@]}"; do
       docker exec $svc python manage.py migrate --noinput
   done
   ```

4. **Creación de Superusuario Django (Opcional):**
   La base de datos se inicializa y las migraciones se aplican automáticamente, por lo que este paso **solo es necesario si requieres acceder al panel de administración de Django (`/admin`)**.
   ```bash
   docker exec -it samr-auth python manage.py createsuperuser
   ```
   *Nota: Si estás ejecutando esto en entornos Windows o Git Bash, el comando anterior puede fallar por la falta de una terminal interactiva (TTY). En ese caso, debes anteponer `winpty`:*
   ```bash
   winpty docker exec -it samr-auth python manage.py createsuperuser
   ```
