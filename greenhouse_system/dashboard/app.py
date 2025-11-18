"""Compatibilidad retroactiva para el dashboard.

El dashboard se encuentra ahora en ``greenhouse_system.clientes.app``.
Este módulo reexpone los objetos principales para evitar importaciones rotas.
"""
from __future__ import annotations

from greenhouse_system.clientes.app import app, server


if __name__ == "__main__":
    app.run(debug=True)
