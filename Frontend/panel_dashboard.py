"""Panel de dashboard en Tkinter (KPIs + 4 graficas con Canvas)."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Any

from Backend.metricas_dashboard import paquete_dashboard

COLOR_NAVY = "#1B2D4A"
COLOR_ORANGE = "#E85D21"
COLOR_CARD = "#FFFFFF"
COLOR_MUTED = "#5C6F82"
COLOR_BG = "#EEF2F8"
PALETA_BARRAS = ("#E85D21", "#243B63", "#5C8FD6", "#2E9B6A", "#9B59B6", "#C94A14")


def _acortar(texto: str, max_len: int = 14) -> str:
    t = texto.strip()
    if len(t) <= max_len:
        return t
    return t[: max_len - 1] + "…"


def _dibujar_barras_horizontales(
    canvas: tk.Canvas,
    series: list[tuple[str, float]],
    titulo: str,
    unidad: str,
) -> None:
    canvas.delete("all")
    w = int(canvas.winfo_width() or 420)
    h = int(canvas.winfo_height() or 200)
    if w < 80:
        w = 420
    if h < 80:
        h = 200

    canvas.create_rectangle(0, 0, w, h, fill=COLOR_CARD, outline=COLOR_NAVY, width=1)
    canvas.create_text(12, 10, anchor="nw", text=titulo, fill=COLOR_NAVY, font=("Segoe UI", 10, "bold"))

    if not series:
        canvas.create_text(w // 2, h // 2, text="Sin datos", fill=COLOR_MUTED, font=("Segoe UI", 10))
        return

    max_v = max(v for _, v in series) or 1.0
    margen_izq = 118
    margen_der = 24
    margen_sup = 34
    margen_inf = 16
    alto_barra = max(14, (h - margen_sup - margen_inf) // max(len(series), 1) - 6)
    ancho_max = w - margen_izq - margen_der

    for i, (etiqueta, valor) in enumerate(series):
        y = margen_sup + i * (alto_barra + 6)
        ancho = int(ancho_max * (valor / max_v))
        color = PALETA_BARRAS[i % len(PALETA_BARRAS)]
        canvas.create_text(
            margen_izq - 8,
            y + alto_barra // 2,
            text=_acortar(etiqueta, 16),
            anchor="e",
            fill=COLOR_MUTED,
            font=("Segoe UI", 9),
        )
        canvas.create_rectangle(margen_izq, y, margen_izq + ancho, y + alto_barra, fill=color, outline="")
        texto_val = f"{valor:,.1f}" if isinstance(valor, float) and valor % 1 else f"{int(valor):,}"
        canvas.create_text(
            margen_izq + ancho + 6,
            y + alto_barra // 2,
            text=f"{texto_val} {unidad}".strip(),
            anchor="w",
            fill=COLOR_NAVY,
            font=("Segoe UI", 9),
        )


def _dibujar_linea(canvas: tk.Canvas, series: list[tuple[str, float]], titulo: str) -> None:
    canvas.delete("all")
    w = int(canvas.winfo_width() or 420)
    h = int(canvas.winfo_height() or 200)
    if w < 80:
        w = 420
    if h < 80:
        h = 200

    canvas.create_rectangle(0, 0, w, h, fill=COLOR_CARD, outline=COLOR_NAVY, width=1)
    canvas.create_text(12, 10, anchor="nw", text=titulo, fill=COLOR_NAVY, font=("Segoe UI", 10, "bold"))

    if not series:
        canvas.create_text(w // 2, h // 2, text="Sin datos", fill=COLOR_MUTED, font=("Segoe UI", 10))
        return

    valores = [v for _, v in series]
    min_v = min(valores)
    max_v = max(valores)
    rango = max(max_v - min_v, 1.0)

    pad_x, pad_y = 48, 42
    plot_w, plot_h = w - pad_x * 2, h - pad_y - 28
    puntos: list[tuple[float, float]] = []
    n = len(series)
    for i, (_, valor) in enumerate(series):
        x = pad_x + (plot_w * i / max(n - 1, 1))
        y = pad_y + plot_h * (1 - (valor - min_v) / rango)
        puntos.append((x, y))

    if len(puntos) > 1:
        canvas.create_line(puntos, fill=COLOR_ORANGE, width=2, smooth=True)
    for (x, y), (etq, val) in zip(puntos, series):
        canvas.create_oval(x - 4, y - 4, x + 4, y + 4, fill=COLOR_NAVY, outline="")
        canvas.create_text(x, h - 14, text=_acortar(etq, 10), fill=COLOR_MUTED, font=("Segoe UI", 8))
        canvas.create_text(x, y - 10, text=f"{val:,.0f}", fill=COLOR_NAVY, font=("Segoe UI", 8))


def _dibujar_scatter(canvas: tk.Canvas, puntos: list[dict[str, Any]], titulo: str) -> None:
    canvas.delete("all")
    w = int(canvas.winfo_width() or 420)
    h = int(canvas.winfo_height() or 200)
    if w < 80:
        w = 420
    if h < 80:
        h = 200

    canvas.create_rectangle(0, 0, w, h, fill=COLOR_CARD, outline=COLOR_NAVY, width=1)
    canvas.create_text(12, 10, anchor="nw", text=titulo, fill=COLOR_NAVY, font=("Segoe UI", 10, "bold"))

    if not puntos:
        canvas.create_text(w // 2, h // 2, text="Sin datos", fill=COLOR_MUTED, font=("Segoe UI", 10))
        return

    pesos = [p["peso"] for p in puntos]
    kms = [p["kms"] for p in puntos]
    min_p, max_p = min(pesos), max(pesos)
    min_k, max_k = min(kms), max(kms)
    r_p = max(max_p - min_p, 0.001)
    r_k = max(max_k - min_k, 0.001)

    pad_l, pad_r, pad_t, pad_b = 52, 18, 36, 36
    plot_w, plot_h = w - pad_l - pad_r, h - pad_t - pad_b

    canvas.create_text(14, pad_t + plot_h // 2, text="km", fill=COLOR_MUTED, font=("Segoe UI", 8))
    canvas.create_text(pad_l + plot_w // 2, h - 10, text="kg", fill=COLOR_MUTED, font=("Segoe UI", 8))

    for i, p in enumerate(puntos):
        x = pad_l + plot_w * (p["peso"] - min_p) / r_p
        y = pad_t + plot_h * (1 - (p["kms"] - min_k) / r_k)
        color = PALETA_BARRAS[i % len(PALETA_BARRAS)]
        canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=color, outline=COLOR_NAVY, width=1)


class PanelDashboard(ttk.Frame):
    def __init__(self, master: tk.Misc, gestor, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self._gestor = gestor

        encabezado = ttk.Label(
            self,
            text="Dashboard analitico (modelo estrella)",
            style="AppHeader.TLabel",
        )
        encabezado.pack(anchor="w")

        self._fila_kpi = tk.Frame(self, bg=COLOR_BG)
        self._fila_kpi.pack(fill="x", pady=(10, 14))

        self._tarjetas_kpi: list[tk.Frame] = []
        titulos_kpi = (
            "Envios",
            "Costo total (COP)",
            "Peso promedio (kg)",
            "Kilometros",
        )
        for titulo in titulos_kpi:
            marco = tk.Frame(
                self._fila_kpi,
                bg=COLOR_CARD,
                highlightbackground=COLOR_NAVY,
                highlightthickness=1,
                padx=14,
                pady=12,
            )
            marco.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(marco, text=titulo, bg=COLOR_CARD, fg=COLOR_MUTED, font=("Segoe UI", 9)).pack(anchor="w")
            valor_lbl = tk.Label(
                marco,
                text="—",
                bg=COLOR_CARD,
                fg=COLOR_NAVY,
                font=("Segoe UI", 16, "bold"),
            )
            valor_lbl.pack(anchor="w", pady=(6, 0))
            marco._valor_label = valor_lbl  # type: ignore[attr-defined]
            self._tarjetas_kpi.append(marco)

        rejilla = tk.Frame(self, bg=COLOR_BG)
        rejilla.pack(fill="both", expand=True)

        self._cv_peso_clase = tk.Canvas(rejilla, width=440, height=210, bg=COLOR_CARD, highlightthickness=0)
        self._cv_costo_fecha = tk.Canvas(rejilla, width=440, height=210, bg=COLOR_CARD, highlightthickness=0)
        self._cv_zona = tk.Canvas(rejilla, width=440, height=210, bg=COLOR_CARD, highlightthickness=0)
        self._cv_scatter = tk.Canvas(rejilla, width=440, height=210, bg=COLOR_CARD, highlightthickness=0)

        self._cv_peso_clase.grid(row=0, column=0, padx=(0, 10), pady=(0, 10), sticky="nsew")
        self._cv_costo_fecha.grid(row=0, column=1, padx=0, pady=(0, 10), sticky="nsew")
        self._cv_zona.grid(row=1, column=0, padx=(0, 10), pady=0, sticky="nsew")
        self._cv_scatter.grid(row=1, column=1, padx=0, pady=0, sticky="nsew")
        rejilla.columnconfigure(0, weight=1)
        rejilla.columnconfigure(1, weight=1)
        rejilla.rowconfigure(0, weight=1)
        rejilla.rowconfigure(1, weight=1)

        self.bind("<Configure>", self._on_resize)

    def _on_resize(self, _event=None) -> None:
        if getattr(self, "_datos_cache", None):
            self._pintar(self._datos_cache)

    def refrescar(self) -> None:
        self._datos_cache = paquete_dashboard(self._gestor)
        self._pintar(self._datos_cache)

    def _pintar(self, datos: dict[str, Any]) -> None:
        k = datos["kpis"]
        valores = (
            str(k["total_envios"]),
            f"{k['costo_total_cop']:,}".replace(",", "."),
            f"{k['peso_promedio_kg']:.2f}",
            f"{k['kms_totales']:.1f}",
        )
        for marco, texto in zip(self._tarjetas_kpi, valores):
            marco._valor_label.config(text=texto)  # type: ignore[attr-defined]

        _dibujar_barras_horizontales(
            self._cv_peso_clase,
            datos["peso_clase"],
            "1. Peso total por clase de servicio",
            "kg",
        )
        _dibujar_linea(
            self._cv_costo_fecha,
            datos["costo_fecha"],
            "2. Costo medio COP por fecha",
        )
        _dibujar_barras_horizontales(
            self._cv_zona,
            [(e, v) for e, v in datos["envios_zona"]],
            "3. Envios por localidad",
            "uds",
        )
        _dibujar_scatter(
            self._cv_scatter,
            datos["scatter"],
            "4. Kilometros vs peso (por envio)",
        )
