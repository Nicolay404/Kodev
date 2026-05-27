Guía de Modelado y Conexiones de
Diagramas de Casos de Uso (Corregido)
Lineamientos de Diseño Estructural y Arquitectura de Software
Versión: 2.0 (Consolidado y Corregido según Diccionario de Clases)
Lineado / Espaciado: 1.15
1. Convenciones y Reglas de Oro de Modelado UML
● Asociación Simple (Línea Continua): Conecta un Actor únicamente con un Caso de
Uso Base (el que inicia o en el que participa activamente).
● Relación <<include>> (Flecha Discontinua): El caso de uso origen requiere
obligatoriamente la ejecución del caso de uso destino. La flecha apunta al caso incluido.
El actor no se conecta al caso incluido.
● Relación <<extend>> (Flecha Discontinua): El caso de uso origen es una extensión
opcional o condicional del caso de uso destino. La flecha apunta al caso base. El actor
no se conecta al caso extensor.
2. Especificación de Conexiones por Módulo
Módulo 1: Solicitud de Asistencia Médica Remota
Actor / Elemento Origen Tipo de Conexión / Relación Elemento Destino
Paciente (Actor Principal) Asociación Simple CU-M1-01 Registrar paciente
Paciente (Actor Principal) Asociación Simple CU-M1-02 Iniciar sesión
Paciente (Actor Principal) Asociación Simple CU-M1-03 Solicitar asistencia
médica
Dispositivo de Monitoreo Asociación Simple CU-M1-04 Emitir alerta
(Actor Principal) automática
CU-M1-03 Solicitar asistencia <<include>> CU-M1-02 Iniciar sesión
médica
CU-M1-03 Solicitar asistencia <<include>> CU-M1-05 Registrar solicitud
médica médica
CU-M1-04 Emitir alerta <<include>> CU-M1-05 Registrar solicitud
automática médica

Módulo 2: Evaluación y Asignación del Servicio
Actor / Elemento Origen  Tipo de Conexión / Relación  Elemento Destino
Médico Tratante (Actor  Asociación Simple  CU-M2-02 Consultar historial
| Principal)  |     | clínico  |
| ----------- | --- | -------- |
Médico Tratante (Actor  Asociación Simple  CU-M2-03 Clasificar urgencia
Principal)
Administrador Clínico (Actor  Asociación Simple  CU-M2-04 Publicar oferta en
| Principal)  |     | el consorcio  |
| ----------- | --- | ------------- |
Administrador Clínico (Actor  Asociación Simple  CU-M2-05 Asignar centro del
| Principal)  |     | consorcio  |
| ----------- | --- | ---------- |
Consorcio (Sistema Externo /  Asociación Simple  CU-M2-04 Publicar oferta en
| Secundario)  |     | el consorcio  |
| ------------ | --- | ------------- |
Consorcio (Sistema Externo /  Asociación Simple  CU-M2-05 Asignar centro del
| Secundario)  |     | consorcio  |
| ------------ | --- | ---------- |
CU-M2-03 Clasificar urgencia  <<include>>  CU-M2-01 Validar solicitud
CU-M2-03 Clasificar urgencia  <<include>>  CU-M2-02 Consultar historial
clínico
CU-M2-05 Asignar centro del  <<include>>  CU-M2-06 Notificar
| consorcio  |     | asignación al paciente  |
| ---------- | --- | ----------------------- |

Módulo 3: Atención Médica Remota
Actor / Elemento Origen  Tipo de Conexión / Relación  Elemento Destino
Médico Tratante (Actor  Asociación Simple  CU-M3-01 Diagnosticar y
| Principal)  |     | registrar tratamiento  |
| ----------- | --- | ---------------------- |
Enfermero (Actor Principal)  Asociación Simple  CU-M3-03 Gestionar alerta
por valor fuera de rango
| Paramédico (Actor        | Asociación Simple  | CU-M3-04 Coordinar      |
| ------------------------ | ------------------ | ----------------------- |
| Secundario)              |                    | despacho de ambulancia  |
| CU-M3-01 Diagnosticar y  | <<include>>        | * CU-M2-02 Consultar    |
| registrar tratamiento    |                    | historial clínico       |
CU-M3-03 Gestionar alerta  <<include>>  CU-M3-02 Monitorear señales
| por valor fuera de rango  |             | médicas                  |
| ------------------------- | ----------- | ------------------------ |
| CU-M3-04 Coordinar        | <<extend>>  | CU-M3-01 Diagnosticar y  |
| despacho de ambulancia    |             | registrar tratamiento    |

Módulo 4: Gestión Financiera y Facturación
Actor / Elemento Origen Tipo de Conexión / Relación Elemento Destino
Administrador Clínico (Actor Asociación Simple CU-M4-03 Generar factura
Principal)
Paciente (Actor Principal) Asociación Simple CU-M4-04 Registrar pago
MSP / IESS (Sistema Externo Asociación Simple CU-M4-01 Verificar cobertura
/ Secundario)
CU-M4-03 Generar factura <<include>> CU-M4-02 Calcular costo del
servicio
CU-M4-02 Calcular costo del <<include>> CU-M4-01 Verificar cobertura
servicio
CU-M4-05 Habilitar pago <<extend>> CU-M4-04 Registrar pago
diferido
Módulo 5: Gestión Clínica y Seguimiento
Actor / Elemento Origen Tipo de Conexión / Relación Elemento Destino
Médico Tratante (Actor Asociación Simple CU-M5-04 Cerrar caso clínico
Principal)
Sistemas Externos / Red de Asociación Simple CU-M5-05 Intercambiar
Salud Pública (Secundario) información con sistemas
externos
CU-M5-04 Cerrar caso clínico <<include>> CU-M5-03 Evaluar evolución
del paciente
CU-M5-03 Evaluar evolución <<include>> CU-M5-02 Definir plan de
del paciente seguimiento
CU-M5-02 Definir plan de <<include>> CU-M5-01 Actualizar historial
seguimiento clínico
CU-M5-05 Intercambiar <<extend>> CU-M5-01 Actualizar historial
información con sistemas clínico
externos
Módulo T: Transversales

Actor / Elemento Origen  Tipo de Conexión / Relación  Elemento Destino
Auditor (Actor Principal)  Asociación Simple  CU-T-02 Consultar registros
de auditoría
Administrador TI (Actor  Asociación Simple  CU-T-04 Registrar incidente
Principal)
CU-T-02 Consultar registros  <<include>>  CU-T-01 Iniciar sesión
de auditoría
CU-T-04 Registrar incidente  <<include>>  CU-T-03 Monitorear
disponibilidad del servicio
| CU-T-03 Monitorear  | <<include>>  | CU-T-01 Iniciar sesión  |
| ------------------- | ------------ | ----------------------- |
disponibilidad del servicio
| CU-T-05 Incorporar nuevo  | <<extend>>  | CU-T-03 Monitorear           |
| ------------------------- | ----------- | ---------------------------- |
| dispositivo               |             | disponibilidad del servicio  |