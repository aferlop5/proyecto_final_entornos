"""Dash layout for the greenhouse realtime dashboard."""
from dash import dcc, html


def create_layout() -> html.Div:
    return html.Div(
        [
            dcc.Location(id="app-url"),
            dcc.Interval(id="interval-component", interval=2_000, n_intervals=0),
            html.Header(
                [
                    html.H1("Invernadero Inteligente - Monitorización OPC UA"),
                    html.P(
                        "Panel en tiempo real para supervisar clima, riego y estado de las plantas.",
                        className="subtitle",
                    ),
                ],
                className="page-header",
            ),
            html.Div(id="kpi-container", className="kpi-section"),
            html.Div(
                [
                    html.Div(
                        [
                            html.H2("Clima"),
                            html.P("Zona", className="section-label"),
                            html.Div(id="clima-zone", className="zone-badge"),
                            html.Div(id="clima-data", className="sensor-content"),
                        ],
                        className="sensor-column clima-column",
                    ),
                    html.Div(
                        [
                            html.H2("Riego"),
                            html.Div(id="riego-data", className="sensor-content"),
                        ],
                        className="sensor-column riego-column",
                    ),
                    html.Div(
                        [
                            html.H2("Plantas"),
                            html.Div(id="plantas-data", className="sensor-content"),
                        ],
                        className="sensor-column plantas-column",
                    ),
                ],
                className="sensor-grid",
            ),
            html.Section(
                [
                    html.H2("Alertas"),
                    html.Div(
                        [
                            html.Div(
                                [
                                    html.H3("Zona A"),
                                    html.Div(id="alert-zone-a", className="alert-section"),
                                ],
                                className="alert-column zone-a-column",
                            ),
                            html.Div(
                                [
                                    html.H3("Zona B"),
                                    html.Div(id="alert-zone-b", className="alert-section"),
                                ],
                                className="alert-column zone-b-column",
                            ),
                        ],
                        className="alert-columns",
                    ),
                ],
                className="alerts-section",
            ),
            html.Section(
                [
                    html.H2("Evolución histórica"),
                    dcc.Graph(id="historical-charts", config={"displayModeBar": False}),
                ],
                className="history-section",
            ),
            html.Section(
                [
                    html.H2("Informes"),
                    html.Button(
                        "Generar informe diario",
                        id="btn-generar-informe",
                        className="report-button",
                        n_clicks=0,
                    ),
                    html.Div(id="report-status", className="report-status"),
                    dcc.Download(id="download-informe"),
                ],
                className="report-section",
            ),
        ],
        className="app-container",
    )