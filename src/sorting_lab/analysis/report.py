"""Simple HTML report generation."""

from __future__ import annotations

from pathlib import Path
import pandas as pd


def generate_report(results_path: str, output_path: str) -> None:
    """Create a lightweight HTML report from a CSV results file."""
    df = pd.read_csv(results_path)
    summary_fields = {"avg_time_s": "mean", "memory_mb": "mean"}
    if "memory_peak_mb" in df.columns:
        summary_fields["memory_peak_mb"] = "mean"
    summary = df.groupby("algorithm").agg(summary_fields).reset_index()

    html = f"""
    <html>
    <head><title>Sorting Lab Report</title></head>
    <body>
    <h1>Sorting Lab Raporu</h1>
    <p>Kaynak: {results_path}</p>
    <h2>Ham Sonuçlar</h2>
    {df.to_html(index=False)}
    <h2>Özet</h2>
    {summary.to_html(index=False)}
    </body>
    </html>
    """
    out_path = Path(output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")
    print(f"HTML raporu yazıldı: {out_path}")
