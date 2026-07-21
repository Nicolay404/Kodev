# Casos de Uso — Sistema de Atención Médica Remota (SAMR)

> **Proyecto:** SAMR — Sistema de Atención Médica Remota  
> **Equipo:** Kodev | UTPL — Ingeniería de Requisitos · 1er Bimestre  
> **Versión:** 2.1 ajustada | Mayo 2026  
> **Base de ajuste:** Se mantienen los 5 módulos originales de la macrocadena de valor y se corrigen los flujos para que representen procesos de negocio, sin convertir detalles técnicos internos en pasos del caso de uso.
>
> **Criterio aplicado en los flujos:** el resultado o sustantivo principal con el que termina un paso inicia el siguiente paso, para mantener continuidad lógica del proceso.  
> Ejemplo: **solicitud registrada** → **solicitud registrada validada** → **solicitud validada evaluada** → **caso asignado atendido**.
>
> **Convenciones UML:**
> - `«include»` → comportamiento obligatorio para completar el caso de uso.
> - `«extend»` → comportamiento opcional, condicionado o complementario.

---

## Actores del Proceso

| Actor | Tipo | Descripción |
|---|---|---|
| **Paciente** | Principal | Usuario en atención domiciliaria que solicita ayuda, reporta síntomas, recibe atención o es monitoreado remotamente. |
| **Familiar del Paciente** | Secundario | Persona autorizada que puede apoyar, registrar una solicitud en representación del paciente o recibir notificaciones permitidas. |
| **Consorcio SAMR** | Principal / organizacional | Conjunto de centros participantes que coordina la validación, evaluación, priorización, asignación e intercambio asistencial. |
| **Centro Médico** | Principal / organizacional | Hospital, clínica o subcentro participante que recibe casos, aporta profesionales y comparte información clínica autorizada. |
| **Profesional de la Salud** | Principal | Médico, enfermero o paramédico que recibe, atiende, orienta, registra evolución y cierra casos clínicos. |
| **Enfermero / Paramédico** | Secundario | Personal de soporte para emergencias, primeros auxilios, atención humana especializada o posible derivación presencial. |
| **Administrador TI** | Secundario | Responsable del soporte operativo, incorporación controlada de centros, dispositivos o modelos, según corresponda. |
| **MSP** | Externo | Ministerio de Salud Pública del Ecuador, relacionado con regulación, auditoría e interoperabilidad. |
| **IESS** | Externo | Instituto Ecuatoriano de Seguridad Social, relacionado con intercambio de información clínica. |
| **SPDP** | Externo | Superintendencia de Protección de Datos Personales, relacionada con auditoría y cumplimiento de privacidad. |

---

# Módulo 1 — Módulo de Solicitud

## CU-01: Paciente: Solicitar atención médica de forma multimodal

**Actor principal:** Paciente  
**Actores secundarios:** Familiar del Paciente, Consorcio SAMR, Centro Médico

```text
Paciente: Solicitar atención
    «include» Paciente: Registrar síntomas
    «include» Consorcio SAMR: Verificar usuario registrado o representación autorizada
    «include» Paciente: Confirmar consentimiento para uso de información clínica
    «extend»  Familiar del Paciente: Registrar solicitud
    «extend»  Paciente: Reportar síntomas
    «extend»  Dispositivo de monitoreo: Enviar datos biomédicos
```

---



# Módulo 2 — Módulo de Evaluación y Asignación

## CU-02: Consorcio SAMR: Evaluar y asignar solicitud de atención

**Actor principal:** Consorcio SAMR  
**Actores secundarios:** Paciente, Centro Médico, Profesional de la Salud, Enfermero / Paramédico, agentes de IA

```text
Consorcio SAMR: Evaluar y asignar solicitud de atención
    «include» Agentes de IA: Realizar triage de la solicitud
    «include» Agentes de IA: Clasificar nivel de riesgo
    «include» Agentes de IA: Asignar centro médico y profesional disponible
    «include» Agentes de IA: Fundamentar Sugerencias de acción
Agentes de IA: Trasladar caso a profsional de la salud
Profesional de la Salud: Tomar control del caso
    «include» Realizar triage de la solicitud
    «include» Clasificar nivel de riesgo
    «include» Asignar centro médico y profesional disponible
Enfermero / Paramédico: Recibir escalamiento por caso crítico //FLUJO ALTERNO
Paciente: Recibir confirmación y seguimiento de asignación
```

---



# Módulo 3 — Módulo de Atención y Operación

## CU-03: Profesional de la Salud: Brindar atención médica remota

**Actor principal:** Profesional de la Salud  
**Actores secundarios:** Paciente, Familiar del Paciente, Enfermero / Paramédico, Centro Médico

```text
Centro Médico:Recibir Asignación de caso
    «include» Profesional de la Salud: Atender el caso asignado
    «include» Profesional de la Salud: Realizar teleconsulta o atención remota según prioridad
    «include» Profesional de la Salud: Supervisar datos médicos
Paciente: Recibir guías de primeros auxilios mediante bot
    «include» paramedico: atender caso asignado
Paramédico: Recibir asignación de caso
    «include» paramedico: atender caso asignado

```

---


# Módulo 4 — Módulo de Seguimiento y Continuidad Asistencial

## CU-04: Profesional de la Salud: Gestionar seguimiento y cierre del caso clínico

**Actor principal:** Profesional de la Salud  
**Actores secundarios:** Paciente, MSP, SPDP

```text
Profesional de la Salud: Gestionar seguimiento y cierre del caso clínico
    «include» Profesional de la Salud: Registrar evolución del paciente
    «include» Profesional de la Salud: Actualizar estado clínico del caso
    «include» Profesional de la Salud: Cerrar caso y generar resumen clínico
Paciente: Recibir notificación de cambio de estado autorizado
MSP / SPDP: Revisar interacciones y decisiones registradas
```



# Módulo 5 — Módulo de Integración a Consorcio

## CU-05: Centro Médico: Integrarse al consorcio e intercambiar información clínica

**Actor principal:** Centro Médico  
**Actores secundarios:** Consorcio SAMR, Administrador TI, MSP, IESS, SPDP

```text
Centro Médico: Integrarse al consorcio
    «include» Centro Médico: Solicitar incorporación al consorcio
    «include» Consorcio SAMR: Verificar condiciones de participación del centro
    «include» Centro Médico: Intercambiar información clínica autorizada
    «extend»  MSP / IESS: Intercambiar información clínica autorizada
    «extend»  SPDP: Revisar cumplimiento de privacidad y consentimiento
    «extend»  Administrador TI: Incorporar nuevos dispositivos médicos o modelos de IA controlados
```

---
