

## Cadena de Valores

#### Cadena de Valor de Atención Ambulatoria de Emergencia

1. Módulo de Solicitud
	Paciente envía solicitud de ayuda (app móvil/web/dispositivo médico)
	Registro de usuarios al sistema SAMR en caso de que no estén

Sistema SAMR recibe solicitud

2. Módulo de Evaluación y Asignación
	Validación de identidad del paciente
        
	Consulta historial médico
	(MSP, IESS, historial interno)
	    
	Clasificación automática de prioridad
	(triage digital)
	    
	¿La emergencia es crítica?
		Posibles Respuestas (Si o no)

2. Módulo de Atención
	 ├── Sí
	 │      ↓
	 │  Activar protocolo prioritario
	 │      ↓
	 │  Asignar centro médico disponible
	 │      ↓
	 │  Despacho de ambulancia
	 │      ↓
	 │  Monitoreo en tiempo real
	 │      ↓
	 │  Llegada al paciente
	 │      ↓
	 │  Atención presencial
	 │      ↓
	 │  Registro del incidente
	 │      ↓
	 │  Cierre del caso
	 │
	 └── No
	        ↓
	Transferir a teleconsulta médica
	        ↓
	Diagnóstico remoto
	        ↓
	Tratamiento/Recomendaciones
	        ↓
	Seguimiento
	        ↓
	Registro histórico

3. Módulo de Pago
	Si (Tiene Seguro)
		Se descuenta
	Sino
		Se cobra

#### Cadena de Valor de Telemedicina

1.  Módulo de Solicitud
	Paciente solicita teleconsulta

2. Módulo de Evaluación y Asignación
	Sistema verifica disponibilidad médica  
	↓  
	Asignación de profesional  
	↓  
	Consulta historial clínico

3. Módulo de Atencion (Teleconsulta)
	Videollamada segura  
	↓  
	Evaluación médica  
	↓  
	Solicitud de datos biométricos  
	(EKG, presión, oxígeno, etc.)  
	↓  
	Recepción de datos en tiempo real  
	↓  
	Diagnóstico  
	↓  
	Prescripción médica  
	↓  
	Generación de receta digital

4. Módulo de Pago
	Validación de seguro médico
	↓
	Si (Tiene cobertura MSP/IESS/Seguro privado)
		Se registra cobertura automática
	Sino
		Se genera cobro del servicio
		

5. Módulo de Seguimiento
	↓  
	Seguimiento posterior  
	↓  
	Almacenamiento en historial clínico

#### Cadena de Valor de Atención Domiciliaria

1.  Módulo de Solicitud
	Paciente solicita atención domiciliaria

2. Módulo de Evaluación y Asignación
	Validación de identidad del paciente
        
	Consulta historial médico
	(MSP, IESS, historial interno)
	    
	Clasificación automática de prioridad
	(triage digital)
	
	¿Usario es nuevo?
		Posibles Respuestas (Si o no)
	
	Sistema verifica disponibilidad médica  
	↓  
	Asignación de profesional  
	↓  
	Consulta historial clínico

3. Módulo de Atención 
	 Si (Es nuevo)
		Registro del domicilio  
		↓  
		Instalación de dispositivos médicos  
		↓  
		Configuración de monitoreo remoto  
		↓  
		Sincronización con nube médica  
		↓  
		Monitoreo continuo  
		↓  
		Generación de alertas  
		↓  
		Evaluación médica remota
	Sino
		¿La emergencia es crítica?
			Posibles Respuestas (V o F)
				Si (V)
					Envío de personal médico  
					 ↓  
					Atención presencial
				Sino
					Continuar monitoreo  
					↓  
					Actualización del historial clínico  
					↓  
					Seguimiento continuo (Conecta con el modulo 4)


4. Módulo de Pago
	Validación de seguro médico
	↓
	Si (Tiene cobertura MSP/IESS/Seguro privado)
		Se registra cobertura automática
	Sino
		Se genera cobro del servicio
		

5. Módulo de Seguimiento
	↓  
	Seguimiento posterior  
	↓  
	Almacenamiento en historial clínico


#### Cadena de Valor de Monitoreo Médico Inteligente

1. Módulo de Solicitud:
	Generación de solicitud automático IoT (Es itinerario con el modulo 4)
	
2. Módulo de Evaluación y Asignación:
	Comparación con umbrales críticos
	¿Valores peligrosos?
	 ├── Sí
	 │      ↓
	 │  Generación automática de alerta
	 │      ↓
	 │  Notificación al centro médico
	 │      ↓
	 │  Priorización del caso

3. Módulo de Atención:
	Se realiza la atención médica

4. Módulo de Pago:
	Validación de seguro médico
	↓
	Si (Tiene cobertura MSP/IESS/Seguro privado)
		Se registra cobertura automática
	Sino
		Se genera cobro del servicio
		

5. Módulo de Seguimiento:
	Dispositivo médico captura datos
	        ↓
	Datos enviados a la nube
	        ↓
	Procesamiento en tiempo real
	        ↓
	Motor de análisis clínico
	        ↓
	Guardar métricas históricas
	        ↓
	Continuar monitoreo

#### Cadena de Valor de Gestión de Emergencias Distribuidas

1.	Módulo de Solicitud
	Paciente genera solicitud de emergencia (	Obtención de ubicación geográfica )
	↓
Sistema recibe alerta (puente al otro modulo)
	
2.	Módulo de Evaluación 
	Validación de identidad del paciente
	↓
	Consulta de historial clínico
	↓
	Clasificación automática de gravedad
	(triage digital)
	↓
	Determinación del nivel de prioridad
	↓
	Generación del caso de emergencia 
	↓
	Difusión de la solicitud a múltiples centros médicos
	↓
	Centros médicos reciben notificación
	↓
	Evaluación de disponibilidad de recursos
	(ambulancias, médicos, camas, equipos)
	↓
	Comparación de tiempos de respuesta
	↓
	Selección automática del centro óptimo
	(según cercanía, capacidad y prioridad) 
	↓
	Confirmación del centro médico asignado
	↓
	Asignación de ambulancia/personal médico
	↓
	Despacho de unidad de emergencia
	↓
	Monitoreo GPS en tiempo real
	↓
	Comunicación continua con el paciente 
	
3.	Módulo de Atención de Emergencia
	Llegada del personal médico
	↓
	Atención prehospitalaria
	↓
	Monitoreo de signos vitales
	↓
	¿Requiere hospitalización?
		Si (Requiere hospitalización)
		↓
		Traslado al hospital asignado
		↓
		Entrega formal del paciente
	Sino
		↓
		Atención domiciliaria/remota
		↓
		Alta médica temporal
		
4.	Módulo de Pago 
	Validación de seguro médico
	↓
	Si (Tiene cobertura MSP/IESS/Seguro privado)
		Se registra cobertura automática
	Sino
		Se genera cobro del servicio
		
5.	Módulo de Seguimiento
	Registro completo del incidente
	↓
	Actualización del historial clínico
	↓
	Seguimiento post emergencia


#### Cadena de Valor de Gestión de Datos Clínicos

> Módulo 1, 2 ,3 y 4 no son tan relevantes a la cadena de valor, solo siguen el formato de los otros módulos
1. Modulo de Solicitud
	Generación de solicitud del paciente
	
2. Modulo de Evaluación y Asignación
	Solicitud evaluada y asignada
	
3. Modulo Atención
	Se atiende al paciente
	
4. Modulo pago
	Validación de seguro médico
	↓
	Si (Tiene cobertura MSP/IESS/Seguro privado)
		Se registra cobertura automática
	Sino
		Se genera cobro del servicio
		
5. Modulo de seguimiento:
	Captura de información clínica
	↓
	Almacenamiento persistente
	↓
	Sincronización con sistemas externos
	(MSP, IESS, hospitales)
	↓
	Actualización del historial

#### Cadena de Valor de Gestión Económica y Facturación

1. Módulo de Solicitud:
	------------------
	
2. Módulo de Evaluación y Asignación:
	-------------------
	

3. Módulo de Atención:
	Registro de la atención que se esta brindado
	↓  
	Clasificación del tipo de atención

4. Módulo de Pago:
	Validación de cobertura  
	(seguro/MSP/IESS)  
	↓  
	Cálculo de costos  
	↓  
	Generación de factura  
	↓  
	Pago diferido o inmediato  
	↓  
	Confirmación financiera


5. Módulo de Seguimiento:

	Registro de la atención que se ha consumido



-------------------------------------------------------
### Vista Global de la Macro Cadena

1. Solicitud
        ↓
2. Evaluación y Asignación
        ↓
3. Atención Médica
        ├── Emergencia Ambulatoria
        ├── Telemedicina
        ├── Atención Domiciliaria
        ├── Monitoreo Inteligente
        └── Emergencias Distribuidas
        ↓
4. Gestión Financiera y Facturación
        ↓
5. Gestión Clínica y Seguimiento
        ↓
Retroalimentación al sistema


---  
  
# Macro Cadena Principal de Valor - SAMR
## Vista Global Simplificada de la Macro Cadena

```text
1. Solicitud
        ↓
2. Evaluación y Asignación
        ↓
3. Atención Médica
        ├── Emergencia Ambulatoria
        ├── Telemedicina
        ├── Atención Domiciliaria
        ├── Monitoreo Inteligente
        └── Emergencias Distribuidas
        ↓
4. Gestión Financiera y Facturación
        ↓
5. Gestión Clínica y Seguimiento
        ↓
Retroalimentación al sistema
```

---

## 1. Módulo de Solicitud

Este módulo centraliza todas las entradas al sistema SAMR, tanto manuales como automáticas.

## Flujo del módulo

```text
Paciente genera solicitud
(app móvil/web/dispositivo médico)
        ↓
Obtención de ubicación geográfica
        ↓
Recepción de solicitud en el sistema SAMR
        ↓
¿Tipo de solicitud?
        ├── Emergencia ambulatoria
        ├── Telemedicina
        ├── Atención domiciliaria
        ├── Emergencia distribuida
        └── Alerta automática IoT
                ↓
Generación automática/manual del caso
        ↓
Registro inicial de solicitud
```

---

## 2. Módulo de Evaluación y Asignación

Este módulo determina la prioridad, gravedad y asignación de recursos médicos.

## Flujo del módulo

```text
Validación de identidad del paciente
        ↓
Consulta de historial clínico
(MSP, IESS, historial interno)
        ↓
Consulta de elegibilidad/cobertura
        ↓
Clasificación automática de prioridad
(triage digital)
        ↓
Determinación de gravedad
        ↓
¿Solicitud crítica?
        ├── Sí
        │      ↓
        │  Activación de protocolo prioritario
        │      ↓
        │  Difusión a múltiples centros médicos
        │      ↓
        │  Evaluación de disponibilidad
        │  (ambulancias, médicos, camas, equipos)
        │      ↓
        │  Comparación de tiempos de respuesta
        │      ↓
        │  Selección automática del centro óptimo
        │      ↓
        │  Asignación de ambulancia/personal médico
        │      ↓
        │  Despacho de unidad de emergencia
        │
        └── No
                ↓
        Asignación de atención médica
                ├── Telemedicina
                ├── Atención domiciliaria
                └── Monitoreo remoto
                        ↓
                Asignación de profesional médico
```

---

## 3. Módulo de Atención Médica

Este módulo contiene la prestación real de servicios médicos del sistema SAMR.

---

## 3.1 Atención Ambulatoria de Emergencia

```text
Monitoreo GPS en tiempo real
        ↓
Llegada del personal médico
        ↓
Atención prehospitalaria
        ↓
Monitoreo de signos vitales
        ↓
¿Requiere hospitalización?
        ├── Sí
        │      ↓
        │  Traslado al hospital
        │      ↓
        │  Entrega formal del paciente
        │
        └── No
                ↓
        Atención domiciliaria/remota
                ↓
        Alta médica temporal
```

---

## 3.2 Telemedicina

```text
Inicio de videollamada médica
        ↓
Evaluación médica remota
        ↓
Solicitud de datos biométricos
(EKG, presión, oxígeno, etc.)
        ↓
Recepción de datos en tiempo real
        ↓
Diagnóstico remoto
        ↓
Prescripción médica
        ↓
Generación de receta digital
```

---

## 3.3 Atención Domiciliaria

```text
Registro del domicilio
        ↓
Instalación de dispositivos médicos
        ↓
Configuración de monitoreo remoto
        ↓
Sincronización con nube médica
        ↓
Atención médica domiciliaria
        ↓
Evaluación médica remota
        ↓
¿Emergencia crítica?
        ├── Sí
        │      ↓
        │  Envío de personal médico
        │      ↓
        │  Atención presencial
        │
        └── No
                ↓
        Continuar atención domiciliaria
```

---

## 3.4 Monitoreo Médico Inteligente
(Monitoreo reactivo/crítico)

```text
Comparación con umbrales críticos
        ↓
¿Valores peligrosos?
        ├── Sí
        │      ↓
        │  Generación automática de alerta
        │      ↓
        │  Notificación al centro médico
        │      ↓
        │  Priorización automática del caso
        │      ↓
        │  Activación de atención médica
        │
        └── No
                ↓
        Continuar monitoreo
```

---

## 3.5 Gestión de Emergencias Distribuidas
(Atención operativa)

```text
Llegada del personal médico
        ↓
Atención prehospitalaria
        ↓
Monitoreo de signos vitales
        ↓
¿Requiere hospitalización?
        ├── Sí
        │      ↓
        │  Traslado al hospital asignado
        │      ↓
        │  Entrega formal del paciente
        │
        └── No
                ↓
        Atención domiciliaria/remota
                ↓
        Alta médica temporal
```

---

## 4. Módulo de Gestión Financiera y Facturación

Este módulo gestiona la cobertura, costos y pagos asociados a la atención médica.

## Flujo del módulo

```text
Recepción del registro de atención médica
        ↓
Clasificación del tipo de servicio
        ├── Emergencia
        ├── Telemedicina
        ├── Atención domiciliaria
        ├── Monitoreo médico
        └── Emergencia distribuida
                ↓
Validación de cobertura
(MSP/IESS/Seguro privado)
        ↓
¿Posee cobertura?
        ├── Sí
        │      ↓
        │  Registro automático de cobertura
        │
        └── No
                ↓
        Cálculo de costos
                ↓
        Generación de factura
                ↓
        Pago inmediato o diferido
                ↓
        Confirmación financiera
```

---

## 5. Módulo de Gestión Clínica y Seguimiento

Este módulo administra la continuidad clínica, almacenamiento de datos médicos y monitoreo continuo del paciente.

## Flujo del módulo

```text
Captura de información clínica
        ↓
Validación de información médica
        ↓
Almacenamiento persistente
        ↓
Actualización del historial clínico
        ↓
Sincronización con sistemas externos
(MSP, IESS, hospitales)
        ↓
Captura continua de datos médicos
        ↓
Procesamiento continuo de métricas
        ↓
Guardar métricas históricas
        ↓
Seguimiento post atención
        ├── Seguimiento remoto
        ├── Seguimiento domiciliario
        ├── Seguimiento post emergencia
        └── Monitoreo continuo
                ↓
¿Se requiere nueva atención?
        ├── Sí
        │      ↓
        │  Retorno al Módulo de Solicitud
        │
        └── No
                ↓
        Cierre definitivo del caso
```

---

