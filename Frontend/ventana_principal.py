"""Interfaz Tkinter - Reto Logistica Ruta Optima.

Cuatro botones CRUD funcionales mas abrir archivo Power BI. Errores con messagebox."""

from __future__ import annotations

import platform
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from Backend.bootstrap import sincronizar_artefactos_bi
from Backend.config import ruta_pbix_esperado
from Backend.entidades import RegistroEnvio
from Frontend.panel_dashboard import PanelDashboard

# Paleta alineada con marca (azul corporativo + naranja acento).
COLOR_NAVY = "#1B2D4A"
COLOR_NAVY_MID = "#243B63"
COLOR_ORANGE = "#E85D21"
COLOR_ORANGE_DARK = "#C94A14"
COLOR_BG_PAGE = "#EEF2F8"
COLOR_CARD = "#FFFFFF"
COLOR_MUTED_TEXT = "#5C6F82"
ALT_ROW = "#F7F9FC"


def _open_pbix(p: Path) -> None:
    s = platform.system()
    if s == "Darwin":
        subprocess.run(["open", str(p)], check=True)
    elif s == "Windows":
        subprocess.run(["cmd", "/c", "start", "", str(p)], check=True)
    else:
        subprocess.run(["xdg-open", str(p)], check=True)


def _labels(pairs: list[tuple[int, str]]) -> list[str]:
    return [f"{i} | {txt}" for i, txt in pairs]


def _pid(sel: str) -> int:
    return int(sel.split("|", 1)[0].strip())


def _set_pick(cb: ttk.Combobox, pairs: list[tuple[int, str]], want_id: int) -> None:
    vals = _labels(pairs)
    cb["values"] = vals
    for idx, lbl in enumerate(vals):
        if _pid(lbl) == want_id:
            cb.current(idx)
            return


def _cargar_logo(repo_root: Path) -> tk.PhotoImage | None:
    marca = repo_root / "Frontend" / "logo_marca.png"
    respaldo_gif = repo_root / "Frontend" / "logo.gif"

    rutas_try = []
    if marca.exists():
        rutas_try.append(marca)
    if respaldo_gif.exists():
        rutas_try.append(respaldo_gif)

    for ruta in rutas_try:
        try:
            from PIL import Image, ImageTk

            im = Image.open(ruta).convert("RGBA")
            alto_objetivo = 96
            ancho = max(int(im.width * alto_objetivo / im.height), 72)
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            im = im.resize((ancho, alto_objetivo), resample)
            return ImageTk.PhotoImage(im)
        except ImportError:
            break
        except OSError:
            continue
        except Exception:
            continue

    for ruta in rutas_try:
        if ruta.suffix.lower() == ".gif":
            try:
                return tk.PhotoImage(file=str(ruta))
            except tk.TclError:
                continue
    return None


def _estilo_dashboard(root: tk.Tk, style: ttk.Style) -> None:
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    root.configure(background=COLOR_BG_PAGE)

    style.configure(".", font=("Segoe UI", 11), background=COLOR_BG_PAGE)
    style.configure(
        "AppHeader.TLabel",
        font=("Segoe UI", 17, "bold"),
        foreground=COLOR_NAVY,
        background=COLOR_BG_PAGE,
    )
    style.configure(
        "Muted.TLabel",
        font=("Segoe UI", 10),
        foreground=COLOR_MUTED_TEXT,
        background=COLOR_BG_PAGE,
    )
    style.configure(
        "Card.TLabelframe",
        background=COLOR_CARD,
        relief="solid",
        borderwidth=1,
    )
    style.configure(
        "CardTitle.TLabelframe.Label",
        font=("Segoe UI", 11, "bold"),
        foreground=COLOR_NAVY,
        background=COLOR_CARD,
    )
    style.configure("Card.Inner.TFrame", background=COLOR_CARD)
    style.configure(
        "TButton",
        font=("Segoe UI", 11),
        padding=(12, 8),
        background="#E4EAF3",
        foreground=COLOR_NAVY,
    )
    style.map(
        "TButton",
        background=[("pressed", COLOR_NAVY_MID), ("active", "#D0DBED")],
        foreground=[("pressed", "#ffffff"), ("active", COLOR_NAVY)],
    )
    style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
    style.configure(
        "Treeview.Heading",
        font=("Segoe UI", 10, "bold"),
        background=COLOR_NAVY,
        foreground="#FFFFFF",
        padding=(6, 6),
    )
    style.map("Treeview", background=[("selected", COLOR_ORANGE)])
    style.map(
        "Treeview.Heading",
        background=[("active", COLOR_NAVY_MID), ("pressed", COLOR_NAVY_MID)],
    )


def _boton_accento(master: tk.Misc, texto: str, comando) -> tk.Button:
    b = tk.Button(
        master,
        text=texto,
        command=comando,
        font=("Segoe UI", 11, "bold"),
        bg=COLOR_ORANGE,
        fg="#FFFFFF",
        activebackground=COLOR_ORANGE_DARK,
        activeforeground="#FFFFFF",
        relief="flat",
        padx=18,
        pady=11,
        cursor="hand2",
        highlightthickness=0,
        borderwidth=0,
    )
    return b


def _boton_secundario(master: tk.Misc, texto: str, comando) -> ttk.Button:
    return ttk.Button(master, text=texto, command=comando)


def _formulario(root: tk.Tk, repo, base: RegistroEnvio | None) -> RegistroEnvio | None:
    zon, cam, fec = repo.combos_zonas_camiones_fechas()
    win = tk.Toplevel(root)
    win.configure(bg=COLOR_BG_PAGE)
    win.grab_set()
    win.title("Registrar envio" if base is None else "Actualizar envio")

    f = tk.Frame(win, bg=COLOR_CARD, padx=18, pady=18, highlightbackground=COLOR_NAVY, highlightthickness=1)
    f.pack(fill="both", expand=True)

    tk.Label(f, text="Peso (kg)", font=("Segoe UI", 10, "bold"), bg=COLOR_CARD, fg=COLOR_NAVY).grid(
        row=0, column=0, sticky="w"
    )
    vp = tk.StringVar(value="" if base is None else str(base.peso_kg))
    ttk.Entry(f, textvariable=vp, width=40).grid(row=0, column=1, padx=(12, 0), sticky="w")

    tk.Label(f, text="Zona Bogota", bg=COLOR_CARD, fg=COLOR_NAVY).grid(row=1, column=0, sticky="w", pady=(14, 0))
    vz = tk.StringVar()
    cz = ttk.Combobox(f, textvariable=vz, state="readonly", width=52)
    cz["values"] = _labels(zon)
    cz.grid(row=1, column=1, padx=(12, 0), pady=(14, 0), sticky="ew")
    if cz["values"]:
        cz.current(0)

    tk.Label(f, text="Camion", bg=COLOR_CARD, fg=COLOR_NAVY).grid(row=2, column=0, sticky="w", pady=(12, 0))
    vc = tk.StringVar()
    cc = ttk.Combobox(f, textvariable=vc, state="readonly", width=52)
    cc["values"] = _labels(cam)
    cc.grid(row=2, column=1, padx=(12, 0), pady=(12, 0), sticky="ew")
    if cc["values"]:
        cc.current(0)

    tk.Label(f, text="Fecha", bg=COLOR_CARD, fg=COLOR_NAVY).grid(row=3, column=0, sticky="w", pady=(12, 0))
    vf = tk.StringVar()
    cf = ttk.Combobox(f, textvariable=vf, state="readonly", width=52)
    cf["values"] = _labels(fec)
    cf.grid(row=3, column=1, padx=(12, 0), pady=(12, 0), sticky="ew")
    if cf["values"]:
        cf.current(0)

    if base is not None:
        _set_pick(cz, zon, base.zona_id)
        _set_pick(cc, cam, base.camion_id)
        _set_pick(cf, fec, base.fecha_key)

    out: dict[str, RegistroEnvio | None] = {"r": None}

    def guardar():
        try:
            peso = float(vp.get().replace(",", ".").strip())
        except ValueError:
            messagebox.showerror("Peso", "Numero invalido.", parent=win)
            return
        if peso <= 0:
            messagebox.showwarning("Peso", "Debe ser mayor que cero.", parent=win)
            return
        try:
            fk = _pid(vf.get())
            zid = _pid(vz.get())
            cid = _pid(vc.get())
        except (ValueError, tk.TclError, IndexError):
            messagebox.showerror("Formulario", "Seleccion incompleta.", parent=win)
            return
        out["r"] = RegistroEnvio(
            envio_id=None if base is None else base.envio_id,
            fecha_key=fk,
            zona_id=zid,
            camion_id=cid,
            peso_kg=round(peso, 4),
        )
        win.destroy()

    bar = tk.Frame(f, bg=COLOR_CARD)
    bar.grid(row=6, column=0, columnspan=2, pady=(22, 0), sticky="ew")
    bt_ok = tk.Button(
        bar,
        text=" Guardar en SQLite ",
        command=guardar,
        bg=COLOR_ORANGE,
        fg="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        relief="flat",
        padx=16,
        pady=10,
        cursor="hand2",
    )
    bt_ok.pack(side="left")
    tk.Button(bar, text=" Cancelar ", command=win.destroy, relief="groove").pack(side="left", padx=(10, 0))

    f.columnconfigure(1, weight=1)
    root.wait_window(win)
    return out["r"]


def _sync_bi(gestor) -> None:
    sincronizar_artefactos_bi(gestor)


def lanzar_gui(repo_root: Path, gestor, repo) -> None:
    root = tk.Tk()
    root.title("Ruta Optima - Logistica Bogota - SQLite / Tkinter / Power BI")
    root.geometry("1020x920")
    root.minsize(980, 820)

    estilo = ttk.Style(root)
    _estilo_dashboard(root, estilo)

    banner = tk.Frame(root, bg=COLOR_NAVY, padx=20, pady=16)
    banner.pack(fill="x")

    cab = tk.Frame(banner, bg=COLOR_NAVY)
    cab.pack(side="left", fill="y")

    foto = _cargar_logo(repo_root)
    if foto is not None:
        tk.Label(cab, image=foto, bg=COLOR_NAVY).pack(side="left", padx=(0, 16))
        root._logo_photo_ref = foto

    texto_cab = tk.Frame(cab, bg=COLOR_NAVY)
    texto_cab.pack(side="left", fill="y")
    tk.Label(
        texto_cab,
        text="Ruta Optima",
        font=("Segoe UI", 21, "bold"),
        fg="#FFFFFF",
        bg=COLOR_NAVY,
    ).pack(anchor="w")
    tk.Label(
        texto_cab,
        text="CLASIFICA  |  CALCULA  |  CONECTA",
        font=("Segoe UI", 11),
        fg="#FFB380",
        bg=COLOR_NAVY,
    ).pack(anchor="w", pady=(4, 0))
    tk.Label(
        texto_cab,
        text="Dashboard operativo: CRUD modelo estrella y export paralelo CSV para BI.",
        font=("Segoe UI", 10),
        fg="#C9D6EC",
        bg=COLOR_NAVY,
        justify="left",
    ).pack(anchor="w", pady=(6, 0))

    contenido = ttk.Frame(root, padding=(20, 18))
    contenido.pack(fill="both", expand=True)

    ttk.Label(
        contenido,
        text="Acciones disponibles:",
        style="AppHeader.TLabel",
    ).pack(anchor="w")

    subt = (
        "Cada alta, edicion o borrado en fact_envio vuelca archivos CSV en "
        "powerbi/csv_refresh/. Usa despues Actualizar datos en Desktop."
    )
    ttk.Label(contenido, text=subt, wraplength=900, justify="left", style="Muted.TLabel").pack(
        anchor="w", pady=(4, 12)
    )

    panel_dashboard = PanelDashboard(contenido, gestor)
    panel_dashboard.pack(fill="both", expand=True, pady=(0, 14))
    panel_dashboard.refrescar()

    def _refrescar_vista() -> None:
        panel_dashboard.refrescar()

    tarjeta = ttk.LabelFrame(contenido, text=" Mantenimiento de envios CRUD DB ", padding=16, style="Card.TLabelframe")
    tarjeta.pack(fill="x", anchor="nw")

    area_acciones = tk.Frame(tarjeta, bg=COLOR_CARD)
    area_acciones.pack(fill="x")

    def crear():
        try:
            reg = _formulario(root, repo, None)
            if reg is None:
                return
            nuevo = repo.crear_envio(reg)
            _sync_bi(gestor)
            _refrescar_vista()
            messagebox.showinfo("Create", "Guardado OK. envio_id=%s" % nuevo)
        except Exception as exc:
            messagebox.showerror("Registrar", str(exc))

    def leer():
        try:
            rows = repo.listar_manifiesto_orden_peso()
            win_l = tk.Toplevel(root)
            win_l.configure(bg=COLOR_BG_PAGE)
            win_l.title("Read - Manifiesto (peso descendente)")
            frm_l = tk.Frame(win_l, bg=COLOR_CARD, padx=10, pady=10)
            frm_l.pack(fill="both", expand=True)
            tk.Label(
                frm_l,
                text="Lista ordenada por peso cargado sobre el tractocamion (kg).",
                bg=COLOR_CARD,
                fg=COLOR_NAVY,
                font=("Segoe UI", 11, "bold"),
            ).pack(anchor="w", pady=(0, 8))

            outer = tk.Frame(frm_l, bg=COLOR_CARD)
            outer.pack(fill="both", expand=True)

            cols = ("id", "fecha", "zona", "placa", "kg", "clase", "cop", "km")
            headings = ("ID", "Fecha", "Localidad", "Placa", "Kg", "Clase", "COP", "Km")
            widths = (48, 100, 200, 80, 78, 120, 100, 60)

            tv = ttk.Treeview(outer, columns=cols, show="headings", height=14)
            for col, ht, wd in zip(cols, headings, widths):
                tv.heading(col, text=ht)
                tv.column(col, width=wd, anchor="center")

            sb = ttk.Scrollbar(outer, orient="vertical", command=tv.yview)
            tv.configure(yscrollcommand=sb.set)
            tv.pack(side="left", fill="both", expand=True)
            sb.pack(side="right", fill="y")

            for i, row in enumerate(rows):
                tag = "alt" if i % 2 else "plain"
                tv.insert(
                    "",
                    "end",
                    values=(
                        row["envio_id"],
                        row["fecha"],
                        row["nombre_localidad"],
                        row["placa"],
                        "%.3f" % row["peso_kg"],
                        row["clase_servicio"],
                        row["costo_estimado_cop"],
                        "%.2f" % row["kms_recorrido"],
                    ),
                    tags=(tag,),
                )
            tv.tag_configure("alt", background=ALT_ROW)
            tv.tag_configure("plain", background="#FFFFFF")

        except Exception as exc:
            messagebox.showerror("Ver tabla Read", str(exc))

    def actualizar():
        try:
            eid = simpledialog.askinteger("Update", "Ingrese envio_id:", parent=root)
            if eid is None:
                return
            base = repo.obtener_envio(eid)
            reg = _formulario(root, repo, base)
            if reg is None:
                return
            repo.actualizar_envio(reg)
            _sync_bi(gestor)
            _refrescar_vista()
            messagebox.showinfo("Update", "Actualizado envio_id=%s" % eid)
        except Exception as exc:
            messagebox.showerror("Update", str(exc))

    def eliminar():
        try:
            eid = simpledialog.askinteger("Delete", "Ingrese envio_id:", parent=root)
            if eid is None:
                return
            if not messagebox.askyesno(
                "Confirmar",
                "Eliminar permanentemente envio_id=%s en SQLite?" % eid,
                parent=root,
            ):
                return
            repo.borrar_envio(eid)
            _sync_bi(gestor)
            _refrescar_vista()
            messagebox.showinfo("Delete", "Fila borrada desde fact_envio.")
        except Exception as exc:
            messagebox.showerror("Delete", str(exc))

    def abrir_power_bi():
        try:
            pb = ruta_pbix_esperado()
            if not pb.exists():
                messagebox.showwarning(
                    "Power BI",
                    "Archivo ausente:\n%s\n\n"
                    "1) En terminal: pip install -r requirements.txt\n"
                    "2) Ejecute: ./run_gui.sh\n"
                    "3) Abra el .pbix en Power BI Desktop\n\n"
                    "Guia paso a paso: INSTRUCCIONES_LOCAL.md (seccion 4)." % pb,
                    parent=root,
                )
                return
            _open_pbix(pb)
        except Exception as exc:
            messagebox.showerror("Power BI", str(exc))

    def refrescar_bi():
        try:
            _sync_bi(gestor)
            _refrescar_vista()
            pb = ruta_pbix_esperado()
            extra = "\nRutaOptima.pbix actualizado." if pb.exists() else ""
            messagebox.showinfo("BI", "CSV, CADENA_BASE_DATOS.txt y modelo PBIX regenerados." + extra)
        except Exception as exc:
            messagebox.showerror("BI", str(exc))

    g1 = tk.Frame(area_acciones, bg=COLOR_CARD)
    g1.pack(fill="x", pady=(0, 10))
    _boton_accento(g1, "1  Registrar envio (Create)", crear).pack(side="left")
    _boton_secundario(g1, "2  Ver manifiesto (Read)", leer).pack(side="left", padx=(10, 0))

    g2 = tk.Frame(area_acciones, bg=COLOR_CARD)
    g2.pack(fill="x", pady=(0, 10))
    _boton_secundario(g2, "3  Actualizar registro (Update)", actualizar).pack(side="left")
    _boton_secundario(g2, "4  Eliminar registro (Delete)", eliminar).pack(side="left", padx=(10, 0))

    g3 = tk.Frame(area_acciones, bg=COLOR_CARD)
    g3.pack(fill="x")

    tk.Button(
        g3,
        text=" 5 Abrir Power BI Desktop (RutaOptima.pbix) ",
        command=abrir_power_bi,
        bg=COLOR_NAVY,
        fg="#FFFFFF",
        font=("Segoe UI", 11, "bold"),
        activebackground=COLOR_NAVY_MID,
        activeforeground="#FFFFFF",
        relief="flat",
        padx=16,
        pady=11,
        cursor="hand2",
    ).pack(anchor="w")

    tk.Frame(contenido, height=14, bg=COLOR_BG_PAGE).pack()

    tk.Button(
        contenido,
        text=" Actualizar artefactos para Power BI (CSV + rutas texto) ",
        command=refrescar_bi,
        bg="#FFFFFF",
        fg=COLOR_NAVY,
        font=("Segoe UI", 10),
        relief="solid",
        borderwidth=1,
        highlightbackground=COLOR_NAVY,
        padx=12,
        pady=9,
        cursor="hand2",
    ).pack(anchor="w")

    root.mainloop()
