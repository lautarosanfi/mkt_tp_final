import pandas as pd
import os

# --- Configuración de Rutas ---
RAW_DIR = "raw"  # Asumimos que los CSVs de RAW están en la raíz del proyecto
DW_DIR = "DW"

# Asegurarse que el directorio DW exista
os.makedirs(DW_DIR, exist_ok=True)

def crear_dimensiones():
    """
    Carga los archivos CSV de RAW y genera los archivos CSV
    para Dim_Canal, Dim_Cliente, Dim_Geografia, Dim_Producto y Dim_Tienda.
    """
    print("Iniciando Fase 2: Creación de Dimensiones (Canal, Cliente, Geografia, Producto, Tienda)")

    # --- 1. Creación de Dim_Canal ---
    try:
        print("\n--- Procesando: Dim_Canal ---")
        df_channel = pd.read_csv(os.path.join(RAW_DIR, "channel.csv"))
        
        # Seleccionar y renombrar columnas según DDL
        df_dim_canal = df_channel[['channel_id', 'code', 'name']].copy()
        df_dim_canal = df_dim_canal.rename(columns={
            'channel_id': 'canal_id',
            'code': 'canal_code',
            'name': 'canal_nombre'
        })
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Dim_Canal.csv")
        df_dim_canal.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Dim_Canal.csv' guardado.")
        print(df_dim_canal.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'channel.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Dim_Canal: {e}")

    # --- 2. Creación de Dim_Cliente ---
    try:
        print("\n--- Procesando: Dim_Cliente ---")
        df_customer = pd.read_csv(os.path.join(RAW_DIR, "customer.csv"))
        
        # Generar Surrogate Key (SK)
        df_dim_cliente = df_customer.copy()
        df_dim_cliente = df_dim_cliente.reset_index()
        df_dim_cliente['cliente_sk'] = df_dim_cliente['index'] + 1 # Empezar SK en 1
        
        # Seleccionar y renombrar columnas según DDL
        df_dim_cliente = df_dim_cliente[[
            'cliente_sk', 'customer_id', 'email', 'first_name', 
            'last_name', 'phone', 'status', 'created_at'
        ]]
        
        # Añadir registro para 'Cliente Anónimo'
        anon_record = pd.DataFrame([{
            'cliente_sk': -1,
            'customer_id': -1,
            'email': 'desconocido@dominio.com',
            'first_name': 'Cliente',
            'last_name': 'Anónimo',
            'phone': None,
            'status': 'A',
            'created_at': pd.Timestamp('1900-01-01')
        }])
        
        df_dim_cliente = pd.concat([anon_record, df_dim_cliente], ignore_index=True)
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Dim_Cliente.csv")
        df_dim_cliente.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Dim_Cliente.csv' guardado (con registro anónimo SK=-1).")
        print(df_dim_cliente.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError:
        print("Error: 'customer.csv' no encontrado.")
    except Exception as e:
        print(f"Error procesando Dim_Cliente: {e}")

    # --- 3. Creación de Dim_Geografia ---
    try:
        print("\n--- Procesando: Dim_Geografia ---")
        df_address = pd.read_csv(os.path.join(RAW_DIR, "address.csv"))
        df_province = pd.read_csv(os.path.join(RAW_DIR, "province.csv"))
        
        # Join con province para obtener el nombre
        df_geo_merged = pd.merge(
            df_address,
            df_province,
            on='province_id',
            how='left'
        )
        
        # Generar Surrogate Key (SK)
        df_dim_geografia = df_geo_merged.reset_index()
        df_dim_geografia['geografia_sk'] = df_dim_geografia['index'] + 1
        
        # Seleccionar y renombrar columnas según DDL
        df_dim_geografia = df_dim_geografia[[
            'geografia_sk', 'address_id', 'line1', 'line2', 'city', 
            'postal_code', 'country_code', 'name'
        ]]
        df_dim_geografia = df_dim_geografia.rename(columns={'name': 'nombre_provincia'})
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Dim_Geografia.csv")
        df_dim_geografia.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Dim_Geografia.csv' guardado.")
        print(df_dim_geografia.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado. Asegúrate de tener 'address.csv' y 'province.csv'. {e}")
    except Exception as e:
        print(f"Error procesando Dim_Geografia: {e}")

    # --- 4. Creación de Dim_Producto ---
    try:
        print("\n--- Procesando: Dim_Producto ---")
        df_product = pd.read_csv(os.path.join(RAW_DIR, "product.csv"))
        df_category = pd.read_csv(os.path.join(RAW_DIR, "product_category.csv"))
        
        # Join 1: Producto con su categoría
        df_prod_merged = pd.merge(
            df_product,
            df_category,
            on='category_id',
            how='left',
            suffixes=('', '_cat')
        )
        
        # Join 2: Resultado con la categoría padre
        df_prod_merged = pd.merge(
            df_prod_merged,
            df_category,
            left_on='parent_id',
            right_on='category_id',
            how='left',
            suffixes=('', '_parent')
        )
        
        # Generar Surrogate Key (SK)
        df_dim_producto = df_prod_merged.reset_index()
        df_dim_producto['producto_sk'] = df_dim_producto['index'] + 1
        
        # Seleccionar y renombrar columnas según DDL
        df_dim_producto = df_dim_producto[[
            'producto_sk', 'product_id', 'sku', 'name', 
            'list_price', 'status', 'name_cat', 'name_parent'
        ]]
        df_dim_producto = df_dim_producto.rename(columns={
            'name': 'nombre_producto',
            'status': 'status_producto',
            'name_cat': 'nombre_categoria',
            'name_parent': 'nombre_categoria_padre'
        })
        
        # Limpiar nulos en categorías
        df_dim_producto['nombre_categoria'] = df_dim_producto['nombre_categoria'].fillna('Sin Categoria')
        df_dim_producto['nombre_categoria_padre'] = df_dim_producto['nombre_categoria_padre'].fillna('N/A')
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Dim_Producto.csv")
        df_dim_producto.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Dim_Producto.csv' guardado.")
        print(df_dim_producto.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado. Asegúrate de tener 'product.csv' y 'product_category.csv'. {e}")
    except Exception as e:
        print(f"Error procesando Dim_Producto: {e}")

    # --- 5. Creación de Dim_Tienda ---
    try:
        print("\n--- Procesando: Dim_Tienda ---")
        df_store = pd.read_csv(os.path.join(RAW_DIR, "store.csv"))
        
        # Cargar la Dim_Geografia recién creada para obtener la SK
        df_dim_geografia_lookup = pd.read_csv(os.path.join(DW_DIR, "Dim_Geografia.csv"))
        df_dim_geografia_lookup = df_dim_geografia_lookup[['address_id', 'geografia_sk']]
        
        # Join con Dim_Geografia para obtener la geografia_sk
        df_tienda_merged = pd.merge(
            df_store,
            df_dim_geografia_lookup,
            on='address_id',
            how='left'
        )
        
        # Seleccionar y renombrar columnas según DDL
        df_dim_tienda = df_tienda_merged[['store_id', 'name', 'geografia_sk']]
        df_dim_tienda = df_dim_tienda.rename(columns={'name': 'nombre_tienda'})
        
        # Guardar
        output_path = os.path.join(DW_DIR, "Dim_Tienda.csv")
        df_dim_tienda.to_csv(output_path, index=False, encoding='utf-8')
        
        print(f"¡Éxito! 'Dim_Tienda.csv' guardado.")
        print(df_dim_tienda.head().to_markdown(index=False, numalign="left", stralign="left"))

    except FileNotFoundError as e:
        print(f"Error: Archivo no encontrado. Asegúrate de tener 'store.csv' y 'DW/Dim_Geografia.csv'. {e}")
    except Exception as e:
        print(f"Error procesando Dim_Tienda: {e}")

if __name__ == "__main__":
    crear_dimensiones()