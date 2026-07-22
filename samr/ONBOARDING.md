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

## Backend - URL local de RabbitMQ

El vhost raíz `/` debe declararse codificado como `%2F` para que la misma URL funcione en Celery y Pika:

```env
RABBITMQ_URL=amqp://guest:guest@rabbitmq:5672/%2F
```

## Backend - Ejecutar pruebas

Desde `samr/`, ejecuta pytest dentro del contenedor del servicio que quieras validar:

```bash
docker compose exec auth-service python -m pytest -q
```

## Backend - cifrado de datos de paciente

`patient-service` requiere `PATIENT_DATA_KEY`. El valor de `.env.example` es exclusivamente local; genera una clave Fernet propia para ambientes compartidos o productivos.

## Backend - simuladores MVP

`MVP_FAQ_CONFIDENCE_THRESHOLD` controla el umbral de recuperación FAQ y `MVP_CONSORTIUM_OUTCOME` permite simular `validated`, `rejected` o `timeout`. Redis conserva respuestas FAQ durante 60 segundos mediante `REDIS_URL`. Estas opciones solo sustituyen integraciones externas durante el MVP.

Para IoT, registra primero el dispositivo mediante M4 y usa `MVP_DEVICE_SERVICE_TOKEN` como `X-Service-Token`. `MVP_VITAL_THRESHOLDS` contiene reglas técnicas simuladas; no son parámetros clínicos de producción.

M2 usa `MVP_DEFAULT_RISK_LEVEL` y listas opcionales `MVP_CRITICAL_TERMS`/`MVP_HIGH_TERMS`. El resultado incluye trazabilidad `mvp_rules` y `clinical_validation=false`.

M3 genera una guía de seguridad no clínica desde `MVP_FIRST_AID_GUIDE`; la guía predeterminada solo pide contactar a emergencias y seguir al personal autorizado.

M4 compone localmente un Bundle FHIR y verifica `consent_sharing` por M2M usando `PATIENT_SERVICE_URL`; no transmite datos a MSP/IESS en el modo MVP.

La validación de centros usa `MVP_CENTER_VALIDATION_OUTCOME=validated|rejected`. `serial_number` se transporta en el evento de alta, pero no se persiste porque no forma parte del esquema `devices` aprobado.

La tarea `validate_center_m2m` se ejecuta con Celery; el broker es el mismo `RABBITMQ_URL` del resto del backend.

Para el BFF local usa `BFF_ALLOWED_ORIGINS=http://localhost:3000` y `VERIFY_GATEWAY_TLS=false`. En ambientes compartidos debe ser `true`.

`MVP_NOTIFICATION_BACKEND=log` conserva notificaciones como simulación trazable. Para probar el flujo deben estar activos tanto `notification-service` como `notification-consumer`.

## Backend - arranque automático vigente del MVP

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
   *Nota 1: En el primer arranque, PostgreSQL ejecutará internamente `scripts/init-db.sh` para aprovisionar las 11 bases aisladas. Cada servicio crea y evoluciona sus propias tablas mediante migraciones Django; las reglas de motor, como la inmutabilidad de auditoría, también se instalan mediante la migración versionada del servicio propietario.*
   *Nota 2: La configuración del `docker-compose.yml` ya incluye el uso correcto del alias de red `postgres` y la definición explícita de `DB_HOST=samr-postgres` para garantizar la conexión entre los servicios backend y la base de datos de manera aislada.*

3. **Ejecutar las migraciones de Django:**
   Los microservicios aplican automáticamente las migraciones de su base durante el arranque. Para lanzarlas manualmente en todo el clúster si necesitas resincronizar sin destruir el volumen, puedes usar:
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

## Backend - API de notificaciones del MVP

El contenedor `notification-service` atiende HTTP en el puerto interno `8012`; `notification-consumer` recibe eventos y `notification-worker` los procesa. Nginx publica la bandeja en `GET /api/notifications/` y permite marcar entradas mediante `PATCH /api/notifications/{id}/read/`.

Las entradas viven en Redis por 24 horas, con un máximo de 100 por usuario. Las dependencias nuevas del servicio son `djangorestframework==3.15.2`, `PyJWT==2.8.0`, `cryptography==42.0.5` y `gunicorn==21.2.0`; Docker las instala al reconstruir la imagen.

## Backend - levantar el entorno con Supabase

Supabase se usa como PostgreSQL administrado. El sistema no delega el login a Supabase Auth: `auth-service` lee `auth_db.auth_user`, valida el hash Django y emite los JWT RS256 definidos por la arquitectura.

1. Crea `samr/.env` con `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER` y `DB_PASSWORD`. No copies esos valores a archivos versionados.
2. Para una conexión directa de Supabase, Docker Desktop debe tener salida IPv6. El override habilita IPv6 en `samr-net` y fuerza SSL.
3. Inicia desde `samr/`:

   ```bash
   docker compose --env-file .env -f docker-compose.yml -f docker-compose.supabase.yml up -d --build
   ```

4. Verifica el inicializador y los servicios:

   ```bash
   docker compose --env-file .env -f docker-compose.yml -f docker-compose.supabase.yml ps -a
   docker compose --env-file .env -f docker-compose.yml -f docker-compose.supabase.yml logs supabase-init
   ```

`supabase-init` crea idempotentemente los once schemas documentados. Cada servicio configura `DB_SCHEMA_MODE=schema`, su `DB_SCHEMA` exclusivo, `DB_SSLMODE=require` y adopta tablas existentes mediante `migrate --fake-initial --noinput`. No borres schemas ni ejecutes `down -v` para resolver problemas de conexión.

Para volver al PostgreSQL local se omite `docker-compose.supabase.yml` y se usan los valores locales de `.env.example`.

## Backend - credenciales de prueba y restablecimiento

Las seis cuentas precargadas en Supabase comparten la contraseña temporal `Demo1234` para la demostración:

| Correo | Rol |
|---|---|
| `paciente.juan@gmail.com` | Paciente (`patient`) |
| `paciente.maria@gmail.com` | Paciente (`patient`) |
| `user@prueba1.com` | Paciente (`patient`) |
| `dr.mendoza@samr-salud.gob.ec` | Profesional (`professional`) |
| `admin.sistema@samr-salud.gob.ec` | Administrador SAMR (`system_admin`) |
| `delegado.dpd@samr-salud.gob.ec` | Delegado DPD (`dpd_delegate`) |

Si necesitas volver a generar los hashes o desbloquear las cuentas, ejecuta desde `samr/`:

```bash
docker compose --env-file .env -f docker-compose.yml -f docker-compose.supabase.yml run --rm --no-deps auth-service python manage.py reset_demo_passwords --password Demo1234
```

El procedimiento modifica solamente esas cuentas existentes, no crea datos nuevos y cancela todos los cambios si falta alguna. `Demo1234` es una clave conocida para el MVP; nunca debe usarse en un entorno productivo.
