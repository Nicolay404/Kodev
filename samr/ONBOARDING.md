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
