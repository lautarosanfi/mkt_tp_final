import pandas as pd
import os
import locale


def crear_dim_tiempo(START_DATE, END_DATE, OUTPUT_DIR, OUTPUT_FILE):
    """
    Genera la dimensión de tiempo en el rango de fechas especificado
    y la guarda en un archivo CSV.
    """
    print(f"Iniciando la creación de la Dimensión de Tiempo.")
    print(f"Rango de fechas: {START_DATE} a {END_DATE}")

    # 1. Crear el directorio de salida si no existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Directorio '{OUTPUT_DIR}' asegurado.")

    # 2. Establecer el locale a español para los nombres de los meses
    # (Esto funcionará en tu máquina local si tienes el locale 'es_ES' o 'es')
    try:
        locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
        print("Locale establecido a 'es_ES.UTF-8' para nombres de meses.")
    except locale.Error:
        try:
            locale.setlocale(locale.LC_TIME, 'es')
            print("Locale establecido a 'es'.")
        except locale.Error:
            print(f"Warning: No se pudo setear el locale a español. Se usarán nombres en inglés.")

    # 3. Generar el rango de fechas
    df_tiempo = pd.DataFrame({
        "fecha": pd.date_range(start=START_DATE, end=END_DATE)
    })

    # 4. Extraer atributos de la fecha
    df_tiempo['tiempo_id'] = df_tiempo['fecha'].dt.strftime('%Y%m%d').astype(int)
    df_tiempo['anio'] = df_tiempo['fecha'].dt.year
    df_tiempo['mes'] = df_tiempo['fecha'].dt.month
    df_tiempo['nombre_mes'] = df_tiempo['fecha'].dt.strftime('%B').str.capitalize()
    df_tiempo['dia'] = df_tiempo['fecha'].dt.day
    df_tiempo['trimestre'] = df_tiempo['fecha'].dt.quarter
    
    # .dt.dayofweek (Lunes=0, Domingo=6)
    df_tiempo['dia_semana_num'] = df_tiempo['fecha'].dt.dayofweek 
    df_tiempo['dia_semana_nombre'] = df_tiempo['fecha'].dt.strftime('%A').str.capitalize()

    # 5. Reordenar columnas según el DDL
    column_order = [
        'tiempo_id', 'fecha', 'anio', 'mes', 'nombre_mes', 
        'dia', 'trimestre', 'dia_semana_num', 'dia_semana_nombre'
    ]
    df_tiempo = df_tiempo[column_order]

    # 6. Guardar el archivo
    df_tiempo.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')

    print(f"\n¡Éxito! Archivo '{OUTPUT_FILE}' generado.")
    print("Primeras 5 filas de la dimensión de tiempo:")
    print(df_tiempo.head().to_markdown(index=False, numalign="left", stralign="left"))

if __name__ == "__main__":
    crear_dim_tiempo()