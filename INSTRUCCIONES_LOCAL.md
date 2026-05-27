# Guía local — Ruta Óptima (paso a paso)

Esta guía explica cómo ejecutar el proyecto en tu computador, ver el **dashboard en Tkinter** y montar o abrir el **dashboard en Power BI Desktop**.

---

## Antes de empezar (requisitos)

| Requisito | Para qué sirve |
|-----------|----------------|
| **Python 3.10+** con **Tkinter** | Ventana del proyecto (CRUD + dashboard) |
| **Power BI Desktop** (gratis) | Tablero `.pbix` con gráficas de negocio |
| Conexión a internet (solo la primera vez) | `pip install -r requirements.txt` |

### Comprobar que tienes Tkinter

**macOS** (usa el Python del sistema, no el de Homebrew si falla):

```bash
/usr/bin/python3 -c "import tkinter; print('Tkinter OK')"
```

**Windows** (después de instalar Python desde python.org, marcar “tcl/tk”):

```powershell
python -c "import tkinter; print('Tkinter OK')"
```

Si sale error `No module named '_tkinter'`, reinstala Python activando la opción **tcl/tk** o usa el instalador oficial de python.org.

---

## Paso 1 — Abrir el proyecto

```bash
cd /ruta/donde/clonaste/PROYECTO-FINAL
```

Debes ver carpetas `Backend/`, `Frontend/`, `main.py`, `powerbi/`.

---

## Paso 2 — Instalar dependencias (solo la primera vez)

```bash
python3 -m venv .venv
source .venv/bin/activate          # macOS / Linux
# .venv\Scripts\activate           # Windows (PowerShell)

pip install -r requirements.txt
```

Esto instala:

- **Pillow** — logo PNG en la ventana.
- **pbix-mcp** — genera automáticamente `powerbi/RutaOptima.pbix` con el modelo estrella y medidas DAX.

---

## Paso 3 — Ejecutar la aplicación (dashboard Tkinter)

### Opción recomendada (macOS)

```bash
chmod +x run_gui.sh    # solo la primera vez
./run_gui.sh
```

El script hace dos cosas:

1. Con el **venv**: exporta CSV, actualiza `CADENA_BASE_DATOS.txt` y genera **`powerbi/RutaOptima.pbix`**.
2. Con **`/usr/bin/python3`**: abre la ventana Tkinter (porque suele tener Tkinter en Mac).

### Opción manual

**macOS:**

```bash
source .venv/bin/activate
python -c "from Backend.bootstrap import sincronizar_artefactos_bi; from Backend.base_datos import GestorBaseDatosLogistica; from Backend.config import ruta_base_datos; sincronizar_artefactos_bi(GestorBaseDatosLogistica(ruta_base_datos()))"

PYTHONPATH=. /usr/bin/python3 main.py
```

**Windows / Linux** (si `python` tiene Tkinter):

```bash
set PYTHONPATH=.          # Windows CMD
# export PYTHONPATH=.     # macOS/Linux

python main.py
```

### Qué debes ver en pantalla

1. **Banner azul** con logo y título “Ruta Óptima”.
2. **Dashboard analítico** con:
   - 4 tarjetas KPI (envíos, costo total, peso promedio, km).
   - 4 gráficas (peso por clase, costo por fecha, envíos por zona, km vs peso).
3. **Botones CRUD** (1–4) y **botón 5** para Power BI.

Al **crear, editar o borrar** un envío, las gráficas y KPI se actualizan solas.

---

## Paso 4 — Ver el dashboard en Power BI

### 4.1 Instalar Power BI Desktop

1. Descarga: https://powerbi.microsoft.com/desktop/
2. Instala y abre **Power BI Desktop** (no el servicio web).

### 4.2 Abrir el archivo del proyecto

Tras el **Paso 3**, debe existir:

```
powerbi/RutaOptima.pbix
```

**Forma A — desde Tkinter**

- Pulsa el botón **「5 Abrir Power BI Desktop (RutaOptima.pbix)」**.

**Forma B — manual**

- En Desktop: **Archivo → Abrir → Examinar** → selecciona  
  `PROYECTO-FINAL/powerbi/RutaOptima.pbix`.

**Si el archivo no existe**

```bash
source .venv/bin/activate
python -c "from Backend.generar_pbix import asegurar_archivo_pbix; from Backend.config import ruta_base_datos; print(asegurar_archivo_pbix(ruta_base_datos()))"
```

Si imprime `None`, falta `pbix-mcp`: ejecuta de nuevo `pip install -r requirements.txt`.

### 4.3 Comprobar el modelo de datos

En Power BI Desktop:

1. Icono **Modelo** (diagrama de tablas).
2. Debes ver: `fact_envio`, `dim_fecha`, `dim_zona`, `dim_camion`.
3. Relaciones (muchas → una desde el hecho):
   - `fact_envio[fecha_key]` → `dim_fecha[fecha_key]`
   - `fact_envio[zona_id]` → `dim_zona[zona_id]`
   - `fact_envio[camion_id]` → `dim_camion[camion_id]`

4. En **dim_fecha**, clic derecho → **Marcar como tabla de fechas** → columna `fecha`.

Medidas ya incluidas en el `.pbix` generado (ejemplo):

- `Costo Medio COP por Envio`
- `Total Kg`
- `Total Kms`

### 4.4 Crear la página del dashboard (4 gráficas)

Ve a la vista **Informe** y crea una página llamada **Dashboard Ruta Óptima**.

| # | Visual en Desktop | Campo eje / valores | Objetivo de negocio |
|---|-------------------|---------------------|---------------------|
| 1 | **Gráfico de barras agrupadas** | Eje: `clase_servicio` (fact_envio) · Valores: **Suma** de `peso_kg` | Peso movido por tipo de servicio |
| 2 | **Gráfico de líneas** | Eje: `fecha` (dim_fecha) · Valores: medida **Costo Medio COP por Envio** | Evolución del costo medio |
| 3 | **Gráfico de barras** | Eje: `nombre_localidad` (dim_zona) · Valores: **Recuento** de `envio_id` (fact_envio) | Envíos por localidad |
| 4 | **Gráfico de dispersión** | Eje X: `peso_kg` · Eje Y: `kms_recorrido` · Leyenda: `nombre_localidad` | Relación distancia vs carga |

**Tarjeta KPI extra (opcional):** arrastra la medida **Costo Medio COP por Envio** a un visual **Tarjeta**.

**Columna calculada DAX** (requisito del taller) — en `fact_envio` → **Nueva columna**:

```dax
Clasificacion Riesgo KG =
VAR p = fact_envio[peso_kg]
RETURN
IF (
    p < 2,
    "Tipo documento (ligero)",
    IF ( p <= 30, "Tipo paqueteria (urbano medio)", "Tipo cargo (alto volumen)" )
)
```

Guarda el informe: **Archivo → Guardar** en  
`powerbi/RutaOptima.pbix` (mismo nombre, para el botón 5).

### 4.5 Actualizar datos después de cambios en Tkinter

Cada vez que registres, edites o borres envíos en Tkinter:

1. Los CSV en `powerbi/csv_refresh/` se regeneran automáticamente.
2. En Power BI Desktop: **Inicio → Actualizar** (o botón Actualizar en la cinta).
3. Las gráficas reflejan los datos nuevos.

Ruta SQLite (por si enlazas directo a la BD): está en `powerbi/CADENA_BASE_DATOS.txt`.

---

## Solución de problemas

| Problema | Qué hacer |
|----------|-----------|
| `No module named '_tkinter'` | En Mac: `PYTHONPATH=. /usr/bin/python3 main.py`. En Windows: reinstalar Python con Tcl/Tk. |
| No aparece `RutaOptima.pbix` | Activar venv y `pip install -r requirements.txt`, luego `./run_gui.sh`. |
| Botón 5 dice “archivo ausente” | Ejecutar el bloque `python -c` del apartado 4.2 o `./run_gui.sh`. |
| Power BI no refresca | **Actualizar** en Desktop; revisar que existan CSV en `powerbi/csv_refresh/`. |
| Logo no se ve | `pip install pillow` y comprobar `Frontend/logo_marca.png`. |

---

## Resumen rápido (checklist)

- [ ] `pip install -r requirements.txt`
- [ ] `./run_gui.sh` (o `main.py` con Python que tenga Tkinter)
- [ ] Ver dashboard Tkinter (KPI + 4 gráficas)
- [ ] Abrir `powerbi/RutaOptima.pbix` en Power BI Desktop
- [ ] Crear 4 visuales + 1 medida/columna DAX si aún no están en el informe
- [ ] Guardar `.pbix` y usar **Actualizar** tras cambios en la app

Más detalle técnico del modelo: `powerbi/README_PBI.txt`.
