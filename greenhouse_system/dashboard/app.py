"""Entry point for running the Dash dashboard."""
from __future__ import annotations

import dash

from .layout import create_layout
from .callbacks import register_callbacks


app = dash.Dash(__name__, title="Greenhouse Dashboard", suppress_callback_exceptions=True)
app.layout = create_layout()
register_callbacks(app)

# Expose Flask server for production deployments (gunicorn, etc.)
server = app.server


if __name__ == "__main__":
    app.run(debug=True)
