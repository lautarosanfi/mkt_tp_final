import os
import argparse  # Para manejar argumentos de la terminal
import time      # Para medir el tiempo de ejecución

# 1. Importar las funciones principales de CADA script
from crear_dim_tiempo import crear_dim_tiempo
from crear_dimensiones import crear_dimensiones
from crear_hechos import crear_hechos

def main(start_date, end_date):
    """
    Script principal (orquestador) para ejecutar el proceso ETL completo.
    """
    print("=============================================")
    print("--- INICIANDO PROCESO ETL COMPLETO ---")
    print(f"Rango de fechas para Dim_Tiempo: {start_date} a {end_date}")
    print("=============================================")
    
    start_total_time = time.time()

    # --- Configuración de Rutas ---
    # Estas rutas deben ser consistentes con tus otros scripts
    OUTPUT_DIR = "DW"
    TIEMPO_OUTPUT_FILE = os.path.join(OUTPUT_DIR, "Dim_Tiempo.csv")

    # --- FASE 1: Crear Dim_Tiempo ---
    try:
        print("\n[FASE 1 de 3] Ejecutando: crear_dim_tiempo...")
        start_fase1 = time.time()
        
        # Llamamos a la primera función con los parámetros recibidos
        crear_dim_tiempo(start_date, end_date, OUTPUT_DIR, TIEMPO_OUTPUT_FILE)
        
        print(f"--- Fase 1 (Dim_Tiempo) completada en {time.time() - start_fase1:.2f} segundos ---")
    
    except Exception as e:
        print(f"ERROR FATAL en Fase 1 (Dim_Tiempo): {e}")
        print("El proceso ETL se detendrá.")
        return # Detiene la ejecución si la Dim_Tiempo falla

    # --- FASE 2: Crear Dimensiones ---
    # (Esta función no recibe parámetros según tu script)
    try:
        print("\n[FASE 2 de 3] Ejecutando: crear_dimensiones...")
        start_fase2 = time.time()
        
        # Llamamos a la segunda función
        crear_dimensiones()
        
        print(f"--- Fase 2 (Dimensiones) completada en {time.time() - start_fase2:.2f} segundos ---")
    
    except Exception as e:
        print(f"ERROR FATAL en Fase 2 (Dimensiones): {e}")
        print("El proceso ETL se detendrá.")
        return # Detiene la ejecución si las dimensiones fallan

    # --- FASE 3: Crear Hechos ---
    # (Esta función tampoco recibe parámetros y depende de las fases 1 y 2)
    try:
        print("\n[FASE 3 de 3] Ejecutando: crear_hechos...")
        start_fase3 = time.time()
        
        # Llamamos a la tercera función
        crear_hechos()
        
        print(f"--- Fase 3 (Hechos) completada en {time.time() - start_fase3:.2f} segundos ---")
    
    except Exception as e:
        print(f"ERROR FATAL en Fase 3 (Hechos): {e}")
        print("El proceso ETL se detendrá.")
        return # Detiene la ejecución

    # --- Finalización ---
    end_total_time = time.time()
    print("\n=============================================")
    print("PROCESO ETL COMPLETO FINALIZADO CON ÉXITO.")
    print(f"Tiempo total de ejecución: {end_total_time - start_total_time:.2f} segundos.")
    print(f"Todos los archivos generados en el directorio: '{OUTPUT_DIR}'")
    print("=============================================")


if __name__ == "__main__":
    # --- Configuración de Argumentos de Terminal ---
    # Esto permite que llames al script con:
    # python run_etl.py --start "2023-01-01" --end "2025-12-31"
    
    parser = argparse.ArgumentParser(description="Script principal para ejecutar el ETL completo del Data Warehouse.")
    
    # Añadimos el argumento --start
    parser.add_argument(
        "--start", 
        type=str, 
        default="2023-01-01",  # Valor por defecto si no se especifica
        help="Fecha de inicio (YYYY-MM-DD) para la Dim_Tiempo."
    )
    
    # Añadimos el argumento --end
    parser.add_argument(
        "--end", 
        type=str, 
        default="2025-12-31",  # Valor por defecto si no se especifica
        help="Fecha de fin (YYYY-MM-DD) para la Dim_Tiempo."
    )
    
    # Parseamos los argumentos que nos llegan
    args = parser.parse_args()
    
    # Llamamos a la función main con los argumentos (o los de por defecto)
    main(start_date=args.start, end_date=args.end)