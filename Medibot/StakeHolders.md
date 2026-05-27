# Matriz de Stakeholders, Roles e Impacto en el SAMR

A continuación se presenta la clasificación corregida y validada arquitectónicamente de los stakeholders del Sistema de Atención Médica Remota (SAMR).

---

# CRITERIO DE CLASIFICACIÓN UTILIZADO

## Directo
Stakeholders que:
- ofrecen directamente el servicio médico,
- participan activamente en la atención clínica,
- ejecutan procesos operacionales del sistema.

---

## Indirecto
Stakeholders que:
- reciben beneficios del sistema,
- utilizan el ecosistema de atención,
- o participan de forma secundaria dentro de la cadena de valor.

---

## Ecosistema
Stakeholders externos que:
- regulan,
- supervisan,
- integran,
- auditan,
- o habilitan el funcionamiento institucional y tecnológico del sistema.

---


---

# Matriz de Stakeholders  

| Categoría      | Stakeholder                                              | Rol e Impacto en el SAMR                                                                                                                          |
| -------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Directo**    | Profesionales de la Salud                                | Médicos y especialistas que realizan evaluación clínica, atención y toma de decisiones médicas.                                                   |
| **Directo**    | Enfermeros y Paramédicos                                 | Personal clínico que participa directamente en atención de urgencias y soporte asistencial.                                                       |
|                |                                                          |                                                                                                                                                   |
| **Indirecto**  | Pacientes                                                | Reportan síntomas, reciben monitoreo, atención y seguimiento mediante el sistema.                                                                 |
| **Indirecto**  | Familiares del Paciente                                  | Reciben alertas, seguimiento y notificaciones preventivas.                                                                                        |
| **Indirecto**  | Centros de Asistencia Médica                             | Hospitales públicos y privados, clínicas,  subcentros y consultorios privados que utilizan el sistema para coordinar atención y recursos médicos. |
| **Indirecto**  | Equipos de MLOps / NLP                                   | Mantienen y optimizan modelos inteligentes utilizados en monitoreo y procesamiento conversacional.                                                |
| **Indirecto**  | Kodev                                                    | Equipo multidisciplinario responsable del desarrollo del SAMR.                                                                                    |
| **Indirecto**  | Soporte TI                                               | Equipo responsable del  mantenimiento y evolución del SAMR.                                                                                       |
|                |                                                          |                                                                                                                                                   |
| **Ecosistema** | MSP                                                      | Participa en regulación, interoperabilidad y supervisión institucional.                                                                           |
| **Ecosistema** | IESS                                                     | Participa en integración e intercambio de información clínica.                                                                                    |
| **Ecosistema** | Red de Salud Pública y Centros Participantes (Consorcio) | Facilitan interoperabilidad y coordinación interinstitucional.                                                                                    |
| **Ecosistema** | Proveedores Externos de IA                               | Proveen servicios externos de inferencia o soporte inteligente para centros médicos.                                                              |
| **Ecosistema** | Delegado de Protección de Datos (SPDP)                   | Supervisa cumplimiento relacionado con privacidad y protección de datos clínicos.                                                                 |


---

# INCONSISTENCIAS EVITADAS

Se evitó incorrectamente:
- modelar el sistema SAMR como stakeholder,
- incluir infraestructura técnica como actor organizacional,
- inventar farmacia y laboratorios no descritos,
- introducir entidades tributarias inexistentes,
- mezclar operación clínica con componentes tecnológicos internos.

---