"""Dash callbacks powering the greenhouse dashboard."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from dash import Dash, Input, Output, dcc, html
import plotly.graph_objects as go

from .data_fetcher import DataFetcher


def _safe_float(value: Optional[Any]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_time(value: Optional[Any]) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    try:
        return datetime.fromisoformat(str(value))
    except ValueError:
        return None


def _build_indicator(title: str, value: Optional[float], min_val: float, max_val: float, unit: str = ""):
    if value is None:
        return html.Div([html.H4(title), html.P("Sin datos", className="no-data")], className="indicator-card")

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            number={"suffix": unit},
            title={"text": title},
            gauge={
                "axis": {"range": [min_val, max_val]},
                "bar": {"color": "#2a9d8f"},
                "bgcolor": "#f6f6f6",
            },
        )
    )
    fig.update_layout(margin=dict(l=10, r=10, t=40, b=10), height=220)
    return dcc.Graph(figure=fig, className="indicator-graph", config={"displayModeBar": False})


def _build_line_chart(rows: List[Dict[str, Any]], metrics: List[str], labels: List[str], colors: List[str], title: str):
    fig = go.Figure()
    rows_sorted = list(reversed(rows))
    timestamps = [_parse_time(row.get("timestamp")) for row in rows_sorted]

    for metric, label, color in zip(metrics, labels, colors):
        values = [_safe_float(row.get(metric)) for row in rows_sorted]
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=values,
                name=label,
                mode="lines+markers",
                line=dict(color=color, width=2),
            )
        )

    fig.update_layout(
        title=title,
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", y=-0.2),
        height=300,
        xaxis_title="Tiempo",
    )
    return dcc.Graph(figure=fig, className="line-chart", config={"displayModeBar": False})


def _build_progress(label: str, value: Optional[float], max_value: float, unit: str = ""):
    if value is None:
        return html.Div([html.P(label), html.P("Sin datos", className="no-data")], className="progress-card")
    percentage = max(0.0, min(100.0, (value / max_value) * 100 if max_value else 0.0))
    return html.Div(
        [
            html.P(f"{label}: {value:.1f}{unit}", className="progress-label"),
            html.Div(
                [
                    html.Div(style={"width": f"{percentage:.1f}%"}, className="progress-bar-fill"),
                ],
                className="progress-bar",
            ),
        ],
        className="progress-card",
    )


def _alert_color(tipo_alerta: str) -> str:
    alert = (tipo_alerta or "").lower()
    if "crit" in alert or "temperatura" in alert:
        return "alert-critical"
    if "riego" in alert or "ph" in alert:
        return "alert-warning"
    return "alert-info"


def _build_alerts(alerts: List[Dict[str, Any]]):
    if not alerts:
        return html.Div("Sin alertas activas", className="alert-card alert-ok")

    return [
        html.Div(
            [
                html.H4(alert.get("tipo_alerta", "Alerta")),
                html.P(f"Zona: {alert.get('zona', 'N/D')}", className="alert-meta"),
                html.P(f"Especie: {alert.get('especie', 'N/D')}", className="alert-meta"),
                html.P(_parse_time(alert.get("timestamp")).strftime("%d/%m %H:%M") if _parse_time(alert.get("timestamp")) else ""),
            ],
            className=f"alert-card {_alert_color(alert.get('tipo_alerta', ''))}",
        )
        for alert in alerts
    ]


def _build_kpis(latest: Dict[str, Optional[Dict[str, Any]]], processed: List[Dict[str, Any]]):
    clima = latest.get("clima") or {}
    riego = latest.get("riego") or {}
    plantas = latest.get("plantas") or {}
    procesado = processed[0] if processed else {}

    temperatura = _safe_float(clima.get("temperatura"))
    ph = _safe_float(riego.get("ph"))
    salud = _safe_float(plantas.get("nivel_salud"))
    estres = _safe_float(procesado.get("indice_estres"))

    cards = [
        html.Div(
            [html.H3("Temperatura"), html.P(f"{temperatura:.1f} °C" if temperatura is not None else "Sin datos")],
            className="kpi-card",
        ),
        html.Div(
            [html.H3("pH Riego"), html.P(f"{ph:.2f}" if ph is not None else "Sin datos")],
            className="kpi-card",
        ),
        html.Div(
            [html.H3("Salud Plantas"), html.P(f"{salud:.1f}%" if salud is not None else "Sin datos")],
            className="kpi-card",
        ),
        html.Div(
            [html.H3("Índice Estrés"), html.P(f"{estres:.2f}" if estres is not None else "Sin datos")],
            className="kpi-card",
        ),
    ]
    return cards


def _build_historical(processed: List[Dict[str, Any]]) -> go.Figure:
    figure = go.Figure()
    if not processed:
        figure.update_layout(title="Sin datos históricos", height=320)
        return figure

    rows = list(reversed(processed))
    timestamps = [_parse_time(row.get("timestamp")) for row in rows]

    estres = [_safe_float(row.get("indice_estres")) for row in rows]
    eficiencia = [_safe_float(row.get("eficiencia_luz")) for row in rows]
    rendimiento = [_safe_float(row.get("rendimiento_frutos")) for row in rows]
    necesidad_riego = [1 if row.get("necesidad_riego") else 0 for row in rows]

    figure.add_trace(
        go.Scatter(x=timestamps, y=estres, name="Índice estrés", mode="lines+markers", line=dict(color="#e76f51"))
    )
    figure.add_trace(
        go.Scatter(x=timestamps, y=eficiencia, name="Eficiencia luz", mode="lines+markers", line=dict(color="#2a9d8f"))
    )
    figure.add_trace(
        go.Bar(
            x=timestamps,
            y=rendimiento,
            name="Rendimiento frutos",
            marker_color="#264653",
            opacity=0.6,
            yaxis="y2",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=timestamps,
            y=necesidad_riego,
            name="Necesidad riego",
            mode="lines",
            line=dict(color="#f4a261", dash="dash"),
            yaxis="y3",
        )
    )

    figure.update_layout(
        title="Indicadores procesados",
        height=360,
        margin=dict(l=20, r=40, t=50, b=40),
        legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="Índices", range=[0, 1.05]),
        yaxis2=dict(title="Frutos", overlaying="y", side="right"),
        yaxis3=dict(title="Necesidad riego", overlaying="y", side="right", position=0.98, range=[0, 1.05]),
        xaxis_title="Tiempo",
    )
    return figure


def register_callbacks(app: Dash) -> None:
    fetcher = DataFetcher()

    @app.callback(
        [
            Output("clima-data", "children"),
            Output("riego-data", "children"),
            Output("plantas-data", "children"),
            Output("alert-panel", "children"),
            Output("kpi-container", "children"),
            Output("clima-zone", "children"),
            Output("historical-charts", "figure"),
        ],
        Input("interval-component", "n_intervals"),
    )
    def update_dashboard(_):
        latest = fetcher.get_latest_sensor_data()
        processed = fetcher.get_processed_data(limit=50)
        alerts = fetcher.get_active_alerts()
        clima_history = fetcher.get_recent_data("clima_data")
        riego_history = fetcher.get_recent_data("riego_data")
        plantas_history = fetcher.get_recent_data("plantas_data")

        clima_latest = latest.get("clima") or {}
        riego_latest = latest.get("riego") or {}
        plantas_latest = latest.get("plantas") or {}

        clima_children = [
            _build_indicator("Temperatura", _safe_float(clima_latest.get("temperatura")), 0, 40, " °C"),
            _build_line_chart(
                clima_history,
                ["humedad", "co2", "presion"],
                ["Humedad (%)", "CO₂ (ppm)", "Presión (hPa)"],
                ["#1d3557", "#457b9d", "#a8dadc"],
                "Clima ambiente",
            ),
        ]

        flujo = _safe_float(riego_latest.get("flujo"))
        caudal = _safe_float(riego_latest.get("caudal_historico"))
        nivel = _safe_float(riego_latest.get("nivel_deposito"))

        riego_children = [
            _build_indicator("pH", _safe_float(riego_latest.get("ph")), 0, 14),
            _build_indicator("Conductividad (mS/cm)", _safe_float(riego_latest.get("conductividad")), 0, 3),
            _build_progress("Nivel depósito", nivel, 100, "%"),
            _build_line_chart(
                riego_history,
                ["flujo", "caudal_historico"],
                ["Flujo", "Caudal histórico"],
                ["#2a9d8f", "#264653"],
                "Dinámica de riego",
            ),
            html.Div(
                [
                    html.P(f"Flujo actual: {flujo:.2f} L/min" if flujo is not None else "Flujo actual: N/D"),
                    html.P(
                        f"Caudal acumulado: {caudal:.2f} L" if caudal is not None else "Caudal acumulado: N/D"
                    ),
                ],
                className="riego-stats",
            ),
        ]

        crecimiento = _safe_float(plantas_latest.get("crecimiento"))
        nivel_salud = _safe_float(plantas_latest.get("nivel_salud"))
        cantidad_frutos = plantas_latest.get("cantidad_frutos")
        calidad_frutos = _safe_float(plantas_latest.get("calidad_frutos"))

        plantas_children = [
            _build_progress("Crecimiento", crecimiento, 15, " cm"),
            _build_progress("Nivel salud", nivel_salud, 100, "%"),
            html.Div(
                [
                    html.P(
                        f"Cantidad frutos: {cantidad_frutos}" if cantidad_frutos is not None else "Cantidad frutos: N/D"
                    ),
                    html.P(
                        f"Calidad frutos: {calidad_frutos:.1f}%" if calidad_frutos is not None else "Calidad frutos: N/D"
                    ),
                    html.P(f"Especie: {plantas_latest.get('especie', 'N/D')}", className="especie-label"),
                ],
                className="plantas-summary",
            ),
        ]

        alert_children = _build_alerts(alerts)
        kpi_children = _build_kpis(latest, processed)
        zone_text = clima_latest.get("zona", "N/D")
        historical_figure = _build_historical(processed)

        return (
            clima_children,
            riego_children,
            plantas_children,
            alert_children,
            kpi_children,
            zone_text,
            historical_figure,
        )