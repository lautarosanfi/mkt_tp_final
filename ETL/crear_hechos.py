import pandas as pd
import os

# --- Configuración de Rutas ---
RAW_DIR = "raw"  # Archivos RAW en la raíz
DW_DIR = "DW"  # Archivos DW en la carpeta DW

def crear_hechos():
    """
    Carga las dimensiones desde la carpeta DW y los archivos RAW
    para generar las 6 tablas de Hechos.
    """
    print("Iniciando Fase 2: Creación de Tablas de Hechos (Facts)")

    # --- 1. Cargar todas las Dimensiones (Lookups) ---
    print("Cargando dimensiones en memoria para lookups...")
    try:
        df_dim_tiempo = pd.read_csv(os.path.join(DW_DIR, "Dim_Tiempo.csv"))
        df_dim_cliente = pd.read_csv(os.path.join(DW_DIR, "Dim_Cliente.csv"))
        df_dim_geografia = pd.read_csv(os.path.join(DW_DIR, "Dim_Geografia.csv"))
        df_dim_producto = pd.read_csv(os.path.join(DW_DIR, "Dim_Producto.csv"))
        df_dim_tienda = pd.read_csv(os.path.join(DW_DIR, "Dim_Tienda.csv"))
        
        # Crear diccionarios de lookups para FKs
        lookup_cliente = df_dim_cliente.set_index('customer_id')['cliente_sk']
        lookup_geografia = df_dim_geografia.set_index('address_id')['geografia_sk']
        lookup_producto = df_dim_producto.set_index('product_id')['producto_sk']
        
        # Lookup de tiempo (convertir 'fecha' a datetime y luego a YYYYMMDD int)
        df_dim_tiempo['fecha'] = pd.to_datetime(df_dim_tiempo['fecha']).dt.date
        lookup_tiempo = df_dim_tiempo.set_index('fecha')['tiempo_id']
        
        # Cliente anónimo SK
        ANON_CLIENTE_SK = -1 # Como se definió en el script anterior

        print("Dimensiones cargadas.")

    except FileNotFoundError as e:
        print(f"Error fatal: No se encontró una dimensión esencial. {e}")
        print("Asegúrese de que '01_crear_dim_tiempo.py' y '02_crear_dimensiones.py' se hayan ejecutado.")
        return # Detener la ejecución si faltan dimensiones
    except Exception as e:
        print(f"Error al cargar dimensiones: {e}")
        return

    # --- Función auxiliar para convertir fechas a tiempo_id ---
    def convert_date_to_tiempo_id(date_series, lookup_tiempo):
        """Convierte una serie de timestamps a YYYYMMDD int usando el lookup."""
        # Convertir a datetime, luego a objeto 'date' (ignora la hora)
        dates = pd.to_datetime(date_series, errors='coerce').dt.date
        # Mapear a tiempo_id
        return dates.map(lookup_tiempo)

    # --- 2. Creación de Fact_Pedidos ---
    try:
        print("\n--- Procesando: Fact_Pedidos ---")
        df_sales_order = pd.read_csv(os.path.join(RAW_DIR, "sales_order.csv"))
        
        df_fact_pedidos = df_sales_order.copy()
        
        # Convertir FKs a SKs
        df_fact_pedidos['tiempo_id'] = convert_date_to_tiempo_id(df_fact_pedidos['order_date'], lookup_tiempo)
        df_fact_pedidos['cliente_sk'] = df_fact_pedidos['customer_id'].map(lookup_cliente)
        df_fact_pedidos['geografia_billing_sk'] = df_fact_pedidos['billing_address_id'].map(lookup_geografia)
        df_fact_pedidos['geografia_shipping_sk'] = df_fact_pedidos['shipping_address_id'].map(lookup_geografia)
        
        # Renombrar 'channel_id' por coherencia
        df_fact_pedidos = df_fact_pedidos.rename(columns={'channel_id': 'canal_id'})
        
        # Seleccionar columnas finales
        final_cols = [
            'order_id', 'tiempo_id', 'cliente_sk', 'canal_id', 'store_id', 
            'geografia_billing_sk', 'geografia_shipping_sk', 'subtotal', 
            'tax_amount', 'shipping_fee', 'total_amount', 'status', 'currency_code'
        ]
        df_fact_pedidos = df_fact_pedidos[final_cols]
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Fact_Pedidos.csv")
        df_fact_pedidos.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Fact_Pedidos.csv' guardado.")
        print(df_fact_pedidos.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'sales_order.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Fact_Pedidos: {e}")

    # --- 3. Creación de Fact_Ventas_Detalle ---
    try:
        print("\n--- Procesando: Fact_Ventas_Detalle ---")
        df_sales_order_item = pd.read_csv(os.path.join(RAW_DIR, "sales_order_item.csv"))
        
        # Necesitamos la fecha de la orden de Fact_Pedidos (recién creada)
        df_fact_pedidos_lookup = pd.read_csv(os.path.join(DW_DIR, "Fact_Pedidos.csv"))[['order_id', 'tiempo_id']]
        
        # Join con items
        df_fact_ventas_detalle = pd.merge(
            df_sales_order_item,
            df_fact_pedidos_lookup,
            on='order_id',
            how='left'
        )
        
        # Convertir FK a SK
        df_fact_ventas_detalle['producto_sk'] = df_fact_ventas_detalle['product_id'].map(lookup_producto)
        
        # Seleccionar columnas finales
        final_cols = [
            'order_item_id', 'order_id', 'producto_sk', 'tiempo_id', 
            'quantity', 'unit_price', 'discount_amount', 'line_total'
        ]
        df_fact_ventas_detalle = df_fact_ventas_detalle[final_cols]
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Fact_Ventas_Detalle.csv")
        df_fact_ventas_detalle.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Fact_Ventas_Detalle.csv' guardado.")
        print(df_fact_ventas_detalle.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'sales_order_item.csv' o 'DW/Fact_Pedidos.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Fact_Ventas_Detalle: {e}")

    # --- 4. Creación de Fact_Pagos ---
    try:
        print("\n--- Procesando: Fact_Pagos ---")
        df_payment = pd.read_csv(os.path.join(RAW_DIR, "payment.csv"))
        
        df_fact_pagos = df_payment.copy()
        
        # Convertir FK a SK
        df_fact_pagos['tiempo_id'] = convert_date_to_tiempo_id(df_fact_pagos['paid_at'], lookup_tiempo)
        
        # Seleccionar columnas finales
        final_cols = [
            'payment_id', 'order_id', 'tiempo_id', 'amount', 
            'method', 'status', 'transaction_ref'
        ]
        df_fact_pagos = df_fact_pagos[final_cols]
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Fact_Pagos.csv")
        df_fact_pagos.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Fact_Pagos.csv' guardado.")
        print(df_fact_pagos.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'payment.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Fact_Pagos: {e}")

    # --- 5. Creación de Fact_Envios ---
    try:
        print("\n--- Procesando: Fact_Envios ---")
        df_shipment = pd.read_csv(os.path.join(RAW_DIR, "shipment.csv"))
        
        df_fact_envios = df_shipment.copy()
        
        # Convertir FKs a SKs
        df_fact_envios['tiempo_shipped_id'] = convert_date_to_tiempo_id(df_fact_envios['shipped_at'], lookup_tiempo)
        df_fact_envios['tiempo_delivered_id'] = convert_date_to_tiempo_id(df_fact_envios['delivered_at'], lookup_tiempo)
        
        # Calcular medida: dias_en_transito
        shipped_dt = pd.to_datetime(df_fact_envios['shipped_at'], errors='coerce')
        delivered_dt = pd.to_datetime(df_fact_envios['delivered_at'], errors='coerce')
        df_fact_envios['dias_en_transito'] = (delivered_dt - shipped_dt).dt.days.astype('Int64')
        
        # Seleccionar columnas finales
        final_cols = [
            'shipment_id', 'order_id', 'tiempo_shipped_id', 'tiempo_delivered_id',
            'dias_en_transito', 'carrier', 'tracking_number', 'status'
        ]
        df_fact_envios = df_fact_envios[final_cols]
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Fact_Envios.csv")
        df_fact_envios.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Fact_Envios.csv' guardado.")
        print(df_fact_envios.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'shipment.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Fact_Envios: {e}")

    # --- 6. Creación de Fact_Sesiones ---
    try:
        print("\n--- Procesando: Fact_Sesiones ---")
        df_web_session = pd.read_csv(os.path.join(RAW_DIR, "web_session.csv"))
        
        df_fact_sesiones = df_web_session.copy()
        
        # Convertir FKs a SKs
        df_fact_sesiones['tiempo_id'] = convert_date_to_tiempo_id(df_fact_sesiones['started_at'], lookup_tiempo)
        
        # Mapear customer_id a cliente_sk
        df_fact_sesiones['cliente_sk'] = df_fact_sesiones['customer_id'].map(lookup_cliente)
        # Reemplazar NaT/NaN (nulos) por el SK de anónimo
        df_fact_sesiones['cliente_sk'] = df_fact_sesiones['cliente_sk'].fillna(ANON_CLIENTE_SK).astype(int)

        # Calcular medida: duracion_sesion_seg
        started_dt = pd.to_datetime(df_fact_sesiones['started_at'], errors='coerce')
        ended_dt = pd.to_datetime(df_fact_sesiones['ended_at'], errors='coerce')
        df_fact_sesiones['duracion_sesion_seg'] = (ended_dt - started_dt).dt.total_seconds().astype('Int64') # Usar Int64 para permitir nulos
        
        # Medida: contador_sesion
        df_fact_sesiones['contador_sesion'] = 1
        
        # Seleccionar columnas finales
        final_cols = [
            'session_id', 'cliente_sk', 'tiempo_id', 'contador_sesion',
            'duracion_sesion_seg', 'source', 'device'
        ]
        df_fact_sesiones = df_fact_sesiones[final_cols]
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Fact_Sesiones.csv")
        df_fact_sesiones.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Fact_Sesiones.csv' guardado.")
        print(df_fact_sesiones.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'web_session.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Fact_Sesiones: {e}")

    # --- 7. Creación de Fact_NPS ---
    try:
        print("\n--- Procesando: Fact_NPS ---")
        df_nps_response = pd.read_csv(os.path.join(RAW_DIR, "nps_response.csv"))
        
        df_fact_nps = df_nps_response.copy()
        
        # Convertir FKs a SKs
        df_fact_nps['tiempo_id'] = convert_date_to_tiempo_id(df_fact_nps['responded_at'], lookup_tiempo)
        
        # Mapear customer_id a cliente_sk
        df_fact_nps['cliente_sk'] = df_fact_nps['customer_id'].map(lookup_cliente)
        # Reemplazar NaT/NaN (nulos) por el SK de anónimo
        df_fact_nps['cliente_sk'] = df_fact_nps['cliente_sk'].fillna(ANON_CLIENTE_SK).astype(int)
        
        # Renombrar 'channel_id' por coherencia
        df_fact_nps = df_fact_nps.rename(columns={'channel_id': 'canal_id'})

        # Seleccionar columnas finales
        final_cols = [
            'nps_id', 'cliente_sk', 'canal_id', 'tiempo_id', 'score', 'comment'
        ]
        df_fact_nps = df_fact_nps[final_cols]
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Fact_NPS.csv")
        df_fact_nps.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Fact_NPS.csv' guardado.")
        print(df_fact_nps.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'nps_response.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Fact_NPS: {e}")

if __name__ == "__main__":
    crear_hechos()
    print("\n\n--- Proceso ETL completado ---")
    print(f"Todos los archivos del Data Warehouse (DW) han sido generados en la carpeta '{DW_DIR}'.")