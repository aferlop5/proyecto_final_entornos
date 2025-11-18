"""Punto de entrada para ejecutar el dashboard web de invernadero."""
from __future__ import annotations

import dash

from greenhouse_system.dashboard.layout import create_layout
from greenhouse_system.dashboard.callbacks import register_callbacks


app = dash.Dash(
    __name__,
    title="Greenhouse Dashboard",
    suppress_callback_exceptions=True,
)
app.layout = create_layout()
register_callbacks(app)

# Exponer el servidor Flask para despliegues en producción.
server = app.server


if __name__ == "__main__":
    app.run(debug=True)
