def detect_anomalies(vitals: dict) -> list:
    """
    Reglas simples en memoria para detectar anomalías.
    vitals format: {'heart_rate': int, 'blood_pressure_sys': int, 'blood_pressure_dia': int, 'oxygen_level': int}
    """
    anomalies = []
    
    hr = vitals.get('heart_rate')
    if hr and (hr < 50 or hr > 110):
        anomalies.append('Abnormal Heart Rate')
        
    oxy = vitals.get('oxygen_level')
    if oxy and oxy < 90:
        anomalies.append('Low Oxygen')
        
    sys = vitals.get('blood_pressure_sys')
    dia = vitals.get('blood_pressure_dia')
    if sys and dia and (sys > 180 or dia > 120):
        anomalies.append('Hypertensive Crisis')
        
    return anomalies
