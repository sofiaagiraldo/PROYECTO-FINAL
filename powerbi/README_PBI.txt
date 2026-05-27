Power BI Desktop — RETO LOGÍSTICA «Ruta-Óptima»
==============================================

Guía paso a paso completa (instalación, ejecución local, dashboard):
  ../INSTRUCCIONES_LOCAL.md   (sección 4 = Power BI)

────────────────────────────────────────────────────────────────────
1) GENERAR EL ARCHIVO .pbix EN TU PC
────────────────────────────────────────────────────────────────────

Desde la raíz del proyecto (con venv y dependencias instaladas):

  pip install -r requirements.txt
  ./run_gui.sh

O solo regenerar el .pbix:

  source .venv/bin/activate
  python -c "from Backend.generar_pbix import asegurar_archivo_pbix; from Backend.config import ruta_base_datos; print(asegurar_archivo_pbix(ruta_base_datos()))"

Debe quedar:  powerbi/RutaOptima.pbix

────────────────────────────────────────────────────────────────────
2) ABRIR Y VER EL DASHBOARD EN POWER BI DESKTOP
────────────────────────────────────────────────────────────────────

A) Instalar Power BI Desktop (gratis):
   https://powerbi.microsoft.com/desktop/

B) Abrir el informe:
   - Desde Tkinter: botón 「5 Abrir Power BI Desktop」
   - O en Desktop: Archivo → Abrir → RutaOptima.pbix

C) Vista Informe: si la página está vacía, crea visuales (tabla abajo).
   Si ya guardaste gráficas antes, aparecerán al abrir el archivo.

────────────────────────────────────────────────────────────────────
3) CONEXIÓN A DATOS (si reconstruyes desde cero)
────────────────────────────────────────────────────────────────────

Opción A — SQLite (recomendada):
  Obtener datos → SQLite → ruta en CADENA_BASE_DATOS.txt
  (se regenera al ejecutar main.py o run_gui.sh)

Opción B — CSV:
  Obtener datos → Texto/CSV → carpeta csv_refresh/
  (fact_envio.csv, dim_fecha.csv, dim_zona.csv, dim_camion.csv)

Modelo estrella (relaciones many-to-one desde hecho):

  dim_fecha[fecha_key]  -> fact_envio[fecha_key]
  dim_zona[zona_id]      -> fact_envio[zona_id]
  dim_camion[camion_id] -> fact_envio[camion_id]

Marcar dim_fecha como tabla de fechas (columna fecha, tipo fecha).

────────────────────────────────────────────────────────────────────
4) DASHBOARD — 4 GRÁFICAS (PASO A PASO EN DESKTOP)
────────────────────────────────────────────────────────────────────

Nueva página: 「Dashboard Ruta Óptima」

  [1] Gráfico de barras
      Eje: fact_envio[clase_servicio]
      Valores: Suma de fact_envio[peso_kg]
      → Peso por tipo de servicio

  [2] Gráfico de líneas
      Eje: dim_fecha[fecha]
      Valores: Medida [Costo Medio COP por Envio]
      → Costo medio en el tiempo

  [3] Gráfico de barras
      Eje: dim_zona[nombre_localidad]
      Valores: Recuento de fact_envio[envio_id]
      → Envíos por localidad

  [4] Gráfico de dispersión
      Eje X: fact_envio[peso_kg]
      Eje Y: fact_envio[kms_recorrido]
      Leyenda: dim_zona[nombre_localidad]
      → Km vs peso por zona

  [Opcional] Tarjeta KPI: medida [Costo Medio COP por Envio]

Guardar: Archivo → Guardar como → powerbi/RutaOptima.pbix

────────────────────────────────────────────────────────────────────
5) ACTUALIZAR DATOS TRAS CAMBIOS EN TKINTER
────────────────────────────────────────────────────────────────────

1. Crear/editar/borrar envío en la app Python (o botón Actualizar artefactos BI).
2. Se sobrescriben powerbi/csv_refresh/*.csv
3. En Power BI Desktop: Inicio → Actualizar

────────────────────────────────────────────────────────────────────
6) DAX (EJEMPLOS DEL TALLER)
────────────────────────────────────────────────────────────────────

MEDIDA (ya puede venir en el .pbix generado):

  Costo Medio COP por Envio :=
  DIVIDE ( SUM ( fact_envio[costo_estimado_cop] ), COUNTROWS ( fact_envio ), 0 )

COLUMNA CALCULADA (crear en fact_envio):

  Clasificacion Riesgo KG =
  VAR p = fact_envio[peso_kg]
  RETURN
  IF (
      p < 2,
      "Tipo documento (ligero)",
      IF ( p <= 30, "Tipo paqueteria (urbano medio)", "Tipo cargo (alto volumen)" )
  )

────────────────────────────────────────────────────────────────────
Archivo RutaOptima.pbix
────────────────────────────────────────────────────────────────────
Nombre exacto para el botón 5 del Tkinter.
Se genera automáticamente con pbix-mcp (requirements.txt).
Sin venv: ver RutaOptima.pbix.LEEME.txt o INSTRUCCIONES_LOCAL.md.
