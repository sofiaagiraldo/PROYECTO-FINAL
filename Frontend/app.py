"""
app.py
Interfaz Gráfica (Frontend) para Ruta-Óptima usando Tkinter.
Incluye CRUD completo, botón Power BI y manejo de excepciones.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import sys
import os
from datetime import date

# Ruta al .pbix (relativa al main.py)
PBIX_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "RutaOptima_Dashboard.pbix")


class RutaOptimaApp(tk.Tk):
    """Ventana principal de la aplicación Ruta-Óptima."""

    # ── Paleta de colores ─────────────────────────────────────────────────────
    COLOR_BG       = "#0D1B2A"   # Azul marino oscuro
    COLOR_PANEL    = "#1B2838"   # Panel lateral
    COLOR_ACCENT   = "#F0A500"   # Amarillo logístico
    COLOR_ACCENT2  = "#00C2C7"   # Cian
    COLOR_TEXT     = "#E8EAF0"
    COLOR_SUBTEXT  = "#8892A4"
    COLOR_SUCCESS  = "#27AE60"
    COLOR_DANGER   = "#E74C3C"
    COLOR_ROW_ODD  = "#151F2E"
    COLOR_ROW_EVEN = "#1B2838"

    def __init__(self):
        super().__init__()
        self.title("🚚 Ruta-Óptima — Sistema de Clasificación de Envíos")
        self.geometry("1100x680")
        self.resizable(True, True)
        self.configure(bg=self.COLOR_BG)

        # Servicio de lógica
        try:
            from Backend.modelos import ServicioLogistica
            self.servicio = ServicioLogistica()
        except Exception as e:
            messagebox.showerror("Error de inicio",
                                 f"No se pudo inicializar la base de datos:\n{e}")
            self.destroy()
            return

        self._cargar_catalogos()
        self._construir_ui()
        self._cargar_tabla()

    # ── Catálogos ─────────────────────────────────────────────────────────────
    def _cargar_catalogos(self):
        try:
            self.destinos = self.servicio.obtener_destinos()  # (id, ciudad, zona, km)
            self.camiones = self.servicio.obtener_camiones()  # (id, placa, conductor)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar catálogos:\n{e}")
            self.destinos = []
            self.camiones = []

    # ── Construcción de UI ────────────────────────────────────────────────────
    def _construir_ui(self):
        # Encabezado
        header = tk.Frame(self, bg=self.COLOR_PANEL, height=70)
        header.pack(fill="x")
        tk.Label(header, text="🚚  RUTA-ÓPTIMA",
                 font=("Courier New", 22, "bold"),
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACCENT).pack(side="left", padx=20, pady=12)
        tk.Label(header, text="Sistema de Clasificación y Gestión de Envíos — Bogotá",
                 font=("Courier New", 10),
                 bg=self.COLOR_PANEL, fg=self.COLOR_SUBTEXT).pack(side="left", padx=5)

        # Contenedor principal
        main = tk.Frame(self, bg=self.COLOR_BG)
        main.pack(fill="both", expand=True, padx=15, pady=10)

        # Panel izquierdo: formulario
        left = tk.Frame(main, bg=self.COLOR_PANEL, width=320, bd=0)
        left.pack(side="left", fill="y", padx=(0, 10))
        left.pack_propagate(False)
        self._construir_formulario(left)

        # Panel derecho: tabla
        right = tk.Frame(main, bg=self.COLOR_BG)
        right.pack(side="left", fill="both", expand=True)
        self._construir_tabla(right)

        # Barra inferior: botones CRUD + Power BI
        self._construir_botones()

    def _lbl(self, parent, text):
        tk.Label(parent, text=text,
                 font=("Courier New", 9, "bold"),
                 bg=self.COLOR_PANEL, fg=self.COLOR_SUBTEXT).pack(anchor="w", padx=15, pady=(8, 0))

    def _construir_formulario(self, parent):
        tk.Label(parent, text="NUEVO / EDITAR ENVÍO",
                 font=("Courier New", 11, "bold"),
                 bg=self.COLOR_PANEL, fg=self.COLOR_ACCENT2).pack(pady=(15, 5))

        # ID (solo lectura)
        self._lbl(parent, "ID Envío (solo lectura)")
        self.entry_id = ttk.Entry(parent, state="readonly")
        self.entry_id.pack(fill="x", padx=15)

        # Fecha
        self._lbl(parent, "Fecha (YYYY-MM-DD)")
        self.entry_fecha = ttk.Entry(parent)
        self.entry_fecha.insert(0, str(date.today()))
        self.entry_fecha.pack(fill="x", padx=15)

        # Remitente
        self._lbl(parent, "Remitente")
        self.entry_remitente = ttk.Entry(parent)
        self.entry_remitente.pack(fill="x", padx=15)

        # Peso
        self._lbl(parent, "Peso (kg)")
        self.entry_peso = ttk.Entry(parent)
        self.entry_peso.pack(fill="x", padx=15)

        # Destino
        self._lbl(parent, "Destino")
        dest_names = [f"{d[1]} ({d[2]})" for d in self.destinos]
        self.combo_destino = ttk.Combobox(parent, values=dest_names, state="readonly")
        if dest_names:
            self.combo_destino.current(0)
        self.combo_destino.pack(fill="x", padx=15)

        # Camión
        self._lbl(parent, "Camión")
        cam_names = [f"{c[1]} — {c[2]}" for c in self.camiones]
        self.combo_camion = ttk.Combobox(parent, values=cam_names, state="readonly")
        if cam_names:
            self.combo_camion.current(0)
        self.combo_camion.pack(fill="x", padx=15)

        # Resultado clasificación
        self._lbl(parent, "Clasificación calculada")
        self.lbl_clasificacion = tk.Label(
            parent, text="—",
            font=("Courier New", 10, "bold"),
            bg=self.COLOR_PANEL, fg=self.COLOR_ACCENT
        )
        self.lbl_clasificacion.pack(anchor="w", padx=15)

        self.lbl_costo = tk.Label(
            parent, text="Costo: —",
            font=("Courier New", 10, "bold"),
            bg=self.COLOR_PANEL, fg=self.COLOR_SUCCESS
        )
        self.lbl_costo.pack(anchor="w", padx=15, pady=(0, 15))

        # Estilos ttk
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TEntry",
                        fieldbackground="#263547", foreground=self.COLOR_TEXT,
                        insertcolor=self.COLOR_TEXT, bordercolor="#2E4057")
        style.configure("TCombobox",
                        fieldbackground="#263547", foreground=self.COLOR_TEXT,
                        selectbackground=self.COLOR_ACCENT)

    def _construir_tabla(self, parent):
        tk.Label(parent, text="MANIFIESTO DE ENVÍOS (ordenado por peso)",
                 font=("Courier New", 10, "bold"),
                 bg=self.COLOR_BG, fg=self.COLOR_ACCENT2).pack(anchor="w", pady=(0, 5))

        cols = ("ID", "Fecha", "Remitente", "Peso (kg)",
                "Costo (COP)", "Destino", "Tipo", "Camión")
        style = ttk.Style(self)
        style.configure("Custom.Treeview",
                        background=self.COLOR_ROW_ODD,
                        foreground=self.COLOR_TEXT,
                        rowheight=26,
                        fieldbackground=self.COLOR_ROW_ODD,
                        font=("Courier New", 9))
        style.configure("Custom.Treeview.Heading",
                        background=self.COLOR_ACCENT,
                        foreground="#000000",
                        font=("Courier New", 9, "bold"))
        style.map("Custom.Treeview",
                  background=[("selected", self.COLOR_ACCENT2)])

        frame_tree = tk.Frame(parent, bg=self.COLOR_BG)
        frame_tree.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame_tree, columns=cols,
                                  show="headings", style="Custom.Treeview")
        widths = [40, 90, 150, 80, 120, 130, 120, 110]
        for col, w in zip(cols, widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="center")

        sb_y = ttk.Scrollbar(frame_tree, orient="vertical",
                              command=self.tree.yview)
        sb_x = ttk.Scrollbar(frame_tree, orient="horizontal",
                              command=self.tree.xview)
        self.tree.configure(yscrollcommand=sb_y.set, xscrollcommand=sb_x.set)

        sb_y.pack(side="right", fill="y")
        sb_x.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self._on_seleccion)

    def _construir_botones(self):
        bar = tk.Frame(self, bg=self.COLOR_PANEL, height=55)
        bar.pack(fill="x", side="bottom")
        bar.pack_propagate(False)

        def btn(text, cmd, color):
            b = tk.Button(bar, text=text, command=cmd,
                          font=("Courier New", 10, "bold"),
                          bg=color, fg="#000000" if color == self.COLOR_ACCENT else "#FFFFFF",
                          relief="flat", padx=18, pady=8, cursor="hand2",
                          activebackground=color)
            b.pack(side="left", padx=8, pady=8)
            return b

        btn("➕  REGISTRAR",   self.registrar,  self.COLOR_SUCCESS)
        btn("📋  VER TABLA",   self._cargar_tabla, self.COLOR_ACCENT2)
        btn("✏️  ACTUALIZAR",  self.actualizar,  "#3498DB")
        btn("🗑️  ELIMINAR",    self.eliminar,   self.COLOR_DANGER)
        btn("📊  ABRIR POWER BI", self.abrir_powerbi, self.COLOR_ACCENT)

        # Manifiesto
        btn("📄  MANIFIESTO",  self.ver_manifiesto, "#7D3C98")

    # ── Eventos ───────────────────────────────────────────────────────────────
    def _on_seleccion(self, event):
        """Carga fila seleccionada en el formulario."""
        sel = self.tree.selection()
        if not sel:
            return
        vals = self.tree.item(sel[0], "values")
        # vals: ID, Fecha, Remitente, Peso, Costo, Destino, Tipo, Camión
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, "end")
        self.entry_id.insert(0, vals[0])
        self.entry_id.config(state="readonly")

        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, vals[1])

        self.entry_remitente.delete(0, "end")
        self.entry_remitente.insert(0, vals[2])

        self.entry_peso.delete(0, "end")
        self.entry_peso.insert(0, vals[3])

        # Seleccionar destino
        dest_ciudad = vals[5]
        for i, d in enumerate(self.destinos):
            if d[1] == dest_ciudad:
                self.combo_destino.current(i)
                break

        # Seleccionar camión
        cam_placa = vals[7]
        for i, c in enumerate(self.camiones):
            if c[1] == cam_placa:
                self.combo_camion.current(i)
                break

        self.lbl_clasificacion.config(text=vals[6])
        costo_raw = vals[4].replace("$", "").replace(",", "").strip()
        self.lbl_costo.config(text=f"Costo: ${float(costo_raw):,.0f} COP")

    def _leer_formulario(self):
        """Retorna los datos del formulario validados."""
        fecha     = self.entry_fecha.get().strip()
        remitente = self.entry_remitente.get().strip()
        peso_str  = self.entry_peso.get().strip()

        if not fecha or not remitente or not peso_str:
            raise ValueError("Todos los campos son obligatorios.")

        try:
            peso_kg = float(peso_str)
        except ValueError:
            raise ValueError("El peso debe ser un número válido.")

        if peso_kg <= 0:
            raise ValueError("El peso debe ser mayor a 0.")

        idx_dest = self.combo_destino.current()
        idx_cam  = self.combo_camion.current()
        if idx_dest < 0 or idx_cam < 0:
            raise ValueError("Seleccione un destino y un camión.")

        id_destino = self.destinos[idx_dest][0]
        id_camion  = self.camiones[idx_cam][0]
        return fecha, remitente, peso_kg, id_destino, id_camion

    # ── CRUD ──────────────────────────────────────────────────────────────────
    def registrar(self):
        try:
            fecha, remitente, peso_kg, id_destino, id_camion = self._leer_formulario()
            new_id, costo = self.servicio.registrar_envio(
                fecha, remitente, peso_kg, id_destino, id_camion)
            from Backend.modelos import Envio
            tipo = Envio.clasificar(peso_kg)
            self.lbl_clasificacion.config(text=tipo)
            self.lbl_costo.config(text=f"Costo: ${costo:,.0f} COP")
            messagebox.showinfo("✅ Registrado",
                                f"Envío #{new_id} registrado correctamente.\n"
                                f"Tipo: {tipo}\nCosto: ${costo:,.0f} COP")
            self._cargar_tabla()
            self._limpiar_formulario()
        except ValueError as e:
            messagebox.showwarning("⚠️ Validación", str(e))
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al registrar:\n{e}")

    def actualizar(self):
        try:
            id_str = self.entry_id.get().strip()
            if not id_str:
                raise ValueError("Seleccione un envío de la tabla para actualizar.")
            id_envio = int(id_str)
            fecha, remitente, peso_kg, id_destino, id_camion = self._leer_formulario()
            self.servicio.modificar_envio(
                id_envio, fecha, remitente, peso_kg, id_destino, id_camion)
            messagebox.showinfo("✅ Actualizado",
                                f"Envío #{id_envio} actualizado correctamente.")
            self._cargar_tabla()
            self._limpiar_formulario()
        except ValueError as e:
            messagebox.showwarning("⚠️ Validación", str(e))
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al actualizar:\n{e}")

    def eliminar(self):
        try:
            id_str = self.entry_id.get().strip()
            if not id_str:
                raise ValueError("Seleccione un envío de la tabla para eliminar.")
            id_envio = int(id_str)
            confirmar = messagebox.askyesno(
                "Confirmar", f"¿Eliminar el envío #{id_envio}? Esta acción no se puede deshacer.")
            if confirmar:
                self.servicio.borrar_envio(id_envio)
                messagebox.showinfo("✅ Eliminado",
                                    f"Envío #{id_envio} eliminado correctamente.")
                self._cargar_tabla()
                self._limpiar_formulario()
        except ValueError as e:
            messagebox.showwarning("⚠️ Validación", str(e))
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al eliminar:\n{e}")

    def _cargar_tabla(self):
        try:
            for item in self.tree.get_children():
                self.tree.delete(item)
            rows = self.servicio.listar_envios()
            for i, r in enumerate(rows):
                id_e, fecha, rem, peso, costo, ciudad, tipo, placa = r
                tag = "odd" if i % 2 == 0 else "even"
                self.tree.insert("", "end", tags=(tag,),
                                 values=(id_e, fecha, rem,
                                         f"{peso:.2f}",
                                         f"${costo:,.0f}",
                                         ciudad, tipo, placa))
            self.tree.tag_configure("odd",  background=self.COLOR_ROW_ODD)
            self.tree.tag_configure("even", background=self.COLOR_ROW_EVEN)
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error al cargar datos:\n{e}")

    def _limpiar_formulario(self):
        self.entry_id.config(state="normal")
        self.entry_id.delete(0, "end")
        self.entry_id.config(state="readonly")
        self.entry_fecha.delete(0, "end")
        self.entry_fecha.insert(0, str(date.today()))
        self.entry_remitente.delete(0, "end")
        self.entry_peso.delete(0, "end")
        self.lbl_clasificacion.config(text="—")
        self.lbl_costo.config(text="Costo: —")

    def ver_manifiesto(self):
        try:
            lineas = self.servicio.generar_manifiesto()
            win = tk.Toplevel(self)
            win.title("📄 Manifiesto de Carga")
            win.configure(bg=self.COLOR_BG)
            win.geometry("900x400")
            txt = tk.Text(win, bg="#0D1B2A", fg=self.COLOR_TEXT,
                          font=("Courier New", 9), relief="flat")
            txt.pack(fill="both", expand=True, padx=10, pady=10)
            txt.insert("end", "\n".join(lineas))
            txt.config(state="disabled")
        except Exception as e:
            messagebox.showerror("❌ Error", f"No se pudo generar el manifiesto:\n{e}")

    # ── Power BI ──────────────────────────────────────────────────────────────
    def abrir_powerbi(self):
        try:
            if not os.path.exists(PBIX_PATH):
                messagebox.showwarning(
                    "⚠️ Archivo no encontrado",
                    f"No se encontró el archivo Power BI en:\n{PBIX_PATH}\n\n"
                    "Asegúrese de tener el archivo .pbix en la carpeta raíz del proyecto.")
                return
            if sys.platform == "win32":
                os.startfile(PBIX_PATH)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", PBIX_PATH])
            else:
                subprocess.Popen(["xdg-open", PBIX_PATH])
            messagebox.showinfo("📊 Power BI",
                                "Abriendo el tablero de Power BI...\n"
                                "Si no se abre, verifique que Power BI Desktop esté instalado.")
        except Exception as e:
            messagebox.showerror("❌ Error al abrir Power BI",
                                 f"No se pudo abrir el archivo .pbix:\n{e}")


def iniciar():
    app = RutaOptimaApp()
    app.mainloop()
