# Proyecto final — RETO LOGISTICA «Ruta-Óptima»

Ecosistema end-to-end (Python + SQLite modelo estrella + Tkinter + Power BI) segun **Taller Final Corte 3 — Programacion y Decisiones (UNISABANA)**.

## Estructura exigida

| Elemento | Descripcion |
|----------|-------------|
| `Backend/` | POO + SQLite (tabla hechos `fact_envio` + dimensiones `dim_fecha`, `dim_zona`, `dim_camion`) |
| `Frontend/` | GUI Tkinter, marca `logo_marca.png` (logo proyecto); respaldo opcional `logo.gif` |
| `main.py` | Orquestador: inicializa BD, exporta CSV/txt para BI y lanza Tkinter |
| `data/ruta_optima.db` | Base SQLite (generada/regenerada al arrancar si hace falta) |
| `powerbi/` | `csv_refresh/` (automatico), `CADENA_BASE_DATOS.txt`, `README_PBI.txt`, y **tu** `RutaOptima.pbix` |
| `README.md` | Este archivo |

## Reto aplicado

**Ruta Optima**: peso kg + zona destino; clasificacion automatica (**Documento** / **Paqueteria** / **Carga**) y cotizacion COP mediante `ServicioEnvios` en `Backend/logica_reto.py`, persistida en `fact_envio` con manifiesto ordenable por peso (consulta READ).

Al iniciarse, si la BD falta datos, se garantizan **al menos 5 filas por tabla** (dimensiones + hechos) con datos de muestra coherentes.

## Ejecucion

```bash
cd /ruta/al/repositorio
python3 main.py
```

Ventana Tkinter:

1. Registrar (Create), 2. Ver tabla (Read), 3. Actualizar (Update), 4. Eliminar (Delete), 5. Abrir Power BI (`.pbix`).

Los errores de negocio, formato o ficheros se muestran con **`messagebox`** y no deben cerrar la app si el flujo atrapa la excepcion.

Despues de cada CUD, se ejecuta **`sincronizar_artefactos_bi`**: sobrescribe `powerbi/csv_refresh/*.csv` y `powerbi/CADENA_BASE_DATOS.txt` para facilitar refresco en Desktop.

## Power BI

Ver `powerbi/README_PBI.txt` (relaciones, ejemplo de **medida DAX**, ejemplo de **columna calculada**).  
Tu archivo debe guardarse como `powerbi/RutaOptima.pbix` (instrucciones adicionales en `RutaOptima.pbix.LEEME.txt`).

## Dependencias

- Python **3.10+** con Tkinter habilitado.
- **Pillow** (`pip install -r requirements.txt`) para cargar y redimensionar `Frontend/logo_marca.png`; sin Pillow se intentara solo GIF.
- SQLite: modulo `sqlite3` de la biblioteca estandar.


## Entrega GitHub individual

Publica este proyecto en tu repositorio **personal publico**; el enlace al repo de un companero tiene penalizacion segun rubrica del curso.
