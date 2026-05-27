Power BI Desktop — RETO LOGISTICA «Ruta-Óptima»
==============================================

1) Conexion a datos
--------------------
Opcion A (recomendada en Desktop): obtener datos SQLite y apunte a la ruta que aparece
en CADENA_BASE_DATOS.txt en esta carpeta (se regenera al ejecutar python main.py).

Opcion B: obtener datos texto/CSV desde la carpeta csv_refresh/ que exporta Backend/export_bi.py.

Modelo estrella (relaciones many-to-one desde hecho):

  dim_fecha[fecha_key]  -> fact_envio[fecha_key]
  dim_zona[zona_id]      -> fact_envio[zona_id]
  dim_camion[camion_id] -> fact_envio[camion_id]

Marca dim_fecha como tabla de fechas usando column fecha (tipo fecha).

Dashboard (minimo 4 graficas con valor de negocio)
--------------------------------------------------
Sugeridas: barras clase_servicio vs suma peso_kg; lineas por fecha_costo medio;
scatter kms vs peso_kg partido por zona; tarjeta KPI costo medio por clase.

Ejemplo MEDIDA DAX (pegar como nueva medida)
--------------------------------------------
Nombre: Costo Medio COP por Envio :=
DIVIDE ( SUM ( fact_envio[costo_estimado_cop] ), COUNTROWS ( fact_envio ), 0 )


Ejemplo COLUMNA CALCULADA DAX (columna nueva en tabla hechos)
-------------------------------------------------------------
Clasificacion Riesgo KG =
VAR p = fact_envio[peso_kg]
RETURN
IF (
    p < 2,
    "Tipo documento (ligero)",
    IF ( p <= 30, "Tipo paqueteria (urbano medio)", "Tipo cargo (alto volumen)" )
)

Archivo RutaOptima.pbix
-----------------------
Debes guardar el tablero en esta carpeta con exactamente ese nombre para que funcione el botón 5 del Tkinter.
Si aun no lo tienes: crea las consultas desde SQLite como arriba, agrega graficas/DAX y Archivo Guardar como RutaOptima.pbix .
