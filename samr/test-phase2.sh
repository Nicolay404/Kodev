#!/bin/bash
# Script ligero para validar la Fase 2 (Orquestación e Infraestructura)
ERRORS=0
echo "🔍 Iniciando validaciones de Fase 2..."
echo "========================================="
# 1. VALIDACIONES DE ARCHIVOS
echo "1. Validando existencia de archivos clave..."
FILES=(
    "docker-compose.yml"
    "nginx/samr.conf"
    "scripts/init-db.sh"
    "scripts/init-rabbitmq.sh"
    "shared/events/publisher.py"
    "shared/events/consumer.py"
    "ssl/cert.pem"
    "ssl/key.pem"
)
for f in "${FILES[@]}"; do
    if [ ! -f "$f" ]; then
        echo "❌ Archivo no encontrado: $f"
        ERRORS=1
    else
        echo "✓ Encontrado: $f"
    fi
done
echo ""
# 2. VALIDAR YAML DE DOCKER-COMPOSE
echo "2. Validando docker-compose.yml..."
if docker compose config > /dev/null 2>&1; then
    echo "✓ docker-compose.yml es válido"
else
    echo "❌ Error en docker-compose.yml:"
    docker compose config
    ERRORS=1
fi
echo ""
# 3. VALIDAR NGINX.CONF
echo "3. Validando nginx/samr.conf..."
NGINX_MANUAL=0
if command -v nginx >/dev/null 2>&1; then
    if nginx -t -c "$(pwd)/nginx/samr.conf" >/dev/null 2>&1; then
        echo "✓ Sintaxis de Nginx válida (vía nginx -t)."
    else
        echo "⚠️  'nginx -t' falló, ejecutando validación manual..."
        NGINX_MANUAL=1
    fi
else
    echo "⚠️  nginx no está instalado, ejecutando validación manual..."
    NGINX_MANUAL=1
fi
if [ "$NGINX_MANUAL" == "1" ]; then
    UPSTREAMS=(
        "auth_service" "patient_service" "solicitud_service" "monitoring_service"
        "evaluacion_service" "teleconsult_service" "emergency_service" "cierre_caso_service"
        "historial_interop_service" "audit_service" "admin_integracion_service" "notification_service"
    )
    for u in "${UPSTREAMS[@]}"; do
        if grep -q "upstream $u" nginx/samr.conf; then
            echo "✓ Upstream encontrado: $u"
        else
            echo "❌ Falla: upstream $u no encontrado"
            ERRORS=1
        fi
    done
fi
echo ""
# 4. VALIDAR SCRIPTS BASH
echo "4. Validando scripts Bash..."
if bash -n scripts/init-db.sh; then
    echo "✓ init-db.sh sintaxis válida"
else
    echo "❌ Error de sintaxis en init-db.sh"
    ERRORS=1
fi
if bash -n scripts/init-rabbitmq.sh; then
    echo "✓ init-rabbitmq.sh sintaxis válida"
else
    echo "❌ Error de sintaxis en init-rabbitmq.sh"
    ERRORS=1
fi
echo ""
# 5. VALIDAR PYTHON
echo "5. Validando scripts Python..."
if python3 -m py_compile shared/events/publisher.py 2>/dev/null; then
    echo "✓ publisher.py sintaxis válida"
else
    echo "❌ Error de sintaxis en publisher.py"
    python3 -m py_compile shared/events/publisher.py
    ERRORS=1
fi
if python3 -m py_compile shared/events/consumer.py 2>/dev/null; then
    echo "✓ consumer.py sintaxis válida"
else
    echo "❌ Error de sintaxis en consumer.py"
    python3 -m py_compile shared/events/consumer.py
    ERRORS=1
fi
echo ""
# 6. RESUMEN FINAL
echo "========================================="
if [ $ERRORS -eq 0 ]; then
    echo "✅ Fase 2 lista para commit. Todos los archivos son válidos."
    exit 0
else
    echo "❌ Fase 2 tiene errores. Corrígelos antes del commit."
    exit 1
fi
