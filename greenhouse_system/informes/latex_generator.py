"""Generador de informes LaTeX basado en los datos almacenados en MySQL."""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
from typing import Dict, Iterable, List, Sequence, Tuple

from middleware.database_handler import conectar


class ReportGenerator:
    """Crea informes diarios en LaTeX a partir de las últimas 24 horas de datos."""

    def __init__(
        self,
        output_dir: Path | None = None,
        template_path: Path | None = None,
    ) -> None:
        base_dir = Path(__file__).resolve().parent
        self.output_dir = Path(output_dir) if output_dir else base_dir
        self.template_path = Path(template_path) if template_path else base_dir / "plantilla_informe.tex"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_daily_report(
        self,
        output_filename: str | None = None,
        *,
        compile_pdf: bool = False,
    ) -> Dict[str, Path]:
        """Genera el informe del último día y, opcionalmente, compila el PDF.

        Args:
            output_filename: Nombre base o nombre de archivo para el informe. Puede incluir
                o no la extensión ".tex". Si no se indica, se usará un nombre con fecha.
            compile_pdf: Cuando es True, se ejecuta ``pdflatex`` para generar el PDF.

        Returns:
            Diccionario con las rutas del informe LaTeX y, si se solicita, del PDF.
        """

        since = datetime.now() - timedelta(hours=24)
        clima = self._fetch_data(
            "SELECT zona, temperatura, humedad, co2, intensidad_luz, presion FROM clima_data WHERE timestamp >= %s",
            (since,),
        )
        riego = self._fetch_data(
            "SELECT ph, conductividad, flujo, nivel_deposito, caudal_historico FROM riego_data WHERE timestamp >= %s",
            (since,),
        )
        plantas = self._fetch_data(
            "SELECT especie, crecimiento, cantidad_frutos, calidad_frutos, nivel_salud FROM plantas_data WHERE timestamp >= %s",
            (since,),
        )
        alertas = self._fetch_data(
            "SELECT zona, especie, tipo_alerta FROM alertas_criticas WHERE timestamp >= %s",
            (since,),
        )

        tablas = self.create_sensor_tables(
            {
                "clima": clima,
                "riego": riego,
                "plantas": plantas,
            }
        )
        resumen_alertas = self.create_alert_summary(alertas)

        base_name = self._resolve_basename(output_filename)
        tex_path = self.output_dir / f"{base_name}.tex"

        template_text = self.template_path.read_text(encoding="utf-8")
        template_text = template_text.replace("<!-- TABLAS AUTOMÁTICAS AQUÍ -->", tablas)
        template_text = template_text.replace("<!-- RESUMEN DE ALERTAS AQUÍ -->", resumen_alertas)

        tex_path.write_text(template_text, encoding="utf-8")

        paths = {"tex": tex_path}
        if compile_pdf:
            pdf_path = self._compile_pdf(tex_path)
            paths["pdf"] = pdf_path
        return paths

    def create_sensor_tables(self, data: Dict[str, Sequence[Dict[str, float]]]) -> str:
        """Devuelve las tablas LaTeX para las métricas de clima, riego y plantas."""
        secciones: List[str] = []

        clima = data.get("clima", [])
        if clima:
            campos = (
                ("temperatura", "Temperatura (°C)"),
                ("humedad", "Humedad (%)"),
                ("co2", "CO$_2$ (ppm)"),
                ("intensidad_luz", "Intensidad de luz"),
                ("presion", "Presión (hPa)"),
            )
            secciones.append(self._build_stats_table("Resumen de clima", clima, campos))

        riego = data.get("riego", [])
        if riego:
            campos = (
                ("ph", "pH"),
                ("conductividad", "Conductividad (mS/cm)"),
                ("flujo", "Flujo (L/min)"),
                ("nivel_deposito", "Nivel depósito (%)"),
                ("caudal_historico", "Caudal histórico"),
            )
            secciones.append(self._build_stats_table("Resumen de riego", riego, campos))

        plantas = data.get("plantas", [])
        if plantas:
            campos = (
                ("crecimiento", "Crecimiento"),
                ("cantidad_frutos", "Cantidad de frutos"),
                ("calidad_frutos", "Calidad de frutos"),
                ("nivel_salud", "Nivel de salud"),
            )
            secciones.append(self._build_stats_table("Resumen de plantas", plantas, campos))

        if not secciones:
            return "No hay datos disponibles en las últimas 24 horas."
        return "\n\n".join(secciones)

    def create_alert_summary(self, alertas: Sequence[Dict[str, str]]) -> str:
        """Crea un resumen tabular de las alertas críticas registradas."""
        if not alertas:
            return "No se registraron alertas críticas en las últimas 24 horas."

        conteo: Dict[Tuple[str, str, str], int] = defaultdict(int)
        for alerta in alertas:
            clave = (
                alerta.get("zona") or "N/D",
                alerta.get("especie") or "N/D",
                alerta.get("tipo_alerta") or "N/D",
            )
            conteo[clave] += 1

        filas = [
            f"{self._escape_tex(zona)} & {self._escape_tex(especie)} & {self._escape_tex(tipo)} & {cantidad} \\\\"
            for (zona, especie, tipo), cantidad in sorted(conteo.items())
        ]

        tabla = [
            "\\begin{table}[h!]",
            "\\centering",
            "\\caption{Resumen de alertas críticas}",
            "\\begin{tabular}{l l l c}",
            "\\toprule",
            "Zona & Especie & Alerta & Eventos \\",
            "\\midrule",
            *filas,
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
        ]
        return "\n".join(tabla)

    def _fetch_data(self, query: str, params: Tuple[object, ...]) -> List[Dict[str, object]]:
        cnx = conectar()
        try:
            cursor = cnx.cursor(dictionary=True)
            cursor.execute(query, params)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        finally:
            cnx.close()

    def _build_stats_table(
        self,
        titulo: str,
        registros: Sequence[Dict[str, object]],
        campos: Iterable[Tuple[str, str]],
    ) -> str:
        filas = []
        for campo, etiqueta in campos:
            valores = [row[campo] for row in registros if row.get(campo) is not None]
            if not valores:
                continue
            promedio = sum(valores) / len(valores)
            minimo = min(valores)
            maximo = max(valores)
            filas.append(
                f"{self._escape_tex(etiqueta)} & {self._format_valor(promedio)} & {self._format_valor(minimo)} & {self._format_valor(maximo)} \\\\"
            )

        if not filas:
            return f"No se encontraron valores para {titulo.lower()}."

        tabla = [
            "\\begin{table}[h!]",
            "\\centering",
            f"\\caption{{{self._escape_tex(titulo)}}}",
            "\\begin{tabular}{l c c c}",
            "\\toprule",
            "Métrica & Promedio & Mínimo & Máximo \\",
            "\\midrule",
            *filas,
            "\\bottomrule",
            "\\end{tabular}",
            "\\end{table}",
        ]
        return "\n".join(tabla)

    @staticmethod
    def _format_valor(valor: object) -> str:
        if isinstance(valor, (int, float)):
            return f"{valor:.2f}" if isinstance(valor, float) else str(valor)
        return "-"

    @staticmethod
    def _escape_tex(texto: str) -> str:
        reemplazos = {
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
            "\\": r"\textbackslash{}",
        }
        for caracter, escape in reemplazos.items():
            texto = texto.replace(caracter, escape)
        return texto

    @staticmethod
    def _resolve_basename(output_filename: str | None) -> str:
        if not output_filename:
            return f"informe_{datetime.now().strftime('%Y%m%d_%H%M')}"
        filename = Path(output_filename)
        return filename.stem if filename.suffix else str(filename)

    @staticmethod
    def _compile_pdf(tex_path: Path) -> Path:
        try:
            subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", tex_path.name],
                cwd=tex_path.parent,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                "pdflatex no está instalado o no se encuentra en el PATH."
            ) from exc
        except subprocess.CalledProcessError as exc:
            log_path = tex_path.with_suffix(".log")
            raise RuntimeError(
                f"Error al compilar LaTeX. Revisa el log {log_path.name}."
            ) from exc
        return tex_path.with_suffix(".pdf")