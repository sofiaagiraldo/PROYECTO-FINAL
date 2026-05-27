# Proyecto final — RETO LOGÍSTICA «Ruta-Óptima»

Ecosistema end-to-end (Python + SQLite modelo estrella + Tkinter + Power BI) según **Taller Final Corte 3 — Programación y Decisiones (UNISABANA)**.

---

## Guía rápida

**Instrucciones completas paso a paso (local + Power BI):**  
👉 **[INSTRUCCIONES_LOCAL.md](INSTRUCCIONES_LOCAL.md)**

### En 4 comandos (macOS)

```bash
cd PROYECTO-FINAL
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
chmod +x run_gui.sh && ./run_gui.sh
```

1. Se abre la **ventana Tkinter** con dashboard (KPI + 4 gráficas) y CRUD.  
2. Se genera **`powerbi/RutaOptima.pbix`**.  
3. En la app, pulsa **botón 5** o abre ese archivo en **Power BI Desktop** y arma las 4 gráficas del informe (ver guía).

---

## Estructura del proyecto

| Elemento | Descripción |
|----------|-------------|
| `Backend/` | POO + SQLite (`fact_envio` + `dim_fecha`, `dim_zona`, `dim_camion`) |
| `Frontend/` | GUI Tkinter + `panel_dashboard.py` (gráficas en vivo) |
| `main.py` | Orquestador: BD, export BI, GUI |
| `run_gui.sh` | Arranque recomendado en Mac (PBIX + Tkinter) |
| `data/ruta_optima.db` | Base SQLite (≥5 filas por tabla al iniciar) |
| `powerbi/` | CSV, `RutaOptima.pbix`, `README_PBI.txt`, `CADENA_BASE_DATOS.txt` |
| `INSTRUCCIONES_LOCAL.md` | **Guía detallada** ejecución y dashboard Power BI |

---

## Reto aplicado

**Ruta Óptima**: peso (kg) + zona destino → clasificación (**Documento** / **Paquetería** / **Carga**) y cotización COP (`Backend/logica_reto.py`), persistida en `fact_envio`.

---

## Dos dashboards en este proyecto

| Dónde | Qué ves | Cómo abrirlo |
|-------|---------|--------------|
| **Tkinter** (app Python) | 4 KPI + 4 gráficas Canvas; se actualiza al CRUD | `./run_gui.sh` o `main.py` |
| **Power BI Desktop** | Informe `.pbix` (modelo estrella + visuales de negocio) | Botón **5** en la app o abrir `powerbi/RutaOptima.pbix` |

El modelo y medidas DAX base se generan solos; las **4 gráficas del informe** en Desktop se crean una vez siguiendo la tabla en [INSTRUCCIONES_LOCAL.md § 4.4](INSTRUCCIONES_LOCAL.md#44-crear-la-página-del-dashboard-4-gráficas).

---

## Ejecución por sistema operativo

### macOS (recomendado)

```bash
./run_gui.sh
```

Si falla solo con `python3`, usa el Python del sistema:

```bash
PYTHONPATH=. /usr/bin/python3 main.py
```

(Genera el `.pbix` antes con el venv activado; ver `INSTRUCCIONES_LOCAL.md`.)

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
$env:PYTHONPATH="."
python main.py
```

Luego abre `powerbi\RutaOptima.pbix` en Power BI Desktop.

---

## Botones de la ventana Tkinter

1. **Registrar** (Create)  
2. **Ver manifiesto** (Read)  
3. **Actualizar** (Update)  
4. **Eliminar** (Delete)  
5. **Abrir Power BI** → `RutaOptima.pbix`  
- **Actualizar artefactos BI** → regenera CSV + `.pbix`

Errores: `messagebox` + `try/except` (la app no debe cerrarse por validaciones de negocio).

---

## Power BI (referencia técnica)

- Guía de visuales y DAX: `powerbi/README_PBI.txt`  
- Ruta SQLite: `powerbi/CADENA_BASE_DATOS.txt` (se actualiza al arrancar)  
- CSV para refresco: `powerbi/csv_refresh/`

---

## Dependencias

```bash
pip install -r requirements.txt
```

- **Pillow** — logo `Frontend/logo_marca.png`  
- **pbix-mcp** — genera `powerbi/RutaOptima.pbix` automáticamente  
- **Tkinter** y **sqlite3** — biblioteca estándar de Python  

---

## Entrega GitHub individual

Publica este proyecto en tu repositorio **personal público** (enlace a repo de un compañero = penalización según rúbrica).
