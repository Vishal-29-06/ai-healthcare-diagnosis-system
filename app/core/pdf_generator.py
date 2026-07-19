"""
Generates a medical report PDF for a patient's record.

We build this to accept a plain dict of already-fetched data (rather
than raw SQLAlchemy objects) — this keeps the PDF-building logic
decoupled and independently testable from the database layer, and
matches the pattern we've used elsewhere (schemas/routers separated
from models).
"""

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# Matches the landing page's brand colors, so the PDF doesn't look
# like a disconnected generic template.
PRIMARY_TEAL = colors.HexColor("#123B36")
GOLD_ACCENT = colors.HexColor("#C9A15A")
LIGHT_BG = colors.HexColor("#FAF8F3")


def generate_medical_report_pdf(data: dict) -> BytesIO:
    """
    data expects these keys:
      patient_name, patient_email, doctor_name, doctor_specialization,
      appointment_date, diagnosis, notes,
      risk_label, risk_probability, top_factors (list of dicts),
      prescriptions (list of dicts)
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()

    # Custom styles matching our brand, on top of reportlab's defaults.
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"], textColor=PRIMARY_TEAL, fontSize=20
    )
    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=PRIMARY_TEAL,
        spaceBefore=14,
        spaceAfter=6,
    )
    normal = styles["Normal"]

    story = []

    # --- Header ---
    story.append(Paragraph("MediSense AI — Medical Report", title_style))
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(
            f"Generated for {data['patient_name']} · {data['appointment_date']}",
            normal,
        )
    )
    story.append(Spacer(1, 16))

    # --- Patient / Doctor info table ---
    info_table = Table(
        [
            ["Patient", data["patient_name"]],
            ["Email", data["patient_email"]],
            ["Doctor", f"{data['doctor_name']} ({data['doctor_specialization']})"],
            ["Appointment Date", data["appointment_date"]],
        ],
        colWidths=[1.7 * inch, 4.3 * inch],
    )
    info_table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (0, -1), PRIMARY_TEAL),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("LINEBELOW", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
            ]
        )
    )
    story.append(info_table)

    # --- Diagnosis & Notes ---
    story.append(Paragraph("Diagnosis & Notes", heading_style))
    story.append(Paragraph(f"<b>Diagnosis:</b> {data['diagnosis'] or 'N/A'}", normal))
    story.append(Spacer(1, 6))
    story.append(Paragraph(f"<b>Notes:</b> {data['notes'] or 'N/A'}", normal))

    # --- AI Risk Assessment ---
    if data.get("risk_label"):
        story.append(Paragraph("AI Risk Assessment", heading_style))
        story.append(
            Paragraph(
                f"<b>Risk Level:</b> {data['risk_label']} "
                f"({data['risk_probability']:.1%} probability)",
                normal,
            )
        )
        story.append(Spacer(1, 6))

        if data.get("top_factors"):
            factor_rows = [["Factor", "Direction", "Impact"]]
            for f in data["top_factors"]:
                factor_rows.append(
                    [f["feature"], f["direction"], f"{f['impact']:+.3f}"]
                )
            factor_table = Table(factor_rows, colWidths=[2.2 * inch, 2 * inch, 1.8 * inch])
            factor_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_TEAL),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, -1), 9),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(factor_table)

    # --- Prescriptions ---
    story.append(Paragraph("Prescriptions", heading_style))
    prescriptions = data.get("prescriptions") or []
    if prescriptions:
        rx_rows = [["Medicine", "Dosage", "Frequency", "Duration"]]
        for rx in prescriptions:
            rx_rows.append(
                [rx["medicine_name"], rx["dosage"] or "-", rx["frequency"] or "-", rx["duration"] or "-"]
            )
        rx_table = Table(rx_rows, colWidths=[1.8 * inch, 1.2 * inch, 1.6 * inch, 1.4 * inch])
        rx_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), GOLD_ACCENT),
                    ("TEXTCOLOR", (0, 0), (-1, 0), PRIMARY_TEAL),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(rx_table)
    else:
        story.append(Paragraph("No prescriptions on this record.", normal))

    # --- Footer disclaimer ---
    story.append(Spacer(1, 24))
    disclaimer_style = ParagraphStyle(
        "Disclaimer", parent=styles["Normal"], fontSize=8, textColor=colors.grey
    )
    story.append(
        Paragraph(
            "This report is generated by an AI-assisted system for informational "
            "purposes and does not replace professional medical judgment. "
            "Please consult your doctor for diagnosis and treatment decisions.",
            disclaimer_style,
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer
