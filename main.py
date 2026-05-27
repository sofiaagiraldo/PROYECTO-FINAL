"""Orquestador principal: garantiza modelo estrella + exportaciones BI + GUI Tkinter."""

from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    raiz = Path(__file__).resolve().parent
    if str(raiz) not in sys.path:
        sys.path.insert(0, str(raiz))

    from Backend.bootstrap import preparar_ecosistema_star_y_bi
    from Frontend.ventana_principal import lanzar_gui

    gestor, repo = preparar_ecosistema_star_y_bi(raiz / "Frontend")
    lanzar_gui(raiz, gestor, repo)


if __name__ == "__main__":
    main()
