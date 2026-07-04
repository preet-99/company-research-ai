from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT

def generate_pdf(company_name, ai_data, search_data=None, filename="report.pdf"):

    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=25*mm,
        leftMargin=25*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        textColor=colors.HexColor('#1a237e'),
        alignment=TA_CENTER,
        spaceAfter=6,
        spaceBefore=0,
        leading=28
    )

    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        fontName='Helvetica',
        fontSize=12,
        textColor=colors.HexColor('#5c6bc0'),
        alignment=TA_CENTER,
        spaceAfter=4,
        leading=16
    )

    section_style = ParagraphStyle(
        'SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=11,
        textColor=colors.white,
        backColor=colors.HexColor('#1a237e'),
        spaceBefore=16,
        spaceAfter=8,
        leading=18,
        leftIndent=0,
        borderPad=5
    )

    body_style = ParagraphStyle(
        'CustomBody',
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#212121'),
        leading=16,
        spaceAfter=6,
        spaceBefore=0
    )

    bullet_style = ParagraphStyle(
        'CustomBullet',
        fontName='Helvetica',
        fontSize=9.5,
        textColor=colors.HexColor('#212121'),
        leading=16,
        spaceAfter=5,
        spaceBefore=0,
        leftIndent=12,
        bulletIndent=0
    )

    story = []

    # ── Title Block ──────────────────────────────────────────
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("AI Company Research Report", title_style))
    story.append(Paragraph(company_name, subtitle_style))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor('#1a237e'),
        spaceAfter=6
    ))
    story.append(Spacer(1, 4*mm))

    # ── Company Info Table ───────────────────────────────────
    if search_data:
        story.append(Paragraph("  Company Information", section_style))
        story.append(Spacer(1, 2*mm))

        website = search_data.get('website', 'N/A')
        description = search_data.get('description', 'N/A')

        info_data = [
            ["Website", website],
            ["Overview", description],
        ]

        col_widths = [35*mm, 120*mm]
        info_table = Table(info_data, colWidths=col_widths, repeatRows=0)
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8eaf6')),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212121')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9fa8da')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('WORDWRAP', (0, 0), (-1, -1), True),
        ]))
        story.append(info_table)
        story.append(Spacer(1, 4*mm))

    # ── Summary ──────────────────────────────────────────────
    story.append(Paragraph("  Company Summary", section_style))
    story.append(Spacer(1, 2*mm))
    summary = ai_data.get('summary', 'N/A')
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 4*mm))

    # ── Products / Services ──────────────────────────────────
    story.append(Paragraph("  Products / Services", section_style))
    story.append(Spacer(1, 2*mm))
    products = ai_data.get('products', [])
    if products:
        # Show as 2-column table for clean look
        prod_rows = []
        for i in range(0, len(products), 2):
            left = f"• {products[i]}"
            right = f"• {products[i+1]}" if i+1 < len(products) else ""
            prod_rows.append([left, right])

        prod_table = Table(prod_rows, colWidths=[77*mm, 77*mm])
        prod_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9.5),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212121')),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1),
                [colors.HexColor('#f5f5f5'), colors.white]),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#e0e0e0')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(prod_table)
    story.append(Spacer(1, 4*mm))

    # ── Pain Points ──────────────────────────────────────────
    story.append(Paragraph("  AI-Generated Pain Points", section_style))
    story.append(Spacer(1, 2*mm))
    pain_points = ai_data.get('pain_points', [])
    for i, point in enumerate(pain_points, 1):
        story.append(Paragraph(f"{i}.  {point}", bullet_style))
    story.append(Spacer(1, 4*mm))

    # ── Competitors Table ─────────────────────────────────────
    story.append(Paragraph("  Competitor Analysis", section_style))
    story.append(Spacer(1, 2*mm))
    competitors = ai_data.get('competitors', [])

    if competitors:
        comp_data = [["#", "Company Name", "Website"]]
        for i, comp in enumerate(competitors, 1):
            comp_data.append([
                str(i),
                comp.get('name', 'N/A'),
                comp.get('website', 'N/A')
            ])

        comp_table = Table(comp_data, colWidths=[10*mm, 60*mm, 85*mm])
        comp_table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9.5),
            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#212121')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
                [colors.HexColor('#e8eaf6'), colors.white]),
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#9fa8da')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(comp_table)

    # ── Footer ───────────────────────────────────────────────
    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(
        width="100%", thickness=1,
        color=colors.HexColor('#c5cae9'),
        spaceAfter=4
    ))
    story.append(Paragraph(
        "Generated by Preet Vishwakarma  |  AI Company Research Assistant",
        ParagraphStyle(
            'Footer',
            fontName='Helvetica',
            fontSize=8,
            textColor=colors.HexColor('#9e9e9e'),
            alignment=TA_CENTER,
            leading=12
        )
    ))

    doc.build(story)
    return filename