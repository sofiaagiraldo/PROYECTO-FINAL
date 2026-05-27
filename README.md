# 🚚 Ruta-Óptima — Sistema de Clasificación y Gestión de Envíos

> **Taller Final Corte 3 — Ecosistema Tecnológico End-to-End**  
> Asignatura: Programación y Decisiones | Universidad de La Sabana | 2026-1  
> Reto 1: Logística — "Ruta-Óptima"

---

## 📋 Descripción del Proyecto

**Ruta-Óptima** es un ecosistema tecnológico completo para una empresa de envíos en Bogotá que necesita **clasificar paquetes** antes de cargarlos a los camiones. El sistema permite:

- Registrar envíos ingresando **peso (kg)** y **destino**.
- **Clasificar automáticamente** el paquete: `Documento`, `Paquetería`, `Carga`, `Carga Pesada` o `Sobredimensionado`.
- **Calcular el costo de envío** basado en la tarifa por tipo y la distancia al destino.
- **Generar un manifiesto de carga** ordenado por peso.
- Visualizar indicadores de negocio en **Power BI**.

---

## 🏗️ Arquitectura del Sistema

```
RutaOptima/
│
├── main.py                        ← Orquestador principal (punto de entrada)
├── RutaOptima_Dashboard.pbix      ← Tablero de Power BI
├── README.md                      ← Este archivo
│
├── Backend/
│   ├── __init__.py
│   ├── database.py                ← SQLite: creación de tablas, CRUD, semillas
│   ├── modelos.py                 ← POO: Destino, TipoPaquete, Camion, Envio, ServicioLogistica
│   └── ruta_optima.db             ← Base de datos (generada automáticamente)
│
└── Frontend/
    ├── __init__.py
    └── app.py                     ← Interfaz gráfica Tkinter
```

### Esquema Estrella (SQLite)

```
          dim_destino          dim_tipo_paquete       dim_camion
         ┌───────────┐        ┌─────────────────┐    ┌───────────┐
         │ id_destino│        │ id_tipo          │    │ id_camion │
         │ ciudad    │        │ clasificacion    │    │ placa     │
         │ zona      │        │ peso_min_kg      │    │ capacidad │
         │ distancia │        │ peso_max_kg      │    │ conductor │
         └─────┬─────┘        │ tarifa_base      │    └─────┬─────┘
               │              └────────┬─────────┘          │
               └──────────────────┐    │    ┌───────────────┘
                                  ▼    ▼    ▼
                              ┌─────────────────┐
                              │   fact_envio     │  ← TABLA DE HECHOS
                              │ id_envio (PK)    │
                              │ fecha_envio      │
                              │ remitente        │
                              │ peso_kg          │
                              │ costo_envio      │
                              │ id_destino (FK)  │
                              │ id_tipo    (FK)  │
                              │ id_camion  (FK)  │
                              └─────────────────┘
```

---

## ⚙️ Requisitos Previos

- Python **3.10+**
- Tkinter (incluido con Python en Windows/macOS; en Ubuntu: `sudo apt install python3-tk`)
- Power BI Desktop (para abrir el `.pbix`)
- No se requieren librerías externas — solo la biblioteca estándar de Python.

---

## 🚀 Instrucciones de Ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/<TU_USUARIO>/RutaOptima.git
cd RutaOptima
```

### 2. Ejecutar la aplicación

```bash
python main.py
```

Esto:
1. Crea automáticamente la base de datos `Backend/ruta_optima.db` (si no existe).
2. Inserta los datos semilla (mínimo 5 registros por tabla).
3. Abre la ventana principal de la interfaz gráfica.

### 3. Abrir el tablero de Power BI

Desde la interfaz, haga clic en el botón **"📊 ABRIR POWER BI"**. También puede abrir `RutaOptima_Dashboard.pbix` directamente con Power BI Desktop.

> **Nota sobre la conexión en Power BI:** Abra el archivo `.pbix`, vaya a *Transformar datos → Configuración del origen de datos* y actualice la ruta al archivo `Backend/ruta_optima.db` con la ruta absoluta en su equipo.

---

## 🖥️ Funcionalidades de la Interfaz

| Botón | Función |
|---|---|
| ➕ **REGISTRAR** | Crea un nuevo envío con clasificación y costo automáticos |
| 📋 **VER TABLA** | Recarga el manifiesto desde la base de datos |
| ✏️ **ACTUALIZAR** | Modifica el envío seleccionado en la tabla |
| 🗑️ **ELIMINAR** | Elimina el envío seleccionado (con confirmación) |
| 📊 **ABRIR POWER BI** | Lanza el archivo `.pbix` en Power BI Desktop |
| 📄 **MANIFIESTO** | Muestra el manifiesto completo ordenado por peso |

---

## 📊 Power BI — Tablero de Inteligencia de Negocios

El archivo `.pbix` incluye:

### Modelo Estrella
- Relaciones activas entre `fact_envio` y las tres dimensiones.
- Tabla Calendario conectada para análisis temporal.

### Gráficas (mínimo 4)
1. **Envíos por Tipo de Paquete** — Gráfico de torta
2. **Ingresos por Destino** — Gráfico de barras
3. **Evolución Mensual de Envíos** — Gráfico de línea (serie temporal)
4. **Top Remitentes por Costo Total** — Gráfico de barras horizontal

### Medidas DAX
```dax
// MEDIDA DAX: Total Ingresos
Total Ingresos = SUM(fact_envio[costo_envio])

// MEDIDA DAX: Promedio Costo por Envío
Promedio Costo = DIVIDE(SUM(fact_envio[costo_envio]), COUNTROWS(fact_envio))

// MEDIDA DAX: Crecimiento MoM
Crecimiento MoM =
DIVIDE(
    [Total Ingresos] - CALCULATE([Total Ingresos], PREVIOUSMONTH(Calendario[Fecha])),
    CALCULATE([Total Ingresos], PREVIOUSMONTH(Calendario[Fecha]))
)
```

### Columna Calculada DAX
```dax
// COLUMNA CALCULADA: Franja de costo
Franja Costo =
IF(fact_envio[costo_envio] < 20000, "Económico",
   IF(fact_envio[costo_envio] < 60000, "Estándar", "Premium"))
```

---

## 📐 Reglas de Clasificación de Paquetes

| Clasificación | Rango de Peso |
|---|---|
| Documento | < 0.5 kg |
| Paquetería | 0.5 kg – 5.0 kg |
| Carga | 5.0 kg – 30.0 kg |
| Carga Pesada | 30.0 kg – 100.0 kg |
| Sobredimensionado | > 100.0 kg |

**Fórmula de costo:**
```
Costo = Tarifa Base + (Distancia km × $50 × Peso kg)
```

---

## 👥 Integrantes del Grupo

- [Nombre Integrante 1]
- [Nombre Integrante 2]
- [Nombre Integrante 3]

---

## 📚 Tecnologías Utilizadas

| Capa | Tecnología |
|---|---|
| Backend | Python 3.10+, SQLite3, POO |
| Frontend | Tkinter (GUI) |
| Base de Datos | SQLite (Esquema Estrella) |
| BI | Microsoft Power BI Desktop |
| Control de Versiones | Git / GitHub |
