"""Entrada obsoleta del dashboard.

El dashboard se ejecuta ahora desde ``greenhouse_system/clientes/app.py``.
Este archivo solo persiste para mostrar un mensaje claro en caso de usos
antiguos (``python -m dashboard.app``)."""
from __future__ import annotations

raise RuntimeError(
    "El dashboard se ha movido al paquete 'clientes'. Ejecuta 'python3 clientes/app.py' "
    "(o 'python3 -m clientes.app') desde la raíz de greenhouse_system."
)
