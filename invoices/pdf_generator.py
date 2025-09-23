from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from io import BytesIO


def generate_invoice_pdf(invoice, output_path):
    """Generate PDF invoice matching the design in the image"""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        alignment=TA_RIGHT,
        spaceAfter=20,
        fontName="Helvetica-Bold",
    )

    # Get user profile data for sender details
    # Use stored details from invoice (locked at creation time)
    sender_name = invoice.sender_name
    sender_address = invoice.sender_address_line_1
    sender_address2 = invoice.sender_address_line_2 or ""
    sender_town = invoice.sender_town
    sender_postcode = invoice.sender_post_code
    sender_phone = invoice.sender_phone
    sender_email = invoice.sender_email

    # Bank details (locked at creation time)
    bank_name = invoice.bank_name
    account_name = invoice.account_name
    account_number = invoice.account_number
    sort_code = invoice.sort_code

    # Header section with sender details and invoice title
    header_data = [
        [sender_name, f"INVOICE"],
        [sender_address, ""],
        [sender_address2 if sender_address2 else "", ""],
        [sender_town, ""],
        [sender_postcode, ""],
        [sender_phone, ""],
        [sender_email, ""],
    ]

    header_table = Table(header_data, colWidths=[4 * inch, 2 * inch])
    header_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (1, 0), (1, 0), 18),
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (0, 0), 12),
                ("FONTSIZE", (0, 1), (0, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.append(header_table)
    story.append(Spacer(1, 20))

    # Client and invoice details section
    client = invoice.client
    details_data = [
        ["ISSUED TO:", "INVOICE NUMBER:", invoice.invoice_number],
        [client.company_name, "Date:", invoice.issue_date.strftime("%d/%m/%Y")],
        [client.contact_person, "Due Date:", invoice.due_date.strftime("%d/%m/%Y")],
        [client.address_line_1, "Bank:", bank_name],
        [client.address_line_2 or "", "Account Name:", account_name],
        [f"{client.town}, {client.post_code}", "Account:", account_number],
        ["", "Sort Code:", sort_code],
    ]

    details_table = Table(details_data, colWidths=[3 * inch, 1.5 * inch, 1.5 * inch])
    details_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
                ("FONTNAME", (2, 0), (2, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    story.append(details_table)
    story.append(Spacer(1, 20))

    # Line items table
    line_items_data = [["DESCRIPTION", "RATE (PH)", "HOURS", "TOTAL"]]

    for item in invoice.line_items.all():
        work_log = item.work_log
        # Format date like "29th July", "30th July", etc.
        day = work_log.work_date.day
        suffix = get_day_suffix(day)
        month = work_log.work_date.strftime("%B")
        description = f"Consulting Services - {day}{suffix} {month}"

        line_items_data.append(
            [
                description,
                f"£{work_log.hourly_rate}",
                str(work_log.hours_worked),
                f"£{work_log.total_amount}",
            ]
        )

    line_items_table = Table(
        line_items_data, colWidths=[3 * inch, 1.5 * inch, 1 * inch, 1.5 * inch]
    )
    line_items_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, -1), "LEFT"),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("LINEBELOW", (0, 0), (-1, 0), 1, colors.black),
                ("LINEBELOW", (0, 1), (-1, -1), 0.5, colors.grey),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    story.append(line_items_table)
    story.append(Spacer(1, 20))

    # Total section
    total_data = [["TOTAL", f"£{invoice.total_amount}"]]

    total_table = Table(total_data, colWidths=[4 * inch, 2 * inch])
    total_table.setStyle(
        TableStyle(
            [
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("TOPPADDING", (0, 0), (-1, 0), 5),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 5),
            ]
        )
    )

    story.append(total_table)
    story.append(Spacer(1, 30))

    # Payment terms
    payment_terms = Paragraph(
        "PAYMENT DUE WITHIN 30 DAYS",
        ParagraphStyle(
            "PaymentTerms", alignment=TA_CENTER, fontSize=12, fontName="Helvetica-Bold"
        ),
    )
    story.append(payment_terms)

    doc.build(story)


def get_day_suffix(day):
    """Get the appropriate suffix for a day number (1st, 2nd, 3rd, etc.)"""
    if 10 <= day % 100 <= 20:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return suffix


def generate_invoice_pdf_response(invoice):
    """Generate PDF invoice and return as HTTP response"""
    from django.http import HttpResponse

    # Create a BytesIO buffer to store the PDF
    buffer = BytesIO()

    # Generate the PDF
    generate_invoice_pdf(invoice, buffer)

    # Get the value of the buffer
    pdf = buffer.getvalue()
    buffer.close()

    # Create the HTTP response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="invoice-{invoice.invoice_number}.pdf"'
    )
    response.write(pdf)

    return response
