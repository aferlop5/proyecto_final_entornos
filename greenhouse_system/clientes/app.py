"""Punto de entrada para ejecutar el dashboard web de invernadero."""
from __future__ import annotations

import sys
from pathlib import Path

import dash


def _asegurar_ruta_paquete() -> None:
    """Garantiza que el paquete ``greenhouse_system`` sea importable.

    Esto permite ejecutar el archivo tanto con ``python -m clientes.app`` como
    directamente con ``python clientes/app.py``.
    """

    paquete_ya_disponible = "greenhouse_system" in sys.modules
    if paquete_ya_disponible:
        return

    try:
        import greenhouse_system  # type: ignore # noqa:F401 (comprobación rápida)
        return
    except ModuleNotFoundError:
        raiz_proyecto = Path(__file__).resolve().parents[2]
        ruta_raiz = str(raiz_proyecto)
        if ruta_raiz not in sys.path:
            sys.path.insert(0, ruta_raiz)


_asegurar_ruta_paquete()

from greenhouse_system.dashboard.layout import create_layout  # noqa:E402
from greenhouse_system.dashboard.callbacks import register_callbacks  # noqa:E402


_assets_path = Path(__file__).resolve().parent.parent / "dashboard" / "assets"

app = dash.Dash(
    __name__,
    title="Greenhouse Dashboard",
    suppress_callback_exceptions=True,
    assets_folder=str(_assets_path),  # Cargar CSS desde dashboard/assets
)
app.layout = create_layout()
register_callbacks(app)

# Exponer el servidor Flask para despliegues en producción.
server = app.server


if __name__ == "__main__":
    # app.run(debug=True)  # Descomenta esta línea para desarrollo (muestra DevTools)
    app.run(debug=False) # Usa esta línea para producción (oculta DevTools)
